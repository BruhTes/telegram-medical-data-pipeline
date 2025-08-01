"""
Telegram Scraper Service for Medical Data Collection
"""
import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import Message, Channel, User
from telethon.errors import FloodWaitError, ChannelPrivateError
from dotenv import load_dotenv

from app.core.config import settings
from app.core.channels_config import get_active_channels, get_channel_names

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/telegram_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramScraper:
    """Telegram scraper for medical channels"""
    
    def __init__(self):
        """Initialize the scraper with Telegram credentials"""
        self.api_id = settings.telegram_api_id
        self.api_hash = settings.telegram_api_hash
        self.phone = settings.telegram_phone
        self.client = None
        
        # Medical channels to scrape
        self.medical_channels = get_channel_names()
        
        # Data storage paths
        self.raw_data_path = Path("data/raw/telegram_messages")
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        
    async def connect(self):
        """Connect to Telegram"""
        try:
            self.client = TelegramClient('telegram_session', self.api_id, self.api_hash)
            await self.client.start(phone=self.phone)
            logger.info("Successfully connected to Telegram")
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            raise
            
    async def disconnect(self):
        """Disconnect from Telegram"""
        if self.client:
            await self.client.disconnect()
            logger.info("Disconnected from Telegram")
            
    def _get_channel_data_path(self, channel_name: str, date: datetime) -> Path:
        """Get the file path for storing channel data"""
        date_str = date.strftime("%Y-%m-%d")
        channel_path = self.raw_data_path / date_str / channel_name
        channel_path.mkdir(parents=True, exist_ok=True)
        return channel_path / f"{date_str}_{channel_name}.json"
        
    def _serialize_message(self, message: Message) -> Dict[str, Any]:
        """Serialize a Telegram message to JSON-serializable format"""
        try:
            # Extract media information
            media_info = None
            if message.media:
                media_info = {
                    "type": str(type(message.media).__name__),
                    "file_id": getattr(message.media, 'id', None),
                    "file_size": getattr(message.media, 'size', None),
                    "mime_type": getattr(message.media, 'mime_type', None),
                }
                
            # Extract sender information
            sender_info = None
            if message.sender_id:
                try:
                    sender = self.client.get_entity(message.sender_id)
                    sender_info = {
                        "id": sender.id,
                        "username": getattr(sender, 'username', None),
                        "first_name": getattr(sender, 'first_name', None),
                        "last_name": getattr(sender, 'last_name', None),
                    }
                except Exception as e:
                    logger.warning(f"Could not get sender info: {e}")
                    
            return {
                "id": message.id,
                "date": message.date.isoformat() if message.date else None,
                "text": message.text,
                "sender_id": message.sender_id,
                "sender_info": sender_info,
                "media": media_info,
                "views": getattr(message, 'views', None),
                "forwards": getattr(message, 'forwards', None),
                "replies": getattr(message, 'reply_to', None),
                "raw_data": str(message)  # Keep raw data for debugging
            }
        except Exception as e:
            logger.error(f"Error serializing message {message.id}: {e}")
            return {"error": str(e), "raw_data": str(message)}
            
    async def scrape_channel(self, channel_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape messages from a specific channel"""
        messages = []
        try:
            # Get the channel entity
            channel = await self.client.get_entity(f"@{channel_name}")
            logger.info(f"Scraping channel: {channel_name}")
            
            # Get messages
            async for message in self.client.iter_messages(channel, limit=limit):
                if message and message.text:  # Only process text messages for now
                    serialized_message = self._serialize_message(message)
                    serialized_message["channel_name"] = channel_name
                    serialized_message["channel_id"] = channel.id
                    messages.append(serialized_message)
                    
            logger.info(f"Scraped {len(messages)} messages from {channel_name}")
            
        except ChannelPrivateError:
            logger.warning(f"Channel {channel_name} is private or not accessible")
        except FloodWaitError as e:
            logger.warning(f"Rate limited for {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"Error scraping channel {channel_name}: {e}")
            
        return messages
        
    async def save_channel_data(self, channel_name: str, messages: List[Dict[str, Any]], date: datetime):
        """Save channel data to JSON file"""
        if not messages:
            return
            
        file_path = self._get_channel_data_path(channel_name, date)
        
        data = {
            "metadata": {
                "channel_name": channel_name,
                "scrape_date": datetime.now().isoformat(),
                "message_count": len(messages),
                "date_range": {
                    "start": min(msg.get("date") for msg in messages if msg.get("date")),
                    "end": max(msg.get("date") for msg in messages if msg.get("date"))
                }
            },
            "messages": messages
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(messages)} messages to {file_path}")
        except Exception as e:
            logger.error(f"Error saving data for {channel_name}: {e}")
            
    async def scrape_all_channels(self, limit_per_channel: int = 100):
        """Scrape all medical channels"""
        today = datetime.now()
        
        for channel_name in self.medical_channels:
            try:
                logger.info(f"Starting scrape for channel: {channel_name}")
                messages = await self.scrape_channel(channel_name, limit_per_channel)
                await self.save_channel_data(channel_name, messages, today)
                
                # Rate limiting - be respectful to Telegram
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to scrape channel {channel_name}: {e}")
                continue
                
    async def download_media(self, message: Message, channel_name: str) -> Optional[str]:
        """Download media from a message"""
        if not message.media:
            return None
            
        try:
            # Create media directory
            media_path = Path(f"data/raw/media/{channel_name}")
            media_path.mkdir(parents=True, exist_ok=True)
            
            # Download media
            file_path = await self.client.download_media(
                message.media,
                file=f"{media_path}/{message.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            logger.info(f"Downloaded media: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error downloading media from message {message.id}: {e}")
            return None

async def main():
    """Main function to run the scraper"""
    async with TelegramScraper() as scraper:
        await scraper.scrape_all_channels()

if __name__ == "__main__":
    asyncio.run(main()) 