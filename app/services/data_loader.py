"""
Data Loader Service for Populating Data Lake
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_loader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataLoader:
    """Data loader for populating PostgreSQL data lake"""
    
    def __init__(self):
        """Initialize the data loader"""
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.raw_data_path = Path("data/raw/telegram_messages")
        
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(
            host=settings.database_url.split('@')[1].split(':')[0],
            database=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password
        )
        
    def load_raw_messages(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load raw messages from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            messages = data.get('messages', [])
            logger.info(f"Loaded {len(messages)} messages from {file_path}")
            return messages
            
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            return []
            
    def insert_raw_message(self, conn, message_data: Dict[str, Any]) -> int:
        """Insert a raw message into the database"""
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO raw_telegram_messages (
                        message_id, chat_id, chat_title, sender_id, sender_username,
                        message_text, message_date, has_media, media_type, media_url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    message_data.get('id'),
                    message_data.get('channel_id'),
                    message_data.get('channel_name'),
                    message_data.get('sender_id'),
                    message_data.get('sender_info', {}).get('username') if message_data.get('sender_info') else None,
                    message_data.get('text'),
                    message_data.get('date'),
                    bool(message_data.get('media')),
                    message_data.get('media', {}).get('type') if message_data.get('media') else None,
                    None  # media_url will be populated later
                ))
                
                message_id = cursor.fetchone()[0]
                conn.commit()
                return message_id
                
        except Exception as e:
            logger.error(f"Error inserting message {message_data.get('id')}: {e}")
            conn.rollback()
            return None
            
    def insert_raw_media(self, conn, media_data: Dict[str, Any], message_id: int) -> int:
        """Insert raw media information into the database"""
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO raw_telegram_media (
                        message_id, file_id, file_unique_id, file_size, 
                        file_path, mime_type, local_path
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    message_id,
                    media_data.get('file_id'),
                    None,  # file_unique_id
                    media_data.get('file_size'),
                    None,  # file_path
                    media_data.get('mime_type'),
                    None   # local_path
                ))
                
                media_id = cursor.fetchone()[0]
                conn.commit()
                return media_id
                
        except Exception as e:
            logger.error(f"Error inserting media for message {message_id}: {e}")
            conn.rollback()
            return None
            
    def process_channel_data(self, channel_path: Path) -> int:
        """Process all data files for a channel"""
        processed_count = 0
        
        try:
            conn = self._get_connection()
            
            # Process each JSON file in the channel directory
            for json_file in channel_path.glob("*.json"):
                logger.info(f"Processing file: {json_file}")
                
                messages = self.load_raw_messages(json_file)
                
                for message_data in messages:
                    # Insert raw message
                    message_id = self.insert_raw_message(conn, message_data)
                    
                    if message_id and message_data.get('media'):
                        # Insert media information
                        self.insert_raw_media(conn, message_data['media'], message_id)
                        
                    processed_count += 1
                    
            conn.close()
            logger.info(f"Processed {processed_count} messages from {channel_path}")
            
        except Exception as e:
            logger.error(f"Error processing channel data {channel_path}: {e}")
            
        return processed_count
        
    def load_all_raw_data(self) -> Dict[str, int]:
        """Load all raw data from the data lake into PostgreSQL"""
        stats = {}
        
        try:
            # Process each date directory
            for date_dir in self.raw_data_path.iterdir():
                if date_dir.is_dir():
                    date_str = date_dir.name
                    logger.info(f"Processing date: {date_str}")
                    
                    # Process each channel directory
                    for channel_dir in date_dir.iterdir():
                        if channel_dir.is_dir():
                            channel_name = channel_dir.name
                            logger.info(f"Processing channel: {channel_name}")
                            
                            processed_count = self.process_channel_data(channel_dir)
                            stats[f"{date_str}_{channel_name}"] = processed_count
                            
        except Exception as e:
            logger.error(f"Error loading raw data: {e}")
            
        return stats
        
    def get_loading_stats(self) -> Dict[str, Any]:
        """Get statistics about the data loading process"""
        try:
            conn = self._get_connection()
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Count raw messages
                cursor.execute("SELECT COUNT(*) as count FROM raw_telegram_messages")
                message_count = cursor.fetchone()['count']
                
                # Count raw media
                cursor.execute("SELECT COUNT(*) as count FROM raw_telegram_media")
                media_count = cursor.fetchone()['count']
                
                # Count unique channels
                cursor.execute("SELECT COUNT(DISTINCT chat_title) as count FROM raw_telegram_messages")
                channel_count = cursor.fetchone()['count']
                
                # Get date range
                cursor.execute("""
                    SELECT 
                        MIN(message_date) as earliest_date,
                        MAX(message_date) as latest_date
                    FROM raw_telegram_messages
                """)
                date_range = cursor.fetchone()
                
            conn.close()
            
            return {
                "total_messages": message_count,
                "total_media": media_count,
                "unique_channels": channel_count,
                "date_range": {
                    "earliest": date_range['earliest_date'].isoformat() if date_range['earliest_date'] else None,
                    "latest": date_range['latest_date'].isoformat() if date_range['latest_date'] else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting loading stats: {e}")
            return {}
            
    def create_data_lake_indexes(self):
        """Create indexes for better query performance"""
        try:
            conn = self._get_connection()
            
            with conn.cursor() as cursor:
                # Create indexes if they don't exist
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_raw_messages_chat_id ON raw_telegram_messages(chat_id)",
                    "CREATE INDEX IF NOT EXISTS idx_raw_messages_date ON raw_telegram_messages(message_date)",
                    "CREATE INDEX IF NOT EXISTS idx_raw_messages_sender ON raw_telegram_messages(sender_id)",
                    "CREATE INDEX IF NOT EXISTS idx_raw_media_message_id ON raw_telegram_media(message_id)"
                ]
                
                for index_sql in indexes:
                    cursor.execute(index_sql)
                    
            conn.commit()
            conn.close()
            logger.info("Created data lake indexes")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

def main():
    """Main function to run the data loader"""
    loader = DataLoader()
    
    # Load all raw data
    stats = loader.load_all_raw_data()
    logger.info(f"Loading stats: {stats}")
    
    # Create indexes
    loader.create_data_lake_indexes()
    
    # Get final stats
    final_stats = loader.get_loading_stats()
    logger.info(f"Final stats: {final_stats}")

if __name__ == "__main__":
    main() 