#!/usr/bin/env python3
"""
Script to load raw JSON files from data lake into PostgreSQL raw schema
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RawDataLoader:
    """Load raw JSON data into PostgreSQL raw schema"""
    
    def __init__(self):
        """Initialize the raw data loader"""
        self.raw_data_path = Path("data/raw/telegram_messages")
        self.connection_params = {
            'host': 'localhost',
            'database': 'telegram_medical',
            'user': 'postgres',
            'password': 'password',
            'port': 5432
        }
        
    def create_raw_schema(self):
        """Create raw schema and tables"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            conn.autocommit = True
            
            with conn.cursor() as cursor:
                # Create raw schema
                cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
                
                # Create raw_telegram_data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS raw.raw_telegram_data (
                        id SERIAL PRIMARY KEY,
                        file_path TEXT NOT NULL,
                        channel_name TEXT,
                        scrape_date DATE,
                        data_json JSONB NOT NULL,
                        loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create index on JSONB for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_raw_telegram_data_json 
                    ON raw.raw_telegram_data USING GIN (data_json);
                """)
                
                # Create index on channel_name for filtering
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_raw_telegram_data_channel 
                    ON raw.raw_telegram_data (channel_name);
                """)
                
            conn.close()
            logger.info("✅ Raw schema and tables created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating raw schema: {e}")
            raise
            
    def load_json_file(self, file_path: Path) -> bool:
        """Load a single JSON file into the raw schema"""
        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract metadata
            metadata = data.get('metadata', {})
            channel_name = metadata.get('channel_name')
            scrape_date_str = metadata.get('scrape_date')
            
            # Parse scrape date
            scrape_date = None
            if scrape_date_str:
                try:
                    scrape_date = datetime.fromisoformat(scrape_date_str.replace('Z', '+00:00')).date()
                except:
                    pass
                    
            # Connect to database
            conn = psycopg2.connect(**self.connection_params)
            
            with conn.cursor() as cursor:
                # Check if file already loaded
                cursor.execute("""
                    SELECT id FROM raw.raw_telegram_data 
                    WHERE file_path = %s
                """, (str(file_path),))
                
                if cursor.fetchone():
                    logger.info(f"⏭️ File already loaded: {file_path}")
                    conn.close()
                    return True
                    
                # Insert data
                cursor.execute("""
                    INSERT INTO raw.raw_telegram_data 
                    (file_path, channel_name, scrape_date, data_json)
                    VALUES (%s, %s, %s, %s)
                """, (
                    str(file_path),
                    channel_name,
                    scrape_date,
                    json.dumps(data)
                ))
                
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Loaded: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading {file_path}: {e}")
            return False
            
    def load_all_raw_data(self) -> Dict[str, int]:
        """Load all raw JSON files from the data lake"""
        stats = {
            'total_files': 0,
            'loaded_files': 0,
            'failed_files': 0,
            'channels': {}
        }
        
        try:
            # Create raw schema first
            self.create_raw_schema()
            
            # Find all JSON files
            json_files = list(self.raw_data_path.rglob("*.json"))
            stats['total_files'] = len(json_files)
            
            logger.info(f"Found {len(json_files)} JSON files to load")
            
            for file_path in json_files:
                if self.load_json_file(file_path):
                    stats['loaded_files'] += 1
                    
                    # Track channel stats
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            channel_name = data.get('metadata', {}).get('channel_name', 'unknown')
                            if channel_name not in stats['channels']:
                                stats['channels'][channel_name] = 0
                            stats['channels'][channel_name] += 1
                    except:
                        pass
                else:
                    stats['failed_files'] += 1
                    
            logger.info(f"📊 Loading complete: {stats['loaded_files']}/{stats['total_files']} files loaded")
            logger.info(f"📊 Channels loaded: {list(stats['channels'].keys())}")
            
        except Exception as e:
            logger.error(f"❌ Error in load_all_raw_data: {e}")
            
        return stats
        
    def get_raw_data_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded raw data"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Count total records
                cursor.execute("SELECT COUNT(*) as count FROM raw.raw_telegram_data")
                total_records = cursor.fetchone()['count']
                
                # Count by channel
                cursor.execute("""
                    SELECT channel_name, COUNT(*) as count 
                    FROM raw.raw_telegram_data 
                    WHERE channel_name IS NOT NULL 
                    GROUP BY channel_name 
                    ORDER BY count DESC
                """)
                channel_stats = cursor.fetchall()
                
                # Date range
                cursor.execute("""
                    SELECT 
                        MIN(scrape_date) as earliest_date,
                        MAX(scrape_date) as latest_date
                    FROM raw.raw_telegram_data 
                    WHERE scrape_date IS NOT NULL
                """)
                date_range = cursor.fetchone()
                
            conn.close()
            
            return {
                'total_records': total_records,
                'channel_stats': channel_stats,
                'date_range': date_range
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting raw data stats: {e}")
            return {}

def main():
    """Main function to load raw data"""
    print("🗄️ Loading raw JSON data into PostgreSQL...")
    
    loader = RawDataLoader()
    
    # Load all raw data
    stats = loader.load_all_raw_data()
    
    print(f"\n📊 Loading Statistics:")
    print(f"  Total files found: {stats['total_files']}")
    print(f"  Successfully loaded: {stats['loaded_files']}")
    print(f"  Failed: {stats['failed_files']}")
    
    if stats['channels']:
        print(f"  Channels loaded: {list(stats['channels'].keys())}")
    
    # Get database stats
    db_stats = loader.get_raw_data_stats()
    if db_stats:
        print(f"\n📊 Database Statistics:")
        print(f"  Total records: {db_stats['total_records']}")
        if db_stats['channel_stats']:
            print(f"  Records by channel:")
            for channel in db_stats['channel_stats']:
                print(f"    {channel['channel_name']}: {channel['count']}")
    
    print("\n✅ Raw data loading completed!")
    print("Next step: Run dbt models to transform the data")

if __name__ == "__main__":
    main() 