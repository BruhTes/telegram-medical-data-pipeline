"""
Dagster assets for YOLO image detection
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from dagster import asset, AssetExecutionContext, MetadataValue, Output

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

@asset(
    description="Run YOLO image detection on scraped images",
    group_name="yolo",
    compute_kind="python",
    deps=["scraped_telegram_data"]
)
def yolo_detections(context: AssetExecutionContext) -> Output[Dict[str, Any]]:
    """Run YOLO object detection on images from Telegram channels"""
    
    context.log.info("🤖 Starting YOLO image detection...")
    
    try:
        from app.services.yolo_detector import YOLODetector
        
        # Initialize YOLO detector
        detector = YOLODetector(model_size="n", confidence_threshold=0.25)
        
        # Load model
        if not detector.load_model():
            context.log.warning("⚠️ YOLO model not available, skipping detection")
            return Output(
                value={
                    'status': 'skipped',
                    'reason': 'YOLO model not available',
                    'detection_timestamp': datetime.now().isoformat()
                },
                metadata={
                    "status": "skipped",
                    "reason": "YOLO model not available",
                    "detection_timestamp": datetime.now().isoformat()
                }
            )
        
        # Process images
        stats = detector.scan_and_process_images()
        
        # Get overall stats
        overall_stats = detector.get_processing_stats()
        
        detection_summary = {
            'total_images': stats['total_images'],
            'processed_images': stats['processed_images'],
            'failed_images': stats['failed_images'],
            'channels_processed': list(stats['channels_processed']),
            'total_detection_files': overall_stats.get('total_detection_files', 0),
            'total_detections': overall_stats.get('total_detections', 0),
            'medical_detections': overall_stats.get('medical_detections', 0),
            'avg_confidence': overall_stats.get('avg_confidence', 0.0),
            'detection_timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        context.log.info(f"✅ YOLO detection completed: {detection_summary['processed_images']}/{detection_summary['total_images']} images")
        context.log.info(f"🔍 Total detections: {detection_summary['total_detections']}, Medical: {detection_summary['medical_detections']}")
        
        return Output(
            value=detection_summary,
            metadata={
                "total_images": detection_summary['total_images'],
                "processed_images": detection_summary['processed_images'],
                "failed_images": detection_summary['failed_images'],
                "total_detection_files": detection_summary['total_detection_files'],
                "total_detections": detection_summary['total_detections'],
                "medical_detections": detection_summary['medical_detections'],
                "avg_confidence": detection_summary['avg_confidence'],
                "detection_timestamp": detection_summary['detection_timestamp'],
                "status": detection_summary['status']
            }
        )
        
    except Exception as e:
        context.log.error(f"❌ Error in YOLO detection: {e}")
        raise

@asset(
    description="YOLO detection quality check",
    group_name="yolo",
    compute_kind="python",
    deps=["yolo_detections"]
)
def yolo_quality_check(context: AssetExecutionContext) -> Output[Dict[str, Any]]:
    """Perform quality checks on YOLO detection results"""
    
    context.log.info("🔍 Performing YOLO detection quality checks...")
    
    try:
        from app.api.database import DatabaseManager
        
        db = DatabaseManager()
        
        # Check detection data
        detection_count = db.execute_query_count("SELECT COUNT(*) FROM raw.raw_image_detections")
        
        # Check for high-confidence detections
        high_confidence = db.execute_query_count("""
            SELECT COUNT(*) FROM raw.raw_image_detections,
            LATERAL jsonb_array_elements(detection_data->'detections') as detection
            WHERE (detection->>'confidence')::FLOAT >= 0.8
        """)
        
        # Check for medical detections
        medical_detections = db.execute_query_count("""
            SELECT COUNT(*) FROM raw.raw_image_detections,
            LATERAL jsonb_array_elements(detection_data->'detections') as detection
            WHERE detection->>'is_medical_related' = 'true'
        """)
        
        # Calculate quality metrics
        quality_score = 0
        if detection_count > 0:
            quality_score = (high_confidence / detection_count) * 100
        
        quality_report = {
            'total_detections': detection_count,
            'high_confidence_detections': high_confidence,
            'medical_detections': medical_detections,
            'quality_score': quality_score,
            'check_timestamp': datetime.now().isoformat(),
            'status': 'pass' if quality_score >= 70 else 'warning'
        }
        
        context.log.info(f"✅ YOLO quality check completed: Score {quality_score:.1f}%")
        
        return Output(
            value=quality_report,
            metadata={
                "total_detections": detection_count,
                "high_confidence_detections": high_confidence,
                "medical_detections": medical_detections,
                "quality_score": quality_score,
                "status": quality_report['status'],
                "check_timestamp": quality_report['check_timestamp']
            }
        )
        
    except Exception as e:
        context.log.error(f"❌ Error in YOLO quality check: {e}")
        raise

@asset(
    description="YOLO detection analysis",
    group_name="yolo",
    compute_kind="python",
    deps=["yolo_detections", "loaded_detection_data"]
)
def yolo_analysis(context: AssetExecutionContext) -> Output[Dict[str, Any]]:
    """Analyze YOLO detection results and generate insights"""
    
    context.log.info("📊 Analyzing YOLO detection results...")
    
    try:
        from app.api.database import DatabaseManager
        
        db = DatabaseManager()
        
        # Get detection statistics
        total_detections = db.execute_query_count("SELECT COUNT(*) FROM marts.fct_image_detections")
        
        # Get top detected objects
        top_objects = db.execute_query("""
            SELECT detected_object_class, COUNT(*) as count
            FROM marts.fct_image_detections
            GROUP BY detected_object_class
            ORDER BY count DESC
            LIMIT 10
        """)
        
        # Get medical object statistics
        medical_stats = db.execute_query("""
            SELECT 
                COUNT(*) as total_medical,
                COUNT(CASE WHEN confidence_score >= 0.8 THEN 1 END) as high_confidence_medical,
                AVG(confidence_score) as avg_confidence
            FROM marts.fct_image_detections
            WHERE is_medical_related = TRUE
        """)
        
        # Get channel-wise detection stats
        channel_stats = db.execute_query("""
            SELECT 
                channel_name,
                COUNT(*) as detections,
                COUNT(CASE WHEN is_medical_related THEN 1 END) as medical_detections,
                AVG(confidence_score) as avg_confidence
            FROM marts.fct_image_detections
            GROUP BY channel_name
            ORDER BY detections DESC
        """)
        
        analysis_summary = {
            'total_detections': total_detections,
            'top_detected_objects': [dict(obj) for obj in top_objects],
            'medical_statistics': dict(medical_stats[0]) if medical_stats else {},
            'channel_statistics': [dict(stat) for stat in channel_stats],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        context.log.info(f"✅ YOLO analysis completed: {total_detections} total detections")
        
        return Output(
            value=analysis_summary,
            metadata={
                "total_detections": total_detections,
                "top_objects_count": len(top_objects),
                "medical_detections": medical_stats[0]['total_medical'] if medical_stats else 0,
                "channels_analyzed": len(channel_stats),
                "analysis_timestamp": analysis_summary['analysis_timestamp']
            }
        )
        
    except Exception as e:
        context.log.error(f"❌ Error in YOLO analysis: {e}")
        raise

# Export assets
yolo_assets = [
    yolo_detections,
    yolo_quality_check,
    yolo_analysis
] 