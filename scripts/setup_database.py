#!/usr/bin/env python3
"""
Database setup script for Telegram Medical Data Pipeline
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core.config import settings

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="password"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'telegram_medical'")
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute("CREATE DATABASE telegram_medical")
                print("✅ Database 'telegram_medical' created successfully")
            else:
                print("✅ Database 'telegram_medical' already exists")
                
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ Could not connect to PostgreSQL: {e}")
        print("Please make sure PostgreSQL is running and accessible")
        return False
        
    return True

def create_tables():
    """Create the required tables"""
    try:
        # Connect to our database
        conn = psycopg2.connect(
            host="localhost",
            database="telegram_medical",
            user="postgres",
            password="password"
        )
        
        # Read and execute the init.sql file
        init_sql_path = Path(__file__).parent.parent / "init.sql"
        
        if init_sql_path.exists():
            with open(init_sql_path, 'r') as f:
                sql_commands = f.read()
                
            with conn.cursor() as cursor:
                cursor.execute(sql_commands)
                
            conn.commit()
            print("✅ Database tables created successfully")
        else:
            print("❌ init.sql file not found")
            return False
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
        
    return True

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="telegram_medical",
            user="postgres",
            password="password"
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Connected to PostgreSQL: {version[0]}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🗄️ Setting up PostgreSQL database...")
    
    # Step 1: Create database
    if not create_database():
        return False
        
    # Step 2: Create tables
    if not create_tables():
        return False
        
    # Step 3: Test connection
    if not test_connection():
        return False
        
    print("🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Configure your .env file with database credentials")
    print("2. Set up Telegram API credentials")
    print("3. Run the scraper to collect data")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 