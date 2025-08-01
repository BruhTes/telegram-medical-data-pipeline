{{
  config(
    materialized='table',
    schema='marts'
  )
}}

WITH messages_with_dims AS (
  SELECT 
    -- Message identifiers
    stm.raw_data_id,
    stm.message_id,
    stm.channel_name,
    stm.channel_id,
    stm.sender_id,
    
    -- Date dimension
    DATE(stm.message_date) as message_date_id,
    
    -- Message content
    stm.message_text,
    stm.message_length,
    stm.has_text,
    stm.has_media,
    stm.contains_medical_keywords,
    stm.contains_price_info,
    
    -- Media information
    stm.local_media_path,
    stm.media_type,
    stm.media_file_id,
    stm.media_file_size,
    stm.media_mime_type,
    
    -- Sender information
    stm.sender_username,
    stm.sender_first_name,
    stm.sender_last_name,
    
    -- Channel information from dimension
    dc.category as channel_category,
    dc.priority as channel_priority,
    dc.activity_level as channel_activity_level,
    dc.channel_type as channel_type,
    dc.medical_content_percentage as channel_medical_percentage,
    dc.media_content_percentage as channel_media_percentage,
    
    -- Date attributes from dimension
    dd.year as message_year,
    dd.month as message_month,
    dd.day as message_day,
    dd.day_of_week as message_day_of_week,
    dd.quarter as message_quarter,
    dd.month_name as message_month_name,
    dd.day_name as message_day_name,
    dd.is_business_day as message_is_business_day,
    dd.is_weekend as message_is_weekend,
    dd.season as message_season,
    
    -- Processing metadata
    stm.processed_at,
    stm.scrape_date,
    stm.loaded_at
    
  FROM {{ ref('stg_telegram_messages') }} stm
  LEFT JOIN {{ ref('dim_channels') }} dc ON stm.channel_name = dc.channel_name
  LEFT JOIN {{ ref('dim_dates') }} dd ON DATE(stm.message_date) = dd.date_id
  WHERE stm.message_id IS NOT NULL
),

enriched_messages AS (
  SELECT 
    -- Primary key
    raw_data_id,
    message_id,
    
    -- Foreign keys to dimensions
    channel_name,
    channel_id,
    sender_id,
    message_date_id,
    
    -- Message metrics
    message_text,
    message_length,
    has_text,
    has_media,
    contains_medical_keywords,
    contains_price_info,
    
    -- Media metrics
    local_media_path,
    media_type,
    media_file_id,
    media_file_size,
    media_mime_type,
    
    -- Sender metrics
    sender_username,
    sender_first_name,
    sender_last_name,
    
    -- Channel metrics
    channel_category,
    channel_priority,
    channel_activity_level,
    channel_type,
    channel_medical_percentage,
    channel_media_percentage,
    
    -- Time metrics
    message_year,
    message_month,
    message_day,
    message_day_of_week,
    message_quarter,
    message_month_name,
    message_day_name,
    message_is_business_day,
    message_is_weekend,
    message_season,
    
    -- Derived metrics
    CASE 
      WHEN message_length > 100 THEN 'long'
      WHEN message_length > 50 THEN 'medium'
      ELSE 'short'
    END as message_length_category,
    
    CASE 
      WHEN contains_medical_keywords AND contains_price_info THEN 'medical_commerce'
      WHEN contains_medical_keywords THEN 'medical_info'
      WHEN contains_price_info THEN 'commerce'
      ELSE 'general'
    END as message_type,
    
    CASE 
      WHEN has_media AND contains_medical_keywords THEN 'medical_media'
      WHEN has_media THEN 'media_only'
      WHEN contains_medical_keywords THEN 'medical_text'
      ELSE 'text_only'
    END as content_type,
    
    -- Engagement indicators (placeholder for future metrics)
    FALSE as has_views,
    FALSE as has_forwards,
    FALSE as has_replies,
    0 as view_count,
    0 as forward_count,
    0 as reply_count,
    
    -- Processing metadata
    processed_at,
    scrape_date,
    loaded_at,
    CURRENT_TIMESTAMP as created_at
    
  FROM messages_with_dims
)

SELECT * FROM enriched_messages 