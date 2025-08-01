"""
Database connection module for FastAPI
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Generator, Dict, Any, List
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection manager for FastAPI"""
    
    def __init__(self):
        """Initialize database manager"""
        self.connection_params = {
            'host': 'localhost',
            'database': 'telegram_medical',
            'user': 'postgres',
            'password': 'password',
            'port': 5432
        }
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results as list of dictionaries
        
        Args:
            query: SQL query to execute
            params: Query parameters (optional)
            
        Returns:
            List of dictionaries representing query results
        """
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query_single(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """
        Execute a query and return single result
        
        Args:
            query: SQL query to execute
            params: Query parameters (optional)
            
        Returns:
            Dictionary representing single query result
        """
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query_count(self, query: str, params: tuple = None) -> int:
        """
        Execute a query and return count
        
        Args:
            query: SQL query to execute
            params: Query parameters (optional)
            
        Returns:
            Count of results
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            if conn:
                conn.close()

# Global database manager instance
db = DatabaseManager()

def get_db() -> DatabaseManager:
    """Dependency to get database manager"""
    return db 