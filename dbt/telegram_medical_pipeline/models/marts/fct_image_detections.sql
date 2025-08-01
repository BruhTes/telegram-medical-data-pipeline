{{
  config(
    materialized='table',
    schema='marts'
  )
}}

WITH detection_files AS (
  SELECT 
    file_path,
    file_name,
    channel_name,
    detection_data
  FROM {{ source('raw', 'raw_image_detections') }}
),

extracted_detections AS (
  SELECT 
    df.file_path,
    df.file_name,
    df.channel_name,
    -- Extract message ID from file path (assuming format: message_id_timestamp.ext)
    SPLIT_PART(df.file_name, '_', 1) as message_id_str,
    -- Extract detection data
    detection->>'class_name' as detected_object_class,
    (detection->>'confidence')::FLOAT as confidence_score,
    (detection->>'class_id')::INTEGER as class_id,
    detection->'bbox'->>'x1' as bbox_x1,
    detection->'bbox'->>'y1' as bbox_y1,
    detection->'bbox'->>'x2' as bbox_x2,
    detection->'bbox'->>'y2' as bbox_y2,
    (detection->>'area')::FLOAT as detection_area,
    (detection->>'is_medical_related')::BOOLEAN as is_medical_related,
    detection->>'detection_time' as detection_time,
    -- Extract analysis data
    df.detection_data->'analysis'->>'total_objects' as total_objects_in_image,
    df.detection_data->'analysis'->>'medical_objects' as medical_objects_in_image,
    df.detection_data->'analysis'->>'primary_object' as primary_object,
    (df.detection_data->'analysis'->>'primary_confidence')::FLOAT as primary_confidence,
    (df.detection_data->'analysis'->>'confidence_avg')::FLOAT as avg_confidence,
    df.detection_data->'analysis'->>'content_type' as content_type,
    df.detection_data->'analysis'->>'detected_classes' as detected_classes_array,
    -- Metadata
    df.detection_data->'metadata'->>'detection_time' as processing_time,
    df.detection_data->'metadata'->>'model_used' as model_used,
    (df.detection_data->'metadata'->>'confidence_threshold')::FLOAT as confidence_threshold
  FROM detection_files df,
  LATERAL jsonb_array_elements(df.detection_data->'detections') as detection
  WHERE df.detection_data->'detections' IS NOT NULL
),

cleaned_detections AS (
  SELECT 
    file_path,
    file_name,
    channel_name,
    -- Try to extract message ID (handle cases where it might not be available)
    CASE 
      WHEN message_id_str ~ '^\d+$' THEN message_id_str::BIGINT
      ELSE NULL
    END as message_id,
    detected_object_class,
    confidence_score,
    class_id,
    bbox_x1,
    bbox_y1,
    bbox_x2,
    bbox_y2,
    detection_area,
    is_medical_related,
    detection_time,
    total_objects_in_image,
    medical_objects_in_image,
    primary_object,
    primary_confidence,
    avg_confidence,
    content_type,
    detected_classes_array,
    processing_time,
    model_used,
    confidence_threshold,
    -- Derived fields
    CASE 
      WHEN confidence_score >= 0.8 THEN 'high'
      WHEN confidence_score >= 0.5 THEN 'medium'
      ELSE 'low'
    END as confidence_level,
    CASE 
      WHEN is_medical_related THEN 'medical'
      ELSE 'non_medical'
    END as object_category,
    -- Calculate bounding box dimensions
    (bbox_x2::FLOAT - bbox_x1::FLOAT) as bbox_width,
    (bbox_y2::FLOAT - bbox_y1::FLOAT) as bbox_height,
    -- Calculate relative area (percentage of image)
    CASE 
      WHEN detection_area > 0 THEN 
        ROUND((detection_area / (bbox_width * bbox_height)) * 100, 2)
      ELSE 0
    END as relative_area_percentage
  FROM extracted_detections
  WHERE detected_object_class IS NOT NULL
    AND confidence_score IS NOT NULL
),

final_detections AS (
  SELECT 
    -- Primary key
    ROW_NUMBER() OVER (ORDER BY file_path, detected_object_class, confidence_score DESC) as detection_id,
    
    -- Foreign keys
    message_id,
    channel_name,
    
    -- Detection details
    detected_object_class,
    confidence_score,
    confidence_level,
    class_id,
    object_category,
    is_medical_related,
    
    -- Bounding box information
    bbox_x1,
    bbox_y1,
    bbox_x2,
    bbox_y2,
    bbox_width,
    bbox_height,
    detection_area,
    relative_area_percentage,
    
    -- Image analysis
    total_objects_in_image,
    medical_objects_in_image,
    primary_object,
    primary_confidence,
    avg_confidence,
    content_type,
    detected_classes_array,
    
    -- Processing metadata
    file_path,
    file_name,
    detection_time,
    processing_time,
    model_used,
    confidence_threshold,
    
    -- Audit fields
    CURRENT_TIMESTAMP as created_at
    
  FROM cleaned_detections
)

SELECT * FROM final_detections 