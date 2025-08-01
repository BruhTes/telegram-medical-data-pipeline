#!/usr/bin/env python3
"""
CLI script to run the Telegram scraper
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.telegram_scraper import TelegramScraper
from app.services.data_loader import DataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper_cli.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_scraping_pipeline(limit_per_channel: int = 100, load_to_db: bool = True):
    """Run the complete scraping pipeline"""
    try:
        logger.info("Starting Telegram scraping pipeline")
        
        # Step 1: Scrape Telegram channels
        logger.info("Step 1: Scraping Telegram channels")
        async with TelegramScraper() as scraper:
            await scraper.scrape_all_channels(limit_per_channel)
            
        logger.info("Step 1 completed: Telegram scraping finished")
        
        # Step 2: Load data to PostgreSQL (optional)
        if load_to_db:
            logger.info("Step 2: Loading data to PostgreSQL")
            loader = DataLoader()
            stats = loader.load_all_raw_data()
            loader.create_data_lake_indexes()
            
            final_stats = loader.get_loading_stats()
            logger.info(f"Step 2 completed: Data loaded to PostgreSQL")
            logger.info(f"Final stats: {final_stats}")
        else:
            logger.info("Step 2 skipped: Data loading disabled")
            
        logger.info("Scraping pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Error in scraping pipeline: {e}")
        raise

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Telegram Medical Data Scraper")
    parser.add_argument(
        "--limit", 
        type=int, 
        default=100,
        help="Number of messages to scrape per channel (default: 100)"
    )
    parser.add_argument(
        "--skip-db-load", 
        action="store_true",
        help="Skip loading data to PostgreSQL"
    )
    parser.add_argument(
        "--channels", 
        nargs="+",
        help="Specific channels to scrape (default: all medical channels)"
    )
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    try:
        # Run the pipeline
        asyncio.run(run_scraping_pipeline(
            limit_per_channel=args.limit,
            load_to_db=not args.skip_db_load
        ))
        
        print("✅ Scraping pipeline completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        print("⚠️  Pipeline interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 