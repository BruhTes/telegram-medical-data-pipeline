"""
Dagster assets for Telegram data scraping and loading
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from dagster import asset, AssetExecutionContext, MetadataValue, Output
import pandas as pd

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.telegram_scraper import TelegramScraper
from app.services.data_loader import DataLoader
from app.core.channels_config import TELEGRAM_CHANNELS
from app.core.logging_config import setup_logger

logger = setup_logger(__name__)

@asset(
    description="Scrape data from Telegram channels",
    group_name="telegram",
    compute_kind="python"
)
def scraped_telegram_data(context: AssetExecutionContext) -> Output[Dict[str, Any]]:
    """Scrape data from configured Telegram channels"""
    
    context.log.info("🚀 Starting Telegram data scraping...")
    
    try:
        # Initialize scraper
        scraper = TelegramScraper()
        
        # Get active channels
        active_channels = [channel for channel in TELEGRAM_CHANNELS if channel.get('active', True)]
        context.log.info(f"📊 Found {len(active_channels)} active channels")
        
        # Scrape each channel
        results = {}
        total_messages = 0
        total_media = 0
        
        for channel in active_channels:
            channel_name = channel['name']
            channel_url = channel['url']
            
            context.log.info(f"📡 Scraping channel: {channel_name}")
            
            try:
                # Scrape channel
                channel_data = scraper.scrape_channel(
                    channel_url=channel_url,
                    channel_name=channel_name,
                    limit=100  # Limit for testing
                )
                
                if channel_data:
                    results[channel_name] = {
                        'messages_count': len(channel_data.get('messages', [])),
                        'media_count': len([m for m in channel_data.get('messages', []) if m.get('local_media_path')]),
                        'scrape_time': datetime.now().isoformat(),
                        'status': 'success'
                    }
                    
                    total_messages += results[channel_name]['messages_count']
                    total_media += results[channel_name]['media_count']
                else:
                    results[channel_name] = {
                        'messages_count': 0,
                        'media_count': 0,
                        'scrape_time': datetime.now().isoformat(),
                        'status': 'no_data'
                    }
                    
            except Exception as e:
                context.log.error(f"❌ Error scraping {channel_name}: {e}")
                results[channel_name] = {
                    'messages_count': 0,
                    'media_count': 0,
                    'scrape_time': datetime.now().isoformat(),
                    'status': 'error',
                    'error': str(e)
                }
        
        # Create summary
        summary = {
            'total_channels': len(active_channels),
            'successful_channels': len([r for r in results.values() if r['status'] == 'success']),
            'total_messages': total_messages,
            'total_media': total_media,
            'scrape_timestamp': datetime.now().isoformat(),
            'channel_results': results
        }
        
        context.log.info(f"✅ Scraping completed: {summary['successful_channels']}/{summary['total_channels']} channels")
        context.log.info(f"📊 Total messages: {total_messages}, Total media: {total_media}")
        
        return Output(
            value=summary,
            metadata={
                "total_channels": summary['total_channels'],
                "successful_channels": summary['successful_channels'],
                "total_messages": total_messages,
                "total_media": total_media,
                "scrape_timestamp": summary['scrape_timestamp'],
                "channel_results": MetadataValue.json(results)
            }
        )
        
    except Exception as e:
        context.log.error(f"❌ Fatal error in scraping: {e}")
        raise

@asset(
    description="Load scraped data into PostgreSQL",
    group_name="telegram",
    compute_kind="python",
    deps=["scraped_telegram_data"]
)
def loaded_raw_data(context: AssetExecutionContext) -> Output[Dict[str, Any]]:
    """Load scraped Telegram data into PostgreSQL raw schema"""
    
    context.log.info("🗄️ Starting data loading into PostgreSQL...")
    
    try:
        # Initialize data loader
        loader = DataLoader()
        
        # Load raw data
        load_stats = loader.load_all_raw_data()
        
        context.log.info(f"✅ Data loading completed: {load_stats['loaded_files']}/{load_stats['total_files']} files")
        
        # Get database stats
        db_stats = loader.get_raw_data_stats()
        
        summary = {
            'load_timestamp': datetime.now().isoformat(),
            'load_stats': load_stats,
            'database_stats': db_stats
        }
        
        return Output(
            value=summary,
            metadata={
                "loaded_files": load_stats['loaded_files'],
                "total_files": load_stats['total_files'],
                "failed_files": load_stats['failed_files'],
                "channels_loaded": len(load_stats['channels']),
                "total_records": db_stats.get('total_records', 0),
                "load_timestamp": summary['load_timestamp']
            }
        )
        
    except Exception as e:
        context.log.error(f"❌ Error loading data: {e}")
        raise

@asset(
    description="Load YOLO detection results into PostgreSQL",
    group_name="telegram",
    compute_kind="python",
    deps=["scraped_telegram_data"]
)
def loaded_detection_data(context: AssetExecutionContext) -> Output[Dict[str, Any]]:
    """Load YOLO detection results into PostgreSQL"""
    
    context.log.info("🔍 Loading YOLO detection results...")
    
    try:
        from scripts.load_detections import DetectionLoader
        
        # Initialize detection loader
        loader = DetectionLoader()
        
        # Load detection data
        load_stats = loader.load_all_detections()
        
        context.log.info(f"✅ Detection loading completed: {load_stats['loaded_files']}/{load_stats['total_files']} files")
        
        # Get database stats
        db_stats = loader.get_detection_stats()
        
        summary = {
            'load_timestamp': datetime.now().isoformat(),
            'load_stats': load_stats,
            'database_stats': db_stats
        }
        
        return Output(
            value=summary,
            metadata={
                "loaded_files": load_stats['loaded_files'],
                "total_files": load_stats['total_files'],
                "failed_files": load_stats['failed_files'],
                "channels_with_detections": len(load_stats['channels']),
                "total_detection_records": db_stats.get('total_records', 0),
                "total_object_detections": db_stats.get('detection_stats', {}).get('total_detections', 0),
                "medical_detections": db_stats.get('medical_stats', {}).get('medical_detections', 0),
                "load_timestamp": summary['load_timestamp']
            }
        )
        
    except Exception as e:
        context.log.error(f"❌ Error loading detection data: {e}")
        raise

@asset(
    description="Telegram data quality check",
    group_name="telegram",
    compute_kind="python",
    deps=["loaded_raw_data"]
)
def telegram_data_quality_check(context: AssetExecutionContext) -> Output[Dict[str, Any]]:
    """Perform data quality checks on loaded Telegram data"""
    
    context.log.info("🔍 Performing data quality checks...")
    
    try:
        from app.api.database import DatabaseManager
        
        db = DatabaseManager()
        
        # Check raw data
        raw_count = db.execute_query_count("SELECT COUNT(*) FROM raw.raw_telegram_data")
        
        # Check for empty messages
        empty_messages = db.execute_query_count("""
            SELECT COUNT(*) FROM raw.raw_telegram_data 
            WHERE data_json->>'messages' IS NULL OR jsonb_array_length(data_json->'messages') = 0
        """)
        
        # Check for recent data
        recent_data = db.execute_query_count("""
            SELECT COUNT(*) FROM raw.raw_telegram_data 
            WHERE loaded_at >= CURRENT_DATE - INTERVAL '1 day'
        """)
        
        # Calculate quality metrics
        quality_score = 0
        if raw_count > 0:
            quality_score = ((raw_count - empty_messages) / raw_count) * 100
        
        quality_report = {
            'total_raw_records': raw_count,
            'empty_message_files': empty_messages,
            'recent_data_files': recent_data,
            'quality_score': quality_score,
            'check_timestamp': datetime.now().isoformat(),
            'status': 'pass' if quality_score >= 80 else 'warning'
        }
        
        context.log.info(f"✅ Quality check completed: Score {quality_score:.1f}%")
        
        return Output(
            value=quality_report,
            metadata={
                "total_raw_records": raw_count,
                "empty_message_files": empty_messages,
                "recent_data_files": recent_data,
                "quality_score": quality_score,
                "status": quality_report['status'],
                "check_timestamp": quality_report['check_timestamp']
            }
        )
        
    except Exception as e:
        context.log.error(f"❌ Error in quality check: {e}")
        raise

# Export assets
telegram_assets = [
    scraped_telegram_data,
    loaded_raw_data,
    loaded_detection_data,
    telegram_data_quality_check
] 