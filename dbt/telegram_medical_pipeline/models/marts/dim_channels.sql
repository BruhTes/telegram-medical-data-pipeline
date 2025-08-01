{{
  config(
    materialized='table',
    schema='marts'
  )
}}

WITH channel_data AS (
  SELECT DISTINCT
    channel_name,
    channel_id,
    COUNT(*) as message_count,
    MIN(message_date) as first_message_date,
    MAX(message_date) as last_message_date,
    COUNT(CASE WHEN has_media THEN 1 END) as media_count,
    COUNT(CASE WHEN contains_medical_keywords THEN 1 END) as medical_messages_count,
    COUNT(CASE WHEN contains_price_info THEN 1 END) as price_messages_count,
    AVG(message_length) as avg_message_length,
    COUNT(DISTINCT sender_id) as unique_senders
  FROM {{ ref('stg_telegram_messages') }}
  WHERE channel_name IS NOT NULL
  GROUP BY channel_name, channel_id
),

channel_categories AS (
  SELECT 
    channel_name,
    CASE 
      WHEN LOWER(channel_name) LIKE '%cosmetic%' THEN 'cosmetics'
      WHEN LOWER(channel_name) LIKE '%pharma%' THEN 'pharmaceuticals'
      WHEN LOWER(channel_name) LIKE '%medical%' THEN 'medical_supplies'
      WHEN LOWER(channel_name) LIKE '%health%' THEN 'healthcare'
      WHEN LOWER(channel_name) LIKE '%pharmacy%' THEN 'pharmacy'
      ELSE 'general'
    END as category,
    CASE 
      WHEN LOWER(channel_name) IN ('lobelia4cosmetics', 'tikvahpharma', 'chemed_ethiopia') THEN 'high'
      WHEN LOWER(channel_name) IN ('ethiopian_pharmacy', 'medical_supplies_ethiopia', 'healthcare_ethiopia') THEN 'medium'
      ELSE 'low'
    END as priority
  FROM channel_data
)

SELECT 
  cd.channel_name,
  cd.channel_id,
  cc.category,
  cc.priority,
  cd.message_count,
  cd.media_count,
  cd.medical_messages_count,
  cd.price_messages_count,
  cd.avg_message_length,
  cd.unique_senders,
  cd.first_message_date,
  cd.last_message_date,
  -- Calculate engagement metrics
  CASE 
    WHEN cd.message_count > 0 THEN 
      ROUND((cd.medical_messages_count::FLOAT / cd.message_count) * 100, 2)
    ELSE 0 
  END as medical_content_percentage,
  CASE 
    WHEN cd.message_count > 0 THEN 
      ROUND((cd.media_count::FLOAT / cd.message_count) * 100, 2)
    ELSE 0 
  END as media_content_percentage,
  -- Channel activity level
  CASE 
    WHEN cd.message_count >= 100 THEN 'high'
    WHEN cd.message_count >= 50 THEN 'medium'
    ELSE 'low'
  END as activity_level,
  -- Channel type based on content
  CASE 
    WHEN cd.medical_messages_count > cd.message_count * 0.7 THEN 'medical_focused'
    WHEN cd.media_count > cd.message_count * 0.5 THEN 'media_heavy'
    WHEN cd.price_messages_count > cd.message_count * 0.3 THEN 'commerce_focused'
    ELSE 'general'
  END as channel_type,
  CURRENT_TIMESTAMP as created_at,
  CURRENT_TIMESTAMP as updated_at
FROM channel_data cd
LEFT JOIN channel_categories cc ON cd.channel_name = cc.channel_name
WHERE cd.channel_name IS NOT NULL 