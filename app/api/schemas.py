"""
Pydantic schemas for FastAPI request and response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class ChannelCategory(str, Enum):
    COSMETICS = "cosmetics"
    PHARMACEUTICALS = "pharmaceuticals"
    MEDICAL_SUPPLIES = "medical_supplies"
    HEALTHCARE = "healthcare"
    PHARMACY = "pharmacy"
    GENERAL = "general"

class ChannelPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ContentType(str, Enum):
    MEDICAL_CONTENT = "medical_content"
    GENERAL_CONTENT = "general_content"
    NO_OBJECTS = "no_objects"

class MessageType(str, Enum):
    MEDICAL_COMMERCE = "medical_commerce"
    MEDICAL_INFO = "medical_info"
    COMMERCE = "commerce"
    GENERAL = "general"

# Base Models
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, le=100, description="Page size")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=0, description="Total number of pages")

# Channel Models
class ChannelInfo(BaseModel):
    """Channel information"""
    channel_name: str = Field(..., description="Name of the Telegram channel")
    channel_id: Optional[int] = Field(None, description="Telegram channel ID")
    category: Optional[ChannelCategory] = Field(None, description="Channel category")
    priority: Optional[ChannelPriority] = Field(None, description="Channel priority level")
    message_count: int = Field(..., ge=0, description="Total number of messages")
    media_count: int = Field(..., ge=0, description="Number of messages with media")
    medical_messages_count: int = Field(..., ge=0, description="Number of medical messages")
    price_messages_count: int = Field(..., ge=0, description="Number of price-related messages")
    medical_content_percentage: float = Field(..., ge=0, le=100, description="Percentage of medical content")
    media_content_percentage: float = Field(..., ge=0, le=100, description="Percentage of media content")
    activity_level: str = Field(..., description="Channel activity level")
    channel_type: str = Field(..., description="Type of channel")
    first_message_date: Optional[datetime] = Field(None, description="Date of first message")
    last_message_date: Optional[datetime] = Field(None, description="Date of last message")

class ChannelActivity(BaseModel):
    """Channel activity information"""
    channel_name: str = Field(..., description="Channel name")
    date: datetime = Field(..., description="Activity date")
    message_count: int = Field(..., ge=0, description="Number of messages on this date")
    media_count: int = Field(..., ge=0, description="Number of media messages")
    medical_count: int = Field(..., ge=0, description="Number of medical messages")
    price_count: int = Field(..., ge=0, description="Number of price-related messages")
    avg_message_length: float = Field(..., ge=0, description="Average message length")
    unique_senders: int = Field(..., ge=0, description="Number of unique senders")

# Message Models
class MessageInfo(BaseModel):
    """Message information"""
    message_id: int = Field(..., description="Telegram message ID")
    channel_name: str = Field(..., description="Channel name")
    sender_id: Optional[int] = Field(None, description="Sender ID")
    sender_username: Optional[str] = Field(None, description="Sender username")
    message_text: Optional[str] = Field(None, description="Message text content")
    message_length: int = Field(..., ge=0, description="Message length")
    message_date: datetime = Field(..., description="Message timestamp")
    has_text: bool = Field(..., description="Whether message has text")
    has_media: bool = Field(..., description="Whether message has media")
    contains_medical_keywords: bool = Field(..., description="Whether message contains medical keywords")
    contains_price_info: bool = Field(..., description="Whether message contains price information")
    message_type: Optional[MessageType] = Field(None, description="Type of message")
    content_type: str = Field(..., description="Type of content")
    media_type: Optional[str] = Field(None, description="Type of media if present")
    local_media_path: Optional[str] = Field(None, description="Path to local media file")

class MessageSearchResult(BaseModel):
    """Message search result"""
    message_id: int = Field(..., description="Message ID")
    channel_name: str = Field(..., description="Channel name")
    message_text: Optional[str] = Field(None, description="Message text")
    message_date: datetime = Field(..., description="Message date")
    contains_medical_keywords: bool = Field(..., description="Contains medical keywords")
    contains_price_info: bool = Field(..., description="Contains price information")
    relevance_score: float = Field(..., ge=0, le=1, description="Search relevance score")

# Product Models
class ProductMention(BaseModel):
    """Product mention information"""
    product_name: str = Field(..., description="Name of the product")
    mention_count: int = Field(..., ge=0, description="Number of mentions")
    channel_name: str = Field(..., description="Channel where mentioned")
    first_mentioned: datetime = Field(..., description="First mention date")
    last_mentioned: datetime = Field(..., description="Last mention date")
    price_range: Optional[str] = Field(None, description="Price range if available")
    medical_related: bool = Field(..., description="Whether product is medical-related")

# Analytics Models
class AnalyticsSummary(BaseModel):
    """Analytics summary"""
    total_messages: int = Field(..., ge=0, description="Total messages")
    total_channels: int = Field(..., ge=0, description="Total channels")
    total_media: int = Field(..., ge=0, description="Total media messages")
    total_medical_messages: int = Field(..., ge=0, description="Total medical messages")
    total_price_messages: int = Field(..., ge=0, description="Total price-related messages")
    date_range: Dict[str, datetime] = Field(..., description="Date range of data")
    avg_message_length: float = Field(..., ge=0, description="Average message length")
    medical_content_percentage: float = Field(..., ge=0, le=100, description="Percentage of medical content")

class ChannelRanking(BaseModel):
    """Channel ranking information"""
    rank: int = Field(..., ge=1, description="Ranking position")
    channel_name: str = Field(..., description="Channel name")
    metric_value: float = Field(..., description="Metric value for ranking")
    metric_type: str = Field(..., description="Type of metric")

# Image Detection Models
class ImageDetection(BaseModel):
    """Image detection information"""
    detection_id: int = Field(..., description="Detection ID")
    message_id: Optional[int] = Field(None, description="Associated message ID")
    channel_name: str = Field(..., description="Channel name")
    detected_object_class: str = Field(..., description="Detected object class")
    confidence_score: float = Field(..., ge=0, le=1, description="Detection confidence")
    confidence_level: str = Field(..., description="Confidence level (high/medium/low)")
    is_medical_related: bool = Field(..., description="Whether object is medical-related")
    bbox_coordinates: Dict[str, float] = Field(..., description="Bounding box coordinates")
    detection_area: float = Field(..., ge=0, description="Detection area")
    detection_time: datetime = Field(..., description="Detection timestamp")

# Request Models
class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    channel_filter: Optional[str] = Field(None, description="Filter by specific channel")
    date_from: Optional[datetime] = Field(None, description="Start date filter")
    date_to: Optional[datetime] = Field(None, description="End date filter")
    medical_only: bool = Field(False, description="Filter medical messages only")
    price_only: bool = Field(False, description="Filter price-related messages only")

class ChannelActivityRequest(BaseModel):
    """Channel activity request model"""
    channel_name: str = Field(..., description="Channel name")
    date_from: Optional[datetime] = Field(None, description="Start date")
    date_to: Optional[datetime] = Field(None, description="End date")
    group_by: str = Field("day", pattern="^(day|week|month)$", description="Grouping period")

class TopProductsRequest(BaseModel):
    """Top products request model"""
    limit: int = Field(10, ge=1, le=100, description="Number of top products")
    channel_filter: Optional[str] = Field(None, description="Filter by specific channel")
    date_from: Optional[datetime] = Field(None, description="Start date filter")
    date_to: Optional[datetime] = Field(None, description="End date filter")
    medical_only: bool = Field(False, description="Filter medical products only")

# Response Models
class ChannelsResponse(BaseResponse):
    """Channels response"""
    data: List[ChannelInfo] = Field(..., description="List of channels")
    pagination: Optional[PaginationInfo] = Field(None, description="Pagination information")

class ChannelActivityResponse(BaseResponse):
    """Channel activity response"""
    data: List[ChannelActivity] = Field(..., description="Channel activity data")
    channel_info: Optional[ChannelInfo] = Field(None, description="Channel information")

class MessagesResponse(BaseResponse):
    """Messages response"""
    data: List[MessageInfo] = Field(..., description="List of messages")
    pagination: Optional[PaginationInfo] = Field(None, description="Pagination information")

class SearchResponse(BaseResponse):
    """Search response"""
    data: List[MessageSearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., ge=0, description="Total number of results")
    query: str = Field(..., description="Search query used")

class TopProductsResponse(BaseResponse):
    """Top products response"""
    data: List[ProductMention] = Field(..., description="Top products")
    total_products: int = Field(..., ge=0, description="Total number of products")

class AnalyticsResponse(BaseResponse):
    """Analytics response"""
    data: AnalyticsSummary = Field(..., description="Analytics summary")

class ImageDetectionsResponse(BaseResponse):
    """Image detections response"""
    data: List[ImageDetection] = Field(..., description="Image detections")
    pagination: Optional[PaginationInfo] = Field(None, description="Pagination information")

class ChannelRankingsResponse(BaseResponse):
    """Channel rankings response"""
    data: List[ChannelRanking] = Field(..., description="Channel rankings")
    metric_type: str = Field(..., description="Type of metric used for ranking")

# Error Models
class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now) 