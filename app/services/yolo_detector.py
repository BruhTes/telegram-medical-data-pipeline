"""
YOLO Image Detection Service for Telegram Medical Data Pipeline
"""
import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YOLODetector:
    """YOLO-based image detection service"""
    
    def __init__(self, model_size: str = "n", confidence_threshold: float = 0.25):
        """
        Initialize YOLO detector
        
        Args:
            model_size: Model size ('n', 's', 'm', 'l', 'x')
            confidence_threshold: Minimum confidence score for detections
        """
        self.model_size = model_size
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.media_path = Path("data/raw/media")
        self.detections_path = Path("data/enriched/detections")
        self.detections_path.mkdir(parents=True, exist_ok=True)
        
        # Medical-related object classes (COCO dataset)
        self.medical_objects = {
            'person', 'bottle', 'cup', 'bowl', 'chair', 'couch', 'bed', 'dining table',
            'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'book',
            'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        }
        
        # Medical-specific keywords for filtering
        self.medical_keywords = {
            'medicine', 'pill', 'tablet', 'capsule', 'syrup', 'injection', 'cream',
            'ointment', 'bandage', 'syringe', 'thermometer', 'stethoscope', 'mask',
            'gloves', 'hospital', 'clinic', 'pharmacy', 'medical', 'health'
        }
        
    def load_model(self):
        """Load YOLO model"""
        try:
            # Import ultralytics (will fail if not installed)
            from ultralytics import YOLO
            
            # Load pre-trained model
            model_name = f"yolov8{self.model_size}.pt"
            self.model = YOLO(model_name)
            logger.info(f"✅ YOLO model loaded: {model_name}")
            return True
            
        except ImportError:
            logger.error("❌ ultralytics not installed. Please run: pip install ultralytics")
            return False
        except Exception as e:
            logger.error(f"❌ Error loading YOLO model: {e}")
            return False
    
    def detect_objects(self, image_path: Path) -> List[Dict[str, Any]]:
        """
        Detect objects in an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of detected objects with metadata
        """
        if not self.model:
            logger.error("❌ YOLO model not loaded")
            return []
        
        try:
            # Run inference
            results = self.model(image_path, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get detection data
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = result.names[class_id]
                        
                        detection = {
                            'class_id': class_id,
                            'class_name': class_name,
                            'confidence': confidence,
                            'bbox': {
                                'x1': float(x1),
                                'y1': float(y1),
                                'x2': float(x2),
                                'y2': float(y2)
                            },
                            'area': float((x2 - x1) * (y2 - y1)),
                            'is_medical_related': class_name in self.medical_objects,
                            'detection_time': datetime.now().isoformat()
                        }
                        
                        detections.append(detection)
            
            logger.info(f"🔍 Detected {len(detections)} objects in {image_path.name}")
            return detections
            
        except Exception as e:
            logger.error(f"❌ Error detecting objects in {image_path}: {e}")
            return []
    
    def analyze_image_content(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze image content based on detections
        
        Args:
            detections: List of object detections
            
        Returns:
            Analysis summary
        """
        if not detections:
            return {
                'total_objects': 0,
                'medical_objects': 0,
                'primary_object': None,
                'confidence_avg': 0.0,
                'content_type': 'no_objects'
            }
        
        # Count objects
        total_objects = len(detections)
        medical_objects = sum(1 for d in detections if d['is_medical_related'])
        
        # Find primary object (highest confidence)
        primary_detection = max(detections, key=lambda x: x['confidence'])
        
        # Calculate average confidence
        avg_confidence = sum(d['confidence'] for d in detections) / total_objects
        
        # Determine content type
        if medical_objects > 0:
            content_type = 'medical_content'
        elif total_objects > 0:
            content_type = 'general_content'
        else:
            content_type = 'no_objects'
        
        return {
            'total_objects': total_objects,
            'medical_objects': medical_objects,
            'primary_object': primary_detection['class_name'],
            'primary_confidence': primary_detection['confidence'],
            'confidence_avg': avg_confidence,
            'content_type': content_type,
            'detected_classes': list(set(d['class_name'] for d in detections))
        }
    
    def save_detections(self, image_path: Path, detections: List[Dict[str, Any]], 
                       analysis: Dict[str, Any]) -> Path:
        """
        Save detection results to JSON file
        
        Args:
            image_path: Path to the original image
            detections: List of detections
            analysis: Content analysis
            
        Returns:
            Path to saved detection file
        """
        try:
            # Create detection file path
            detection_file = self.detections_path / f"{image_path.stem}_detections.json"
            
            detection_data = {
                'metadata': {
                    'image_path': str(image_path),
                    'image_name': image_path.name,
                    'detection_time': datetime.now().isoformat(),
                    'model_used': f"yolov8{self.model_size}",
                    'confidence_threshold': self.confidence_threshold
                },
                'analysis': analysis,
                'detections': detections
            }
            
            with open(detection_file, 'w', encoding='utf-8') as f:
                json.dump(detection_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved detections to {detection_file}")
            return detection_file
            
        except Exception as e:
            logger.error(f"❌ Error saving detections for {image_path}: {e}")
            return None
    
    def process_image(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """
        Process a single image: detect objects and save results
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Processing results or None if failed
        """
        try:
            # Check if image exists
            if not image_path.exists():
                logger.warning(f"⚠️ Image not found: {image_path}")
                return None
            
            # Check if already processed
            detection_file = self.detections_path / f"{image_path.stem}_detections.json"
            if detection_file.exists():
                logger.info(f"⏭️ Already processed: {image_path.name}")
                return None
            
            # Detect objects
            detections = self.detect_objects(image_path)
            
            # Analyze content
            analysis = self.analyze_image_content(detections)
            
            # Save results
            saved_file = self.save_detections(image_path, detections, analysis)
            
            return {
                'image_path': str(image_path),
                'detection_file': str(saved_file) if saved_file else None,
                'detections_count': len(detections),
                'analysis': analysis,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing {image_path}: {e}")
            return None
    
    def scan_and_process_images(self, channel_name: str = None) -> Dict[str, Any]:
        """
        Scan for new images and process them
        
        Args:
            channel_name: Specific channel to process (optional)
            
        Returns:
            Processing statistics
        """
        stats = {
            'total_images': 0,
            'processed_images': 0,
            'failed_images': 0,
            'channels_processed': set(),
            'results': []
        }
        
        try:
            # Find all image files
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
            
            if channel_name:
                # Process specific channel
                channel_path = self.media_path / channel_name
                if channel_path.exists():
                    image_files = [
                        f for f in channel_path.rglob("*") 
                        if f.suffix.lower() in image_extensions
                    ]
                else:
                    logger.warning(f"⚠️ Channel directory not found: {channel_path}")
                    return stats
            else:
                # Process all channels
                image_files = []
                for channel_dir in self.media_path.iterdir():
                    if channel_dir.is_dir():
                        channel_images = [
                            f for f in channel_dir.rglob("*") 
                            if f.suffix.lower() in image_extensions
                        ]
                        image_files.extend(channel_images)
            
            stats['total_images'] = len(image_files)
            logger.info(f"🔍 Found {len(image_files)} images to process")
            
            # Process each image
            for image_path in image_files:
                try:
                    result = self.process_image(image_path)
                    if result:
                        stats['processed_images'] += 1
                        stats['channels_processed'].add(image_path.parent.name)
                        stats['results'].append(result)
                    else:
                        stats['failed_images'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing {image_path}: {e}")
                    stats['failed_images'] += 1
            
            logger.info(f"✅ Processing complete: {stats['processed_images']}/{stats['total_images']} images processed")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error in scan_and_process_images: {e}")
            return stats
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about processed images"""
        try:
            stats = {
                'total_detection_files': 0,
                'channels_with_detections': set(),
                'total_detections': 0,
                'medical_detections': 0,
                'avg_confidence': 0.0
            }
            
            # Count detection files
            detection_files = list(self.detections_path.glob("*_detections.json"))
            stats['total_detection_files'] = len(detection_files)
            
            # Analyze detection files
            all_confidence_scores = []
            for detection_file in detection_files:
                try:
                    with open(detection_file, 'r') as f:
                        data = json.load(f)
                    
                    # Extract channel name from image path
                    image_path = Path(data['metadata']['image_path'])
                    channel_name = image_path.parent.name
                    stats['channels_with_detections'].add(channel_name)
                    
                    # Count detections
                    detections = data.get('detections', [])
                    stats['total_detections'] += len(detections)
                    
                    # Count medical detections
                    medical_count = sum(1 for d in detections if d.get('is_medical_related', False))
                    stats['medical_detections'] += medical_count
                    
                    # Collect confidence scores
                    confidence_scores = [d['confidence'] for d in detections]
                    all_confidence_scores.extend(confidence_scores)
                    
                except Exception as e:
                    logger.error(f"❌ Error reading {detection_file}: {e}")
            
            # Calculate average confidence
            if all_confidence_scores:
                stats['avg_confidence'] = sum(all_confidence_scores) / len(all_confidence_scores)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting processing stats: {e}")
            return {}

def main():
    """Main function to run YOLO detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YOLO Image Detection for Telegram Medical Data")
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
    
    args = parser.parse_args()
    
    print("🤖 Starting YOLO Image Detection...")
    
    # Initialize detector
    detector = YOLODetector(
        model_size=args.model_size,
        confidence_threshold=args.confidence
    )
    
    # Load model
    if not detector.load_model():
        print("❌ Failed to load YOLO model")
        return
    
    # Process images
    stats = detector.scan_and_process_images(args.channel)
    
    print(f"\n📊 Processing Statistics:")
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
    
    print("\n✅ YOLO detection completed!")

if __name__ == "__main__":
    main() 