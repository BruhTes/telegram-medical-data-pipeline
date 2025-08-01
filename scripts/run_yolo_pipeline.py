#!/usr/bin/env python3
"""
Complete YOLO Detection Pipeline for Telegram Medical Data
"""
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.yolo_detector import YOLODetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_yolo_detection(channel_name: str = None, model_size: str = "n", confidence: float = 0.25):
    """Run YOLO detection on images"""
    print("🤖 Starting YOLO Image Detection...")
    
    # Initialize detector
    detector = YOLODetector(
        model_size=model_size,
        confidence_threshold=confidence
    )
    
    # Load model
    if not detector.load_model():
        print("❌ Failed to load YOLO model")
        print("💡 Please install ultralytics: pip install ultralytics")
        return False
    
    # Process images
    stats = detector.scan_and_process_images(channel_name)
    
    print(f"\n📊 Detection Statistics:")
    print(f"  Total images found: {stats['total_images']}")
    print(f"  Successfully processed: {stats['processed_images']}")
    print(f"  Failed: {stats['failed_images']}")
    print(f"  Channels processed: {list(stats['channels_processed'])}")
    
    # Get overall stats
    overall_stats = detector.get_processing_stats()
    if overall_stats:
        print(f"\n📊 Overall Statistics:")
        print(f"  Total detection files: {overall_stats['total_detection_files']}")
        print(f"  Channels with detections: {list(overall_stats['channels_with_detections'])}")
        print(f"  Total detections: {overall_stats['total_detections']}")
        print(f"  Medical detections: {overall_stats['medical_detections']}")
        print(f"  Average confidence: {overall_stats['avg_confidence']:.3f}")
    
    return True

def run_detection_loading():
    """Load detection results into database"""
    print("\n🗄️ Loading detection results into PostgreSQL...")
    
    try:
        from scripts.load_detections import DetectionLoader
        
        loader = DetectionLoader()
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
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading detections: {e}")
        return False

def run_dbt_models():
    """Run dbt models for image detections"""
    print("\n🔄 Running dbt models for image detections...")
    
    try:
        from scripts.run_dbt import DbtRunner
        
        runner = DbtRunner()
        
        # Run the image detections model
        success = runner.run("fct_image_detections")
        
        if success:
            print("✅ dbt models completed successfully")
            return True
        else:
            print("❌ dbt models failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running dbt models: {e}")
        return False

def main():
    """Main function to run the complete YOLO pipeline"""
    parser = argparse.ArgumentParser(description="YOLO Detection Pipeline for Telegram Medical Data")
    parser.add_argument(
        "--channel",
        help="Specific channel to process (optional)"
    )
    parser.add_argument(
        "--model-size",
        choices=['n', 's', 'm', 'l', 'x'],
        default='n',
        help="YOLO model size (default: n)"
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.25,
        help="Confidence threshold (default: 0.25)"
    )
    parser.add_argument(
        "--skip-detection",
        action="store_true",
        help="Skip YOLO detection (only load existing results)"
    )
    parser.add_argument(
        "--skip-loading",
        action="store_true",
        help="Skip loading detections to database"
    )
    parser.add_argument(
        "--skip-dbt",
        action="store_true",
        help="Skip dbt model execution"
    )
    parser.add_argument(
        "--detection-only",
        action="store_true",
        help="Only run YOLO detection"
    )
    parser.add_argument(
        "--loading-only",
        action="store_true",
        help="Only load detection results to database"
    )
    parser.add_argument(
        "--dbt-only",
        action="store_true",
        help="Only run dbt models"
    )
    
    args = parser.parse_args()
    
    print("🚀 Starting YOLO Detection Pipeline...")
    print(f"  Model size: {args.model_size}")
    print(f"  Confidence threshold: {args.confidence}")
    if args.channel:
        print(f"  Target channel: {args.channel}")
    
    # Determine which steps to run
    run_detection = not args.skip_detection and not args.loading_only and not args.dbt_only
    run_loading = not args.skip_loading and not args.detection_only and not args.dbt_only
    run_dbt = not args.skip_dbt and not args.detection_only and not args.loading_only
    
    success = True
    
    # Step 1: YOLO Detection
    if run_detection:
        print("\n" + "="*50)
        print("STEP 1: YOLO Image Detection")
        print("="*50)
        success = run_yolo_detection(args.channel, args.model_size, args.confidence)
        if not success:
            print("❌ YOLO detection failed")
            return
    
    # Step 2: Load Detection Results
    if run_loading and success:
        print("\n" + "="*50)
        print("STEP 2: Load Detection Results")
        print("="*50)
        success = run_detection_loading()
        if not success:
            print("❌ Detection loading failed")
            return
    
    # Step 3: Run dbt Models
    if run_dbt and success:
        print("\n" + "="*50)
        print("STEP 3: dbt Model Execution")
        print("="*50)
        success = run_dbt_models()
        if not success:
            print("❌ dbt model execution failed")
            return
    
    if success:
        print("\n" + "="*50)
        print("🎉 YOLO Detection Pipeline Completed Successfully!")
        print("="*50)
        print("\n📊 Next Steps:")
        print("  1. Check the enriched data in data/enriched/detections/")
        print("  2. View detection results in PostgreSQL: raw.raw_image_detections")
        print("  3. Query the fact table: marts.fct_image_detections")
        print("  4. Run analytics queries on the enriched data")
    else:
        print("\n❌ Pipeline failed")

if __name__ == "__main__":
    main() 