"""
Analytics API routes for FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.api.database import get_db, DatabaseManager
from app.api.crud import AnalyticsCRUD
from app.api.schemas import (
    ChannelsResponse, ChannelActivityResponse, MessagesResponse,
    SearchResponse, TopProductsResponse, AnalyticsResponse,
    ImageDetectionsResponse, ChannelRankingsResponse,
    SearchRequest, ChannelActivityRequest, TopProductsRequest,
    PaginationInfo, ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analytics"])

def get_crud(db: DatabaseManager = Depends(get_db)) -> AnalyticsCRUD:
    """Dependency to get CRUD instance"""
    return AnalyticsCRUD(db)

@router.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analytics-api"}

@router.get("/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics_summary(crud: AnalyticsCRUD = Depends(get_crud)):
    """Get overall analytics summary"""
    try:
        summary = crud.get_analytics_summary()
        return AnalyticsResponse(
            message="Analytics summary retrieved successfully",
            data=summary
        )
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics summary")

@router.get("/channels", response_model=ChannelsResponse)
async def get_channels(
    limit: int = Query(50, ge=1, le=100, description="Number of channels to return"),
    offset: int = Query(0, ge=0, description="Number of channels to skip"),
    crud: AnalyticsCRUD = Depends(get_crud)
):
    """Get all channels with analytics"""
    try:
        channels = crud.get_channels(limit=limit, offset=offset)
        total = crud.get_count("marts.dim_channels")
        
        pagination = PaginationInfo(
            page=(offset // limit) + 1,
            size=limit,
            total=total,
            pages=(total + limit - 1) // limit
        )
        
        return ChannelsResponse(
            message="Channels retrieved successfully",
            data=channels,
            pagination=pagination
        )
    except Exception as e:
        logger.error(f"Error getting channels: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve channels")

@router.get("/channels/{channel_name}", response_model=ChannelActivityResponse)
async def get_channel_info(
    channel_name: str,
    crud: AnalyticsCRUD = Depends(get_crud)
):
    """Get specific channel information"""
    try:
        channel_info = crud.get_channel_by_name(channel_name)
        if not channel_info:
            raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found")
        
        return ChannelActivityResponse(
            message=f"Channel '{channel_name}' information retrieved successfully",
            data=[],  # Activity data would be empty for this endpoint
            channel_info=channel_info
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel info for {channel_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve channel information")

@router.get("/channels/{channel_name}/activity", response_model=ChannelActivityResponse)
async def get_channel_activity(
    channel_name: str,
    date_from: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD)"),
    group_by: str = Query("day", regex="^(day|week|month)$", description="Grouping period"),
    crud: AnalyticsCRUD = Depends(get_crud)
):
    """Get channel activity over time"""
    try:
        # Verify channel exists
        channel_info = crud.get_channel_by_name(channel_name)
        if not channel_info:
            raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found")
        
        activity = crud.get_channel_activity(
            channel_name=channel_name,
            date_from=date_from,
            date_to=date_to,
            group_by=group_by
        )
        
        return ChannelActivityResponse(
            message=f"Channel '{channel_name}' activity retrieved successfully",
            data=activity,
            channel_info=channel_info
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel activity for {channel_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve channel activity")

@router.get("/channels/{channel_name}/messages", response_model=MessagesResponse)
async def get_channel_messages(
    channel_name: str,
    limit: int = Query(50, ge=1, le=100, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    crud: AnalyticsCRUD = Depends(get_crud)
):
    """Get messages for a specific channel"""
    try:
        # Verify channel exists
        channel_info = crud.get_channel_by_name(channel_name)
        if not channel_info:
            raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found")
        
        messages = crud.get_messages_by_channel(
            channel_name=channel_name,
            limit=limit,
            offset=offset
        )
        
        total = crud.get_count("marts.fct_messages", {"channel_name": channel_name})
        
        pagination = PaginationInfo(
            page=(offset // limit) + 1,
            size=limit,
            total=total,
            pages=(total + limit - 1) // limit
        )
        
        return MessagesResponse(
            message=f"Channel '{channel_name}' messages retrieved successfully",
            data=messages,
            pagination=pagination
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel messages for {channel_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve channel messages")

@router.get("/search/messages", response_model=SearchResponse)
async def search_messages(
    query: str = Query(..., min_length=1, max_length=100, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    channel_filter: Optional[str] = Query(None, description="Filter by specific channel"),
    date_from: Optional[datetime] = Query(None, description="Start date filter"),
    date_to: Optional[datetime] = Query(None, description="End date filter"),
    medical_only: bool = Query(False, description="Filter medical messages only"),
    price_only: bool = Query(False, description="Filter price-related messages only"),
    crud: AnalyticsCRUD = Depends(get_crud)
):
    """Search messages with relevance scoring"""
    try:
        results = crud.search_messages(
            query=query,
            limit=limit,
            offset=offset,
            channel_filter=channel_filter,
            date_from=date_from,
            date_to=date_to,
            medical_only=medical_only,
            price_only=price_only
        )
        
        # Get total count for this search (simplified)
        total_results = len(results)  # This is approximate since we're limiting
        
        return SearchResponse(
            message="Message search completed successfully",
            data=results,
            total_results=total_results,
            query=query
        )
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to search messages")

@router.get("/reports/top-products", response_model=TopProductsResponse)
async def get_top_products(
    limit: int = Query(10, ge=1, le=100, description="Number of top products"),
    channel_filter: Optional[str] = Query(None, description="Filter by specific channel"),
    date_from: Optional[datetime] = Query(None, description="Start date filter"),
    date_to: Optional[datetime] = Query(None, description="End date filter"),
    medical_only: bool = Query(False, description="Filter medical products only"),
    crud: AnalyticsCRUD = Depends(get_crud)
):
    """Get most frequently mentioned products"""
    try:
        products = crud.get_top_products(
            limit=limit,
            channel_filter=channel_filter,
            date_from=date_from,
            date_to=date_to,
            medical_only=medical_only
        )
        
        return TopProductsResponse(
            message="Top products retrieved successfully",
            data=products,
            total_products=len(products)
        )
    except Exception as e:
        logger.error(f"Error getting top products: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve top products")

@router.get("/reports/channel-rankings", response_model=ChannelRankingsResponse)
async def get_channel_rankings(
    metric: str = Query("message_count", description="Metric to rank by"),
    limit: int = Query(10, ge=1, le=100, description="Number of top channels"),
    crud: AnalyticsCRUD = Depends(get_crud)
):
    """Get channel rankings by various metrics"""
    try:
        rankings = crud.get_channel_rankings(metric=metric, limit=limit)
        
        return ChannelRankingsResponse(
            message="Channel rankings retrieved successfully",
            data=rankings,
            metric_type=metric
        )
    except Exception as e:
        logger.error(f"Error getting channel rankings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve channel rankings")

@router.get("/image-detections", response_model=ImageDetectionsResponse)
async def get_image_detections(
    channel_name: Optional[str] = Query(None, description="Filter by channel name"),
    object_class: Optional[str] = Query(None, description="Filter by object class"),
    medical_only: bool = Query(False, description="Filter medical objects only"),
    limit: int = Query(50, ge=1, le=100, description="Number of detections to return"),
    offset: int = Query(0, ge=0, description="Number of detections to skip"),
    crud: AnalyticsCRUD = Depends(get_crud)
):
    """Get image detections with filters"""
    try:
        detections = crud.get_image_detections(
            channel_name=channel_name,
            object_class=object_class,
            medical_only=medical_only,
            limit=limit,
            offset=offset
        )
        
        # Get total count (simplified)
        total_detections = len(detections)  # This is approximate since we're limiting
        
        pagination = PaginationInfo(
            page=(offset // limit) + 1,
            size=limit,
            total=total_detections,
            pages=(total_detections + limit - 1) // limit
        )
        
        return ImageDetectionsResponse(
            message="Image detections retrieved successfully",
            data=detections,
            pagination=pagination
        )
    except Exception as e:
        logger.error(f"Error getting image detections: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve image detections")

@router.get("/reports/medical-insights", response_model=dict)
async def get_medical_insights(crud: AnalyticsCRUD = Depends(get_crud)):
    """Get medical insights and trends"""
    try:
        # Get analytics summary
        summary = crud.get_analytics_summary()
        
        # Get top medical channels
        medical_channels = crud.get_channel_rankings(metric="medical_messages", limit=5)
        
        # Get top medical products
        medical_products = crud.get_top_products(limit=10, medical_only=True)
        
        # Get recent medical messages
        recent_medical = crud.search_messages(
            query="medicine",
            limit=10,
            medical_only=True
        )
        
        insights = {
            "summary": {
                "total_medical_messages": summary.total_medical_messages,
                "medical_content_percentage": summary.medical_content_percentage,
                "total_channels": summary.total_channels
            },
            "top_medical_channels": medical_channels,
            "top_medical_products": medical_products,
            "recent_medical_messages": recent_medical
        }
        
        return {
            "success": True,
            "message": "Medical insights retrieved successfully",
            "data": insights,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error getting medical insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve medical insights") 