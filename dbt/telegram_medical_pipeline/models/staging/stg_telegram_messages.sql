{{
  config(
    materialized='view',
    schema='staging'
  )
}}

WITH raw_data AS (
  SELECT 
    id,
    file_path,
    channel_name,
    scrape_date,
    data_json,
    loaded_at
  FROM {{ source('raw', 'raw_telegram_data') }}
),

extracted_messages AS (
  SELECT 
    rd.id as raw_data_id,
    rd.channel_name,
    rd.scrape_date,
    rd.loaded_at,
    -- Extract message data from JSON
    (msg->>'id')::BIGINT as message_id,
    (msg->>'channel_id')::BIGINT as channel_id,
    (msg->>'sender_id')::BIGINT as sender_id,
    msg->>'text' as message_text,
    msg->>'date' as message_date_str,
    msg->>'sender_info' as sender_info_json,
    msg->>'media' as media_info_json,
    msg->>'local_media_path' as local_media_path,
    msg->>'views' as views,
    msg->>'forwards' as forwards,
    msg->>'replies' as replies,
    -- Extract sender info
    (msg->'sender_info'->>'id')::BIGINT as sender_info_id,
    msg->'sender_info'->>'username' as sender_username,
    msg->'sender_info'->>'first_name' as sender_first_name,
    msg->'sender_info'->>'last_name' as sender_last_name,
    -- Extract media info
    msg->'media'->>'type' as media_type,
    (msg->'media'->>'file_id')::TEXT as media_file_id,
    (msg->'media'->>'file_size')::INTEGER as media_file_size,
    msg->'media'->>'mime_type' as media_mime_type,
    -- Row number for deduplication
    ROW_NUMBER() OVER (
      PARTITION BY (msg->>'id'), rd.channel_name 
      ORDER BY rd.loaded_at DESC
    ) as rn
  FROM raw_data rd,
  LATERAL jsonb_array_elements(rd.data_json->'messages') as msg
  WHERE rd.data_json->'messages' IS NOT NULL
),

cleaned_messages AS (
  SELECT 
    raw_data_id,
    channel_name,
    scrape_date,
    loaded_at,
    message_id,
    channel_id,
    sender_id,
    -- Clean and validate message text
    CASE 
      WHEN message_text IS NULL OR message_text = '' THEN NULL
      ELSE TRIM(message_text)
    END as message_text,
    -- Parse and validate message date
    CASE 
      WHEN message_date_str IS NULL THEN NULL
      ELSE TRY_CAST(message_date_str AS TIMESTAMP)
    END as message_date,
    -- Clean sender info
    sender_username,
    sender_first_name,
    sender_last_name,
    -- Media information
    local_media_path,
    media_type,
    media_file_id,
    media_file_size,
    media_mime_type,
    -- Derived fields
    CASE 
      WHEN message_text IS NOT NULL AND message_text != '' THEN TRUE
      ELSE FALSE
    END as has_text,
    CASE 
      WHEN local_media_path IS NOT NULL THEN TRUE
      ELSE FALSE
    END as has_media,
    CASE 
      WHEN message_text IS NOT NULL AND message_text != '' 
      THEN LENGTH(message_text)
      ELSE 0
    END as message_length,
    -- Extract medical keywords (basic implementation)
    CASE 
      WHEN LOWER(message_text) LIKE '%medicine%' OR 
           LOWER(message_text) LIKE '%drug%' OR
           LOWER(message_text) LIKE '%pharmacy%' OR
           LOWER(message_text) LIKE '%medical%' OR
           LOWER(message_text) LIKE '%health%' OR
           LOWER(message_text) LIKE '%cosmetic%' OR
           LOWER(message_text) LIKE '%cream%' OR
           LOWER(message_text) LIKE '%tablet%' OR
           LOWER(message_text) LIKE '%syrup%' OR
           LOWER(message_text) LIKE '%injection%'
      THEN TRUE
      ELSE FALSE
    END as contains_medical_keywords,
    -- Extract price information (basic regex)
    CASE 
      WHEN message_text ~ '\d+\s*(?:birr|ETB|ብር|dollar|USD|\$|euro|EUR|€)'
      THEN TRUE
      ELSE FALSE
    END as contains_price_info
  FROM extracted_messages
  WHERE rn = 1  -- Remove duplicates
)

SELECT 
  raw_data_id,
  channel_name,
  scrape_date,
  loaded_at,
  message_id,
  channel_id,
  sender_id,
  message_text,
  message_date,
  sender_username,
  sender_first_name,
  sender_last_name,
  local_media_path,
  media_type,
  media_file_id,
  media_file_size,
  media_mime_type,
  has_text,
  has_media,
  message_length,
  contains_medical_keywords,
  contains_price_info,
  -- Add audit fields
  CURRENT_TIMESTAMP as processed_at
FROM cleaned_messages
WHERE message_id IS NOT NULL  -- Ensure we have valid message IDs 