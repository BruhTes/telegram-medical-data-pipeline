"""
Logging configuration for the Telegram Medical Data Pipeline
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """Setup comprehensive logging configuration"""
    
    # Create logs directory
    Path(log_dir).mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    handlers.append(console_handler)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    handlers.append(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "errors.log"),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    handlers.append(error_handler)
    
    # Telegram scraper specific handler
    scraper_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "telegram_scraper.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    scraper_handler.setLevel(logging.DEBUG)
    scraper_handler.setFormatter(detailed_formatter)
    handlers.append(scraper_handler)
    
    # Data loader specific handler
    loader_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "data_loader.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    loader_handler.setLevel(logging.DEBUG)
    loader_handler.setFormatter(detailed_formatter)
    handlers.append(loader_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Set specific loggers
    loggers = {
        "telegram_scraper": logging.getLogger("app.services.telegram_scraper"),
        "data_loader": logging.getLogger("app.services.data_loader"),
        "api": logging.getLogger("app.api"),
        "config": logging.getLogger("app.core.config")
    }
    
    for logger_name, logger_instance in loggers.items():
        logger_instance.setLevel(logging.DEBUG)
        # Don't propagate to root logger to avoid duplicate logs
        logger_instance.propagate = False
        
        # Add handlers to specific loggers
        for handler in handlers:
            logger_instance.addHandler(handler)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

def log_scraping_stats(stats: dict, logger: logging.Logger):
    """Log scraping statistics"""
    logger.info("=== Scraping Statistics ===")
    logger.info(f"Total channels processed: {len(stats)}")
    
    for channel, count in stats.items():
        logger.info(f"  {channel}: {count} messages")
    
    total_messages = sum(stats.values())
    logger.info(f"Total messages scraped: {total_messages}")
    logger.info("=== End Statistics ===")

def log_loading_stats(stats: dict, logger: logging.Logger):
    """Log data loading statistics"""
    logger.info("=== Data Loading Statistics ===")
    logger.info(f"Total messages loaded: {stats.get('total_messages', 0)}")
    logger.info(f"Total media files: {stats.get('total_media', 0)}")
    logger.info(f"Unique channels: {stats.get('unique_channels', 0)}")
    
    date_range = stats.get('date_range', {})
    if date_range.get('earliest'):
        logger.info(f"Date range: {date_range['earliest']} to {date_range['latest']}")
    
    logger.info("=== End Loading Statistics ===")

def log_error_with_context(error: Exception, context: str, logger: logging.Logger):
    """Log an error with additional context"""
    logger.error(f"Error in {context}: {str(error)}")
    logger.error(f"Error type: {type(error).__name__}")
    logger.error(f"Error details: {error}")
    
    # Log stack trace for debugging
    import traceback
    logger.error(f"Stack trace:\n{traceback.format_exc()}")

def log_channel_status(channel_name: str, status: str, details: str = "", logger: logging.Logger):
    """Log channel processing status"""
    status_emoji = {
        "started": "🟡",
        "completed": "✅",
        "failed": "❌",
        "skipped": "⏭️",
        "rate_limited": "⏳"
    }
    
    emoji = status_emoji.get(status, "ℹ️")
    logger.info(f"{emoji} Channel {channel_name}: {status}")
    
    if details:
        logger.info(f"  Details: {details}")

def log_pipeline_progress(step: str, current: int, total: int, logger: logging.Logger):
    """Log pipeline progress"""
    percentage = (current / total) * 100 if total > 0 else 0
    logger.info(f"Pipeline progress - {step}: {current}/{total} ({percentage:.1f}%)")
    
    # Progress bar
    bar_length = 20
    filled_length = int(bar_length * current // total)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    logger.info(f"Progress: [{bar}] {percentage:.1f}%") 