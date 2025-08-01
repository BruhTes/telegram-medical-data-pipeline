#!/usr/bin/env python3
"""
Script to load YOLO detection results into PostgreSQL
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetectionLoader:
    """Load YOLO detection results into PostgreSQL"""
    
    def __init__(self):
        """Initialize the detection loader"""
        self.detections_path = Path("data/enriched/detections")
        self.connection_params = {
            'host': 'localhost',
            'database': 'telegram_medical',
            'user': 'postgres',
            'password': 'password',
            'port': 5432
        }
        
    def create_detections_schema(self):
        """Create raw schema and detection table"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            conn.autocommit = True
            
            with conn.cursor() as cursor:
                # Create raw schema if not exists
                cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
                
                # Create raw_image_detections table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS raw.raw_image_detections (
                        id SERIAL PRIMARY KEY,
                        file_path TEXT NOT NULL,
                        file_name TEXT NOT NULL,
                        channel_name TEXT,
                        detection_data JSONB NOT NULL,
                        loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create indexes for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_raw_image_detections_json 
                    ON raw.raw_image_detections USING GIN (detection_data);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_raw_image_detections_channel 
                    ON raw.raw_image_detections (channel_name);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_raw_image_detections_file 
                    ON raw.raw_image_detections (file_name);
                """)
                
            conn.close()
            logger.info("✅ Raw image detections schema and tables created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating detections schema: {e}")
            raise
            
    def load_detection_file(self, file_path: Path) -> bool:
        """Load a single detection file into the database"""
        try:
            # Read detection file
            with open(file_path, 'r', encoding='utf-8') as f:
                detection_data = json.load(f)
                
            # Extract metadata
            image_path = detection_data.get('metadata', {}).get('image_path', '')
            image_name = Path(image_path).name if image_path else file_path.stem
            
            # Extract channel name from image path
            channel_name = None
            if image_path:
                path_parts = Path(image_path).parts
                if 'media' in path_parts:
                    media_index = path_parts.index('media')
                    if media_index + 1 < len(path_parts):
                        channel_name = path_parts[media_index + 1]
                        
            # Connect to database
            conn = psycopg2.connect(**self.connection_params)
            
            with conn.cursor() as cursor:
                # Check if file already loaded
                cursor.execute("""
                    SELECT id FROM raw.raw_image_detections 
                    WHERE file_path = %s
                """, (str(file_path),))
                
                if cursor.fetchone():
                    logger.info(f"⏭️ Detection file already loaded: {file_path}")
                    conn.close()
                    return True
                    
                # Insert detection data
                cursor.execute("""
                    INSERT INTO raw.raw_image_detections 
                    (file_path, file_name, channel_name, detection_data)
                    VALUES (%s, %s, %s, %s)
                """, (
                    str(file_path),
                    image_name,
                    channel_name,
                    json.dumps(detection_data)
                ))
                
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Loaded detection: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading detection {file_path}: {e}")
            return False
            
    def load_all_detections(self) -> Dict[str, int]:
        """Load all detection files from the enriched directory"""
        stats = {
            'total_files': 0,
            'loaded_files': 0,
            'failed_files': 0,
            'channels': {}
        }
        
        try:
            # Create schema first
            self.create_detections_schema()
            
            # Find all detection JSON files
            detection_files = list(self.detections_path.glob("*_detections.json"))
            stats['total_files'] = len(detection_files)
            
            logger.info(f"Found {len(detection_files)} detection files to load")
            
            for file_path in detection_files:
                if self.load_detection_file(file_path):
                    stats['loaded_files'] += 1
                    
                    # Track channel stats
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            image_path = data.get('metadata', {}).get('image_path', '')
                            if image_path:
                                path_parts = Path(image_path).parts
                                if 'media' in path_parts:
                                    media_index = path_parts.index('media')
                                    if media_index + 1 < len(path_parts):
                                        channel_name = path_parts[media_index + 1]
                                        if channel_name not in stats['channels']:
                                            stats['channels'][channel_name] = 0
                                        stats['channels'][channel_name] += 1
                    except:
                        pass
                else:
                    stats['failed_files'] += 1
                    
            logger.info(f"📊 Loading complete: {stats['loaded_files']}/{stats['total_files']} files loaded")
            logger.info(f"📊 Channels with detections: {list(stats['channels'].keys())}")
            
        except Exception as e:
            logger.error(f"❌ Error in load_all_detections: {e}")
            
        return stats
        
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded detection data"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Count total records
                cursor.execute("SELECT COUNT(*) as count FROM raw.raw_image_detections")
                total_records = cursor.fetchone()['count']
                
                # Count by channel
                cursor.execute("""
                    SELECT channel_name, COUNT(*) as count 
                    FROM raw.raw_image_detections 
                    WHERE channel_name IS NOT NULL 
                    GROUP BY channel_name 
                    ORDER BY count DESC
                """)
                channel_stats = cursor.fetchall()
                
                # Count total detections across all files
                cursor.execute("""
                    SELECT 
                        SUM(jsonb_array_length(detection_data->'detections')) as total_detections,
                        COUNT(*) as files_with_detections
                    FROM raw.raw_image_detections 
                    WHERE detection_data->'detections' IS NOT NULL
                """)
                detection_stats = cursor.fetchone()
                
                # Count medical detections
                cursor.execute("""
                    SELECT COUNT(*) as medical_detections
                    FROM raw.raw_image_detections,
                    LATERAL jsonb_array_elements(detection_data->'detections') as detection
                    WHERE detection->>'is_medical_related' = 'true'
                """)
                medical_stats = cursor.fetchone()
                
            conn.close()
            
            return {
                'total_records': total_records,
                'channel_stats': channel_stats,
                'detection_stats': detection_stats,
                'medical_stats': medical_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting detection stats: {e}")
            return {}

def main():
    """Main function to load detection data"""
    print("🔍 Loading YOLO detection results into PostgreSQL...")
    
    loader = DetectionLoader()
    
    # Load all detection data
    stats = loader.load_all_detections()
    
    print(f"\n📊 Loading Statistics:")
    print(f"  Total detection files found: {stats['total_files']}")
    print(f"  Successfully loaded: {stats['loaded_files']}")
    print(f"  Failed: {stats['failed_files']}")
    
    if stats['channels']:
        print(f"  Channels with detections: {list(stats['channels'].keys())}")
    
    # Get database stats
    db_stats = loader.get_detection_stats()
    if db_stats:
        print(f"\n📊 Database Statistics:")
        print(f"  Total detection records: {db_stats['total_records']}")
        
        if db_stats['detection_stats']:
            print(f"  Total object detections: {db_stats['detection_stats']['total_detections']}")
            print(f"  Files with detections: {db_stats['detection_stats']['files_with_detections']}")
        
        if db_stats['medical_stats']:
            print(f"  Medical object detections: {db_stats['medical_stats']['medical_detections']}")
        
        if db_stats['channel_stats']:
            print(f"  Detections by channel:")
            for channel in db_stats['channel_stats']:
                print(f"    {channel['channel_name']}: {channel['count']}")
    
    print("\n✅ Detection data loading completed!")
    print("Next step: Run dbt models to transform the detection data")

if __name__ == "__main__":
    main() 