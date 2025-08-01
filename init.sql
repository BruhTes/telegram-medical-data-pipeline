-- Initialize Telegram Medical Data Pipeline Database
-- This script creates the necessary tables for the data pipeline

-- Create database if it doesn't exist
-- (This will be handled by Docker environment variables)

-- Create raw data tables
CREATE TABLE IF NOT EXISTS raw_telegram_messages (
    id SERIAL PRIMARY KEY,
    message_id BIGINT,
    chat_id BIGINT,
    chat_title TEXT,
    sender_id BIGINT,
    sender_username TEXT,
    message_text TEXT,
    message_date TIMESTAMP,
    has_media BOOLEAN DEFAULT FALSE,
    media_type TEXT,
    media_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_telegram_media (
    id SERIAL PRIMARY KEY,
    message_id BIGINT,
    file_id TEXT,
    file_unique_id TEXT,
    file_size INTEGER,
    file_path TEXT,
    mime_type TEXT,
    local_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create processed data tables
CREATE TABLE IF NOT EXISTS processed_messages (
    id SERIAL PRIMARY KEY,
    raw_message_id INTEGER REFERENCES raw_telegram_messages(id),
    cleaned_text TEXT,
    language TEXT,
    sentiment_score FLOAT,
    medical_keywords TEXT[],
    product_mentions TEXT[],
    price_mentions TEXT[],
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed_media (
    id SERIAL PRIMARY KEY,
    raw_media_id INTEGER REFERENCES raw_telegram_media(id),
    yolo_detections JSONB,
    detected_objects TEXT[],
    confidence_scores FLOAT[],
    image_analysis_results JSONB,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create analytics tables
CREATE TABLE IF NOT EXISTS analytics_daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE,
    total_messages INTEGER,
    total_media INTEGER,
    unique_channels INTEGER,
    medical_products_count INTEGER,
    avg_sentiment_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics_product_mentions (
    id SERIAL PRIMARY KEY,
    product_name TEXT,
    mention_count INTEGER,
    channel_id BIGINT,
    first_mentioned TIMESTAMP,
    last_mentioned TIMESTAMP,
    price_range TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_raw_messages_chat_id ON raw_telegram_messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_raw_messages_date ON raw_telegram_messages(message_date);
CREATE INDEX IF NOT EXISTS idx_processed_messages_keywords ON processed_messages USING GIN(medical_keywords);
CREATE INDEX IF NOT EXISTS idx_analytics_daily_stats_date ON analytics_daily_stats(date);
CREATE INDEX IF NOT EXISTS idx_analytics_product_mentions_product ON analytics_product_mentions(product_name);

-- Insert initial data if needed
-- (This can be expanded based on requirements) 