"""
CRUD operations for analytical queries against dbt models
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from app.api.database import DatabaseManager
from app.api.schemas import (
    ChannelInfo, ChannelActivity, MessageInfo, MessageSearchResult,
    ProductMention, AnalyticsSummary, ChannelRanking, ImageDetection
)

logger = logging.getLogger(__name__)

class AnalyticsCRUD:
    """CRUD operations for analytical queries"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_channels(self, limit: int = 50, offset: int = 0) -> List[ChannelInfo]:
        """Get all channels with analytics"""
        query = """
            SELECT 
                channel_name,
                channel_id,
                category,
                priority,
                message_count,
                media_count,
                medical_messages_count,
                price_messages_count,
                avg_message_length,
                unique_senders,
                first_message_date,
                last_message_date,
                medical_content_percentage,
                media_content_percentage,
                activity_level,
                channel_type
            FROM marts.dim_channels
            ORDER BY message_count DESC
            LIMIT %s OFFSET %s
        """
        
        results = self.db.execute_query(query, (limit, offset))
        return [ChannelInfo(**result) for result in results]
    
    def get_channel_activity(self, channel_name: str, date_from: Optional[datetime] = None, 
                           date_to: Optional[datetime] = None, group_by: str = "day") -> List[ChannelActivity]:
        """Get channel activity over time"""
        
        # Build date filter
        date_filter = ""
        params = [channel_name]
        
        if date_from and date_to:
            date_filter = "AND message_date_id BETWEEN %s AND %s"
            params.extend([date_from.date(), date_to.date()])
        elif date_from:
            date_filter = "AND message_date_id >= %s"
            params.append(date_from.date())
        elif date_to:
            date_filter = "AND message_date_id <= %s"
            params.append(date_to.date())
        
        # Build grouping
        if group_by == "week":
            group_clause = "DATE_TRUNC('week', message_date_id) as activity_date"
        elif group_by == "month":
            group_clause = "DATE_TRUNC('month', message_date_id) as activity_date"
        else:
            group_clause = "message_date_id as activity_date"
        
        query = f"""
            SELECT 
                %s as channel_name,
                {group_clause},
                COUNT(*) as message_count,
                COUNT(CASE WHEN has_media THEN 1 END) as media_count,
                COUNT(CASE WHEN contains_medical_keywords THEN 1 END) as medical_count,
                COUNT(CASE WHEN contains_price_info THEN 1 END) as price_count,
                AVG(message_length) as avg_message_length,
                COUNT(DISTINCT sender_id) as unique_senders
            FROM marts.fct_messages
            WHERE channel_name = %s {date_filter}
            GROUP BY activity_date
            ORDER BY activity_date DESC
        """
        
        results = self.db.execute_query(query, params)
        return [ChannelActivity(**result) for result in results]
    
    def search_messages(self, query: str, limit: int = 10, offset: int = 0,
                       channel_filter: Optional[str] = None, date_from: Optional[datetime] = None,
                       date_to: Optional[datetime] = None, medical_only: bool = False,
                       price_only: bool = False) -> List[MessageSearchResult]:
        """Search messages with relevance scoring"""
        
        # Build filters
        filters = []
        params = [f"%{query}%"]  # For ILIKE search
        
        if channel_filter:
            filters.append("channel_name = %s")
            params.append(channel_filter)
        
        if date_from:
            filters.append("message_date_id >= %s")
            params.append(date_from.date())
        
        if date_to:
            filters.append("message_date_id <= %s")
            params.append(date_to.date())
        
        if medical_only:
            filters.append("contains_medical_keywords = TRUE")
        
        if price_only:
            filters.append("contains_price_info = TRUE")
        
        where_clause = " AND ".join(filters) if filters else "1=1"
        
        # Calculate relevance score based on query match
        query = f"""
            SELECT 
                message_id,
                channel_name,
                message_text,
                message_date,
                contains_medical_keywords,
                contains_price_info,
                CASE 
                    WHEN message_text ILIKE %s THEN 1.0
                    WHEN message_text ILIKE %s THEN 0.8
                    WHEN message_text ILIKE %s THEN 0.6
                    ELSE 0.3
                END as relevance_score
            FROM marts.fct_messages
            WHERE message_text IS NOT NULL 
                AND message_text != ''
                AND ({where_clause})
            ORDER BY relevance_score DESC, message_date DESC
            LIMIT %s OFFSET %s
        """
        
        # Add relevance score parameters
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%", limit, offset])
        
        results = self.db.execute_query(query, params)
        return [MessageSearchResult(**result) for result in results]
    
    def get_top_products(self, limit: int = 10, channel_filter: Optional[str] = None,
                        date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
                        medical_only: bool = False) -> List[ProductMention]:
        """Get top mentioned products"""
        
        # Build filters
        filters = []
        params = []
        
        if channel_filter:
            filters.append("channel_name = %s")
            params.append(channel_filter)
        
        if date_from:
            filters.append("message_date_id >= %s")
            params.append(date_from.date())
        
        if date_to:
            filters.append("message_date_id <= %s")
            params.append(date_to.date())
        
        if medical_only:
            filters.append("contains_medical_keywords = TRUE")
        
        where_clause = " AND ".join(filters) if filters else "1=1"
        
        # Extract product names from message text (simplified approach)
        query = f"""
            WITH product_mentions AS (
                SELECT 
                    channel_name,
                    message_text,
                    message_date,
                    contains_medical_keywords,
                    -- Extract potential product names (simplified)
                    CASE 
                        WHEN message_text ~* '\\b(paracetamol|aspirin|ibuprofen|amoxicillin|vitamin|cream|tablet|syrup|injection|antibiotic|medicine|drug|pill|capsule)\\b' 
                        THEN regexp_matches(message_text, '\\b(paracetamol|aspirin|ibuprofen|amoxicillin|vitamin|cream|tablet|syrup|injection|antibiotic|medicine|drug|pill|capsule)\\b', 'gi')
                        ELSE NULL
                    END as product_match
                FROM marts.fct_messages
                WHERE message_text IS NOT NULL 
                    AND message_text != ''
                    AND contains_medical_keywords = TRUE
                    AND ({where_clause})
            )
            SELECT 
                COALESCE(product_match[1], 'Unknown Product') as product_name,
                COUNT(*) as mention_count,
                channel_name,
                MIN(message_date) as first_mentioned,
                MAX(message_date) as last_mentioned,
                TRUE as medical_related
            FROM product_mentions
            WHERE product_match IS NOT NULL
            GROUP BY product_match[1], channel_name
            ORDER BY mention_count DESC
            LIMIT %s
        """
        
        params.append(limit)
        results = self.db.execute_query(query, params)
        return [ProductMention(**result) for result in results]
    
    def get_analytics_summary(self) -> AnalyticsSummary:
        """Get overall analytics summary"""
        
        # Get basic counts
        counts_query = """
            SELECT 
                COUNT(*) as total_messages,
                COUNT(DISTINCT channel_name) as total_channels,
                COUNT(CASE WHEN has_media THEN 1 END) as total_media,
                COUNT(CASE WHEN contains_medical_keywords THEN 1 END) as total_medical_messages,
                COUNT(CASE WHEN contains_price_info THEN 1 END) as total_price_messages,
                AVG(message_length) as avg_message_length
            FROM marts.fct_messages
        """
        
        counts = self.db.execute_query_single(counts_query)
        
        # Get date range
        date_range_query = """
            SELECT 
                MIN(message_date_id) as earliest_date,
                MAX(message_date_id) as latest_date
            FROM marts.fct_messages
        """
        
        date_range = self.db.execute_query_single(date_range_query)
        
        # Calculate medical content percentage
        medical_percentage = 0
        if counts['total_messages'] > 0:
            medical_percentage = (counts['total_medical_messages'] / counts['total_messages']) * 100
        
        return AnalyticsSummary(
            total_messages=counts['total_messages'],
            total_channels=counts['total_channels'],
            total_media=counts['total_media'],
            total_medical_messages=counts['total_medical_messages'],
            total_price_messages=counts['total_price_messages'],
            date_range={
                'earliest': date_range['earliest_date'],
                'latest': date_range['latest_date']
            },
            avg_message_length=counts['avg_message_length'] or 0,
            medical_content_percentage=medical_percentage
        )
    
    def get_channel_rankings(self, metric: str = "message_count", limit: int = 10) -> List[ChannelRanking]:
        """Get channel rankings by various metrics"""
        
        valid_metrics = {
            "message_count": "message_count",
            "media_count": "media_count", 
            "medical_messages": "medical_messages_count",
            "price_messages": "price_messages_count",
            "activity_level": "CASE WHEN message_count >= 100 THEN 3 WHEN message_count >= 50 THEN 2 ELSE 1 END",
            "medical_percentage": "medical_content_percentage",
            "media_percentage": "media_content_percentage"
        }
        
        if metric not in valid_metrics:
            metric = "message_count"
        
        metric_column = valid_metrics[metric]
        
        query = f"""
            SELECT 
                ROW_NUMBER() OVER (ORDER BY {metric_column} DESC) as rank,
                channel_name,
                {metric_column} as metric_value,
                %s as metric_type
            FROM marts.dim_channels
            ORDER BY {metric_column} DESC
            LIMIT %s
        """
        
        results = self.db.execute_query(query, (metric, limit))
        return [ChannelRanking(**result) for result in results]
    
    def get_image_detections(self, channel_name: Optional[str] = None, 
                           object_class: Optional[str] = None,
                           medical_only: bool = False,
                           limit: int = 50, offset: int = 0) -> List[ImageDetection]:
        """Get image detections with filters"""
        
        filters = []
        params = []
        
        if channel_name:
            filters.append("channel_name = %s")
            params.append(channel_name)
        
        if object_class:
            filters.append("detected_object_class = %s")
            params.append(object_class)
        
        if medical_only:
            filters.append("is_medical_related = TRUE")
        
        where_clause = " AND ".join(filters) if filters else "1=1"
        
        query = f"""
            SELECT 
                detection_id,
                message_id,
                channel_name,
                detected_object_class,
                confidence_score,
                confidence_level,
                is_medical_related,
                JSON_BUILD_OBJECT(
                    'x1', bbox_x1,
                    'y1', bbox_y1,
                    'x2', bbox_x2,
                    'y2', bbox_y2
                ) as bbox_coordinates,
                detection_area,
                detection_time
            FROM marts.fct_image_detections
            WHERE {where_clause}
            ORDER BY detection_time DESC
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        results = self.db.execute_query(query, params)
        return [ImageDetection(**result) for result in results]
    
    def get_channel_by_name(self, channel_name: str) -> Optional[ChannelInfo]:
        """Get specific channel information"""
        query = """
            SELECT 
                channel_name,
                channel_id,
                category,
                priority,
                message_count,
                media_count,
                medical_messages_count,
                price_messages_count,
                avg_message_length,
                unique_senders,
                first_message_date,
                last_message_date,
                medical_content_percentage,
                media_content_percentage,
                activity_level,
                channel_type
            FROM marts.dim_channels
            WHERE channel_name = %s
        """
        
        result = self.db.execute_query_single(query, (channel_name,))
        return ChannelInfo(**result) if result else None
    
    def get_messages_by_channel(self, channel_name: str, limit: int = 50, 
                               offset: int = 0) -> List[MessageInfo]:
        """Get messages for a specific channel"""
        query = """
            SELECT 
                message_id,
                channel_name,
                sender_id,
                sender_username,
                message_text,
                message_length,
                message_date,
                has_text,
                has_media,
                contains_medical_keywords,
                contains_price_info,
                message_type,
                content_type,
                media_type,
                local_media_path
            FROM marts.fct_messages
            WHERE channel_name = %s
            ORDER BY message_date DESC
            LIMIT %s OFFSET %s
        """
        
        results = self.db.execute_query(query, (channel_name, limit, offset))
        return [MessageInfo(**result) for result in results]
    
    def get_count(self, table: str, filters: Dict[str, Any] = None) -> int:
        """Get count of records with optional filters"""
        query = f"SELECT COUNT(*) FROM {table}"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = %s")
                params.append(value)
            query += f" WHERE {' AND '.join(conditions)}"
        
        return self.db.execute_query_count(query, tuple(params) if params else None) 