"""
Telegram API Endpoints - Complete REST API for Telegram Groups Management
Provides endpoints for group management, posting, analytics and automation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import asyncio
import logging

# Import Telegram components
from .telegram_automator import TelegramAutomator, TelegramMessage, TelegramGroup
from .telegram_action_generator import TelegramActionGenerator
from .monitoring import TelegramMonitor

# Models for API requests/responses
class PostMessageRequest(BaseModel):
    group_id: int = Field(..., description="Telegram group ID")
    text: str = Field(..., min_length=1, max_length=4096, description="Message text")
    media: Optional[str] = Field(None, description="Media file path or URL")
    media_type: str = Field("photo", description="Media type: photo, video, document")
    buttons: Optional[List[List[Dict[str, str]]]] = Field(None, description="Inline keyboard buttons")
    parse_mode: str = Field("HTML", description="Parse mode: HTML, Markdown")
    disable_web_page_preview: bool = Field(False, description="Disable web page preview")

class ScheduleMessageRequest(BaseModel):
    group_id: int = Field(..., description="Telegram group ID")
    text: str = Field(..., min_length=1, max_length=4096, description="Message text")
    send_time: datetime = Field(..., description="When to send the message")
    media: Optional[str] = Field(None, description="Media file path or URL")
    media_type: str = Field("photo", description="Media type")
    buttons: Optional[List[List[Dict[str, str]]]] = Field(None, description="Inline keyboard buttons")

class BulkMessageRequest(BaseModel):
    group_ids: List[int] = Field(..., min_items=1, description="List of group IDs")
    text: str = Field(..., min_length=1, max_length=4096, description="Message text")
    media: Optional[str] = Field(None, description="Media file path or URL")
    delay_between: int = Field(5, ge=1, le=60, description="Delay between sends in seconds")

class GenerateContentRequest(BaseModel):
    group_id: int = Field(..., description="Target group ID")
    content_type: str = Field("promotional", description="Content type: promotional, educational, engagement")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for content generation")

class CampaignRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Campaign name")
    group_ids: List[int] = Field(..., min_items=1, description="Target group IDs")
    campaign_type: str = Field("awareness", description="Campaign type: awareness, engagement, conversion")
    duration_days: int = Field(7, ge=1, le=30, description="Campaign duration in days")
    goals: Dict[str, Any] = Field({}, description="Campaign goals and targets")

# Initialize router
router = APIRouter(prefix="/telegram", tags=["Telegram"])

# Global instances (in production, use dependency injection)
telegram_automator = TelegramAutomator()
telegram_action_generator = TelegramActionGenerator()
telegram_monitor = TelegramMonitor()

# Logger
logger = logging.getLogger(__name__)

# Dependency to get connected automator
async def get_telegram_automator() -> TelegramAutomator:
    """Get connected Telegram automator instance"""
    if not telegram_automator.is_connected:
        await telegram_automator.connect()
    return telegram_automator

# Health and Status Endpoints
@router.get("/health")
async def health_check():
    """Health check endpoint for Telegram service"""
    try:
        status = "healthy" if telegram_automator.dummy_mode else ("connected" if telegram_automator.is_connected else "disconnected")
        
        return {
            "service": "telegram",
            "status": status,
            "dummy_mode": telegram_automator.dummy_mode,
            "timestamp": datetime.now().isoformat(),
            "groups_count": len(telegram_automator.groups),
            "message_queue_size": len(telegram_automator.message_queue)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@router.get("/status")
async def get_service_status():
    """Get detailed service status and statistics"""
    try:
        automator = await get_telegram_automator()
        
        # Calculate statistics
        active_groups = len([g for g in automator.groups.values() if g.is_active])
        scheduled_messages = len([msg for msg in automator.message_queue if msg.get("status") == "scheduled"])
        
        # Get recent activity
        recent_activity = await telegram_monitor.get_recent_activity(hours=24)
        
        return {
            "connection_status": "connected" if automator.is_connected else "disconnected",
            "dummy_mode": automator.dummy_mode,
            "statistics": {
                "total_groups": len(automator.groups),
                "active_groups": active_groups,
                "scheduled_messages": scheduled_messages,
                "messages_sent_24h": recent_activity.get("messages_sent", 0),
                "avg_engagement_rate": recent_activity.get("avg_engagement", 0.15)
            },
            "service_info": {
                "max_message_length": 4096,
                "rate_limits": "30 messages per second per bot",
                "supported_media": ["photo", "video", "document", "audio"],
                "last_update": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Group Management Endpoints
@router.get("/groups", response_model=List[Dict[str, Any]])
async def get_groups():
    """Get list of all accessible Telegram groups"""
    try:
        automator = await get_telegram_automator()
        groups = await automator.get_groups()
        
        return [
            {
                "id": group.id,
                "username": group.username,
                "title": group.title,
                "members_count": group.members_count,
                "is_active": group.is_active,
                "engagement_rate": group.engagement_rate,
                "post_frequency": group.post_frequency,
                "content_types": group.content_type or [],
                "last_post_time": group.last_post_time.isoformat() if group.last_post_time else None
            }
            for group in groups
        ]
    except Exception as e:
        logger.error(f"Failed to get groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/groups/{group_id}")
async def get_group_info(group_id: int):
    """Get detailed information about a specific group"""
    try:
        automator = await get_telegram_automator()
        group = await automator.get_group_info(group_id)
        
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        return {
            "id": group.id,
            "username": group.username,
            "title": group.title,
            "members_count": group.members_count,
            "is_active": group.is_active,
            "engagement_rate": group.engagement_rate,
            "post_frequency": group.post_frequency,
            "content_types": group.content_type or [],
            "last_post_time": group.last_post_time.isoformat() if group.last_post_time else None,
            "analytics": await automator.get_group_analytics(group_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get group {group_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/groups/{group_id}/analytics")
async def get_group_analytics(
    group_id: int,
    days: int = Query(7, ge=1, le=30, description="Number of days for analytics")
):
    """Get analytics for a specific group"""
    try:
        automator = await get_telegram_automator()
        analytics = await automator.get_group_analytics(group_id, days)
        
        if "error" in analytics:
            raise HTTPException(status_code=400, detail=analytics["error"])
        
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics for group {group_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Message Management Endpoints
@router.post("/messages/send")
async def send_message(request: PostMessageRequest):
    """Send message to a Telegram group"""
    try:
        automator = await get_telegram_automator()
        
        # Create message object
        message = TelegramMessage(
            text=request.text,
            media=request.media,
            media_type=request.media_type,
            buttons=request.buttons,
            parse_mode=request.parse_mode,
            disable_web_page_preview=request.disable_web_page_preview
        )
        
        # Send message
        result = await automator.send_message(request.group_id, message)
        
        # Log activity
        await telegram_monitor.log_activity("message_sent", {
            "group_id": request.group_id,
            "success": result.get("success", False),
            "message_length": len(request.text)
        })
        
        if result.get("success"):
            return JSONResponse(content=result, status_code=200)
        else:
            # Handle specific errors
            error_type = result.get("error", "unknown")
            if error_type == "flood_wait":
                return JSONResponse(
                    content={
                        "error": "Rate limited",
                        "wait_time": result.get("wait_time"),
                        "retry_after": result.get("wait_time")
                    },
                    status_code=429
                )
            elif error_type == "no_permission":
                raise HTTPException(status_code=403, detail="No permission to post in this group")
            else:
                raise HTTPException(status_code=400, detail=result.get("error", "Failed to send message"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/schedule")
async def schedule_message(request: ScheduleMessageRequest):
    """Schedule a message for later sending"""
    try:
        automator = await get_telegram_automator()
        
        # Validate send time (must be in future)
        if request.send_time <= datetime.now():
            raise HTTPException(status_code=400, detail="Send time must be in the future")
        
        # Create message object
        message = TelegramMessage(
            text=request.text,
            media=request.media,
            media_type=request.media_type,
            buttons=request.buttons
        )
        
        # Schedule message
        result = await automator.schedule_message(request.group_id, message, request.send_time)
        
        # Log activity
        await telegram_monitor.log_activity("message_scheduled", {
            "group_id": request.group_id,
            "send_time": request.send_time.isoformat(),
            "message_length": len(request.text)
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/bulk-send")
async def bulk_send_message(request: BulkMessageRequest, background_tasks: BackgroundTasks):
    """Send message to multiple groups"""
    try:
        automator = await get_telegram_automator()
        
        # Create message object
        message = TelegramMessage(text=request.text, media=request.media)
        
        # Send to multiple groups
        result = await automator.bulk_send_message(
            request.group_ids, 
            message, 
            request.delay_between
        )
        
        # Log bulk activity
        await telegram_monitor.log_activity("bulk_message_sent", {
            "total_groups": len(request.group_ids),
            "successful_sends": result.get("successful_sends", 0),
            "failed_sends": result.get("failed_sends", 0)
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to send bulk message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/queue")
async def get_message_queue():
    """Get scheduled message queue"""
    try:
        automator = await get_telegram_automator()
        
        queue_info = []
        for i, msg in enumerate(automator.message_queue):
            queue_info.append({
                "id": i,
                "group_id": msg["group_id"],
                "text_preview": msg["message"].text[:100] + "..." if len(msg["message"].text) > 100 else msg["message"].text,
                "send_time": msg["send_time"].isoformat(),
                "status": msg["status"]
            })
        
        return {
            "total_scheduled": len(queue_info),
            "pending": len([msg for msg in queue_info if msg["status"] == "scheduled"]),
            "queue": queue_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get message queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/process-queue")
async def process_message_queue(background_tasks: BackgroundTasks):
    """Process scheduled message queue"""
    try:
        automator = await get_telegram_automator()
        
        # Process queue in background
        background_tasks.add_task(automator.process_message_queue)
        
        return {
            "status": "processing",
            "message": "Queue processing started in background",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to process queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Content Generation Endpoints
@router.post("/content/generate")
async def generate_content(request: GenerateContentRequest):
    """Generate optimized content for a specific group"""
    try:
        automator = await get_telegram_automator()
        
        # Get group context
        group = await automator.get_group_info(request.group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        group_context = {
            "id": group.id,
            "title": group.title,
            "members_count": group.members_count,
            "engagement_rate": group.engagement_rate,
            **(request.context or {})
        }
        
        # Generate content
        content = await telegram_action_generator.generate_post_content(
            group_context, 
            request.content_type
        )
        
        # Log content generation
        await telegram_monitor.log_activity("content_generated", {
            "group_id": request.group_id,
            "content_type": request.content_type,
            "estimated_engagement": content.get("estimated_engagement", 0)
        })
        
        return content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/strategy/{group_id}")
async def get_content_strategy(group_id: int):
    """Get content strategy recommendations for a group"""
    try:
        automator = await get_telegram_automator()
        
        # Get group info and analytics
        group = await automator.get_group_info(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        analytics = await automator.get_group_analytics(group_id)
        
        # Generate strategy
        strategy = await telegram_action_generator.optimize_posting_schedule(analytics)
        hashtag_strategy = await telegram_action_generator.generate_hashtag_strategy({
            "id": group.id,
            "title": group.title,
            "members_count": group.members_count,
            "engagement_rate": group.engagement_rate
        })
        
        return {
            "group_info": {
                "id": group.id,
                "title": group.title,
                "members_count": group.members_count,
                "current_engagement_rate": group.engagement_rate
            },
            "posting_strategy": strategy,
            "hashtag_strategy": hashtag_strategy,
            "content_recommendations": await telegram_action_generator.analyze_content_performance([])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get content strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Campaign Management Endpoints
@router.post("/campaigns/create")
async def create_campaign(request: CampaignRequest):
    """Create and execute a multi-group campaign"""
    try:
        automator = await get_telegram_automator()
        
        # Get group contexts
        group_contexts = []
        for group_id in request.group_ids:
            group = await automator.get_group_info(group_id)
            if group:
                group_contexts.append({
                    "id": group.id,
                    "title": group.title,
                    "members_count": group.members_count,
                    "engagement_rate": group.engagement_rate
                })
        
        if not group_contexts:
            raise HTTPException(status_code=400, detail="No valid groups found")
        
        # Generate campaign strategy
        campaign_strategy = await telegram_action_generator.generate_campaign_strategy(
            {
                "type": request.campaign_type,
                "duration": request.duration_days,
                **request.goals
            },
            group_contexts
        )
        
        # Create campaign record
        campaign_id = f"tg_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        campaign_info = {
            "id": campaign_id,
            "name": request.name,
            "type": request.campaign_type,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "target_groups": request.group_ids,
            "duration_days": request.duration_days,
            "strategy": campaign_strategy
        }
        
        # Log campaign creation
        await telegram_monitor.log_activity("campaign_created", {
            "campaign_id": campaign_id,
            "campaign_type": request.campaign_type,
            "target_groups": len(request.group_ids),
            "duration": request.duration_days
        })
        
        return campaign_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}")
async def get_campaign_status(campaign_id: str):
    """Get campaign status and performance metrics"""
    # In production, this would fetch from database
    return {
        "campaign_id": campaign_id,
        "status": "active",
        "progress": "Day 3 of 7",
        "performance": {
            "messages_sent": 45,
            "total_reach": 15000,
            "avg_engagement_rate": 0.18,
            "successful_posts": 42,
            "failed_posts": 3
        },
        "next_scheduled": datetime.now() + timedelta(hours=2)
    }

# Monitoring and Analytics Endpoints
@router.get("/monitoring/mentions")
async def monitor_mentions(keywords: List[str] = Query(..., description="Keywords to monitor")):
    """Monitor groups for specific keywords or mentions"""
    try:
        automator = await get_telegram_automator()
        mentions = await automator.monitor_mentions(keywords)
        
        return {
            "keywords": keywords,
            "total_mentions": len(mentions),
            "mentions": mentions,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to monitor mentions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview")
async def get_analytics_overview(
    days: int = Query(7, ge=1, le=30, description="Number of days for analytics")
):
    """Get overall analytics across all groups"""
    try:
        automator = await get_telegram_automator()
        
        # Get analytics for all groups
        all_analytics = []
        for group_id in automator.groups.keys():
            analytics = await automator.get_group_analytics(group_id, days)
            if "error" not in analytics:
                analytics["group_info"] = {
                    "id": group_id,
                    "title": automator.groups[group_id].title,
                    "members_count": automator.groups[group_id].members_count
                }
                all_analytics.append(analytics)
        
        # Calculate aggregate statistics
        total_messages = sum(a.get("total_messages", 0) for a in all_analytics)
        total_reach = sum(a["group_info"]["members_count"] for a in all_analytics)
        avg_engagement = sum(a.get("engagement_rate", 0) for a in all_analytics) / len(all_analytics) if all_analytics else 0
        
        return {
            "period_days": days,
            "total_groups": len(all_analytics),
            "aggregate_stats": {
                "total_messages": total_messages,
                "total_potential_reach": total_reach,
                "average_engagement_rate": round(avg_engagement, 3),
                "active_groups": len([a for a in all_analytics if a.get("total_messages", 0) > 0])
            },
            "top_performing_groups": sorted(
                all_analytics, 
                key=lambda x: x.get("engagement_rate", 0), 
                reverse=True
            )[:5],
            "group_analytics": all_analytics
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/performance")
async def get_performance_metrics(
    group_id: Optional[int] = Query(None, description="Specific group ID, or all groups if not provided"),
    metric_type: str = Query("engagement", description="Metric type: engagement, reach, growth")
):
    """Get detailed performance metrics"""
    try:
        # This would implement detailed performance analysis
        # For now, return sample data
        return {
            "metric_type": metric_type,
            "group_id": group_id,
            "time_series": [
                {"date": "2024-01-10", "value": 0.15},
                {"date": "2024-01-11", "value": 0.18},
                {"date": "2024-01-12", "value": 0.16},
                {"date": "2024-01-13", "value": 0.22},
                {"date": "2024-01-14", "value": 0.19},
            ],
            "summary": {
                "current_value": 0.19,
                "trend": "improving",
                "change_percentage": 12.5,
                "benchmark_comparison": "above_average"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility Endpoints
@router.post("/connect")
async def connect_telegram():
    """Connect to Telegram (useful for manual reconnection)"""
    try:
        success = await telegram_automator.connect()
        
        if success:
            return {
                "status": "connected",
                "groups_loaded": len(telegram_automator.groups),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to connect to Telegram")
            
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disconnect")
async def disconnect_telegram():
    """Disconnect from Telegram"""
    try:
        await telegram_automator.disconnect()
        
        return {
            "status": "disconnected",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to disconnect: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/limits")
async def get_rate_limits():
    """Get current rate limits and usage"""
    return {
        "telegram_limits": {
            "messages_per_second": 30,
            "messages_per_minute": 20,
            "bulk_messages_per_second": 1,
            "group_join_limit": "20 per day"
        },
        "current_usage": {
            "messages_sent_last_minute": 5,
            "queue_size": len(telegram_automator.message_queue),
            "active_connections": 1 if telegram_automator.is_connected else 0
        },
        "recommendations": [
            "Use delays between bulk messages",
            "Monitor queue size regularly",
            "Respect flood wait errors",
            "Implement exponential backoff"
        ]
    }

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import logging

from config.app_settings import is_dummy_mode
from .telegram_automator import TelegramAutomator, create_telegram_automator
from .telegram_action_generator import TelegramActionGenerator, create_telegram_action_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["Telegram"])

# Pydantic models for request/response
class TelegramGroupCreate(BaseModel):
    group_link: str = Field(..., description="Telegram group link or username")
    auto_join: bool = Field(True, description="Automatically join the group")

class TelegramMessage(BaseModel):
    group_id: int = Field(..., description="Target group ID")
    text: str = Field(..., description="Message text")
    reply_to: Optional[int] = Field(None, description="Message ID to reply to")
    parse_mode: str = Field("markdown", description="Message parse mode")

class TelegramBulkMessage(BaseModel):
    group_ids: List[int] = Field(..., description="List of target group IDs")
    text: str = Field(..., description="Message text")
    delay_between_posts: int = Field(60, description="Delay between posts in seconds")

class TelegramScheduledMessage(BaseModel):
    group_id: int = Field(..., description="Target group ID")
    text: str = Field(..., description="Message text")
    schedule_time: datetime = Field(..., description="When to send the message")

class TelegramAutoReply(BaseModel):
    group_id: int = Field(..., description="Target group ID")
    keywords: List[str] = Field(..., description="Keywords to trigger reply")
    reply_text: str = Field(..., description="Auto-reply message")
    enabled: bool = Field(True, description="Enable/disable auto-reply")

class TelegramOptimizationRequest(BaseModel):
    target_metrics: Optional[Dict[str, float]] = Field(None, description="Target performance metrics")
    group_ids: Optional[List[int]] = Field(None, description="Specific groups to optimize")

class TelegramAnalyticsRequest(BaseModel):
    group_id: Optional[int] = Field(None, description="Specific group ID (None for all groups)")
    days: int = Field(7, description="Number of days to analyze")

# Dependency injection
async def get_telegram_automator() -> TelegramAutomator:
    """Get Telegram automator instance"""
    return create_telegram_automator()

async def get_telegram_action_generator(
    automator: TelegramAutomator = Depends(get_telegram_automator)
) -> TelegramActionGenerator:
    """Get Telegram action generator instance"""
    return create_telegram_action_generator(telegram_automator=automator)

# Health check
@router.get("/health")
async def health_check():
    """Check Telegram service health"""
    return {
        "status": "healthy",
        "service": "telegram",
        "dummy_mode": is_dummy_mode(),
        "timestamp": datetime.now().isoformat()
    }

# Group management endpoints
@router.get("/groups")
async def get_groups(
    limit: int = 50,
    automator: TelegramAutomator = Depends(get_telegram_automator)
):
    """Get list of user's Telegram groups"""
    try:
        if not automator.is_connected:
            await automator.connect()
        
        groups = await automator.get_groups(limit=limit)
        
        return {
            "groups": [
                {
                    "id": group.id,
                    "title": group.title,
                    "username": group.username,
                    "members_count": group.members_count,
                    "description": group.description,
                    "is_channel": group.is_channel,
                    "is_group": group.is_group,
                    "is_supergroup": group.is_supergroup,
                    "invite_link": group.invite_link
                }
                for group in groups
            ],
            "total": len(groups)
        }
        
    except Exception as e:
        logger.error(f"Failed to get groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/groups/join")
async def join_group(
    group_data: TelegramGroupCreate,
    automator: TelegramAutomator = Depends(get_telegram_automator)
):
    """Join a Telegram group"""
    try:
        if not automator.is_connected:
            await automator.connect()
        
        success = await automator.join_group(group_data.group_link)
        
        if success:
            return {
                "status": "success",
                "message": f"Successfully joined group: {group_data.group_link}",
                "group_link": group_data.group_link
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to join group")
            
    except Exception as e:
        logger.error(f"Failed to join group {group_data.group_link}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/groups/{group_id}")
async def leave_group(
    group_id: int,
    automator: TelegramAutomator = Depends(get_telegram_automator)
):
    """Leave a Telegram group"""
    try:
        if not automator.is_connected:
            await automator.connect()
        
        success = await automator.leave_group(group_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Successfully left group: {group_id}",
                "group_id": group_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to leave group")
            
    except Exception as e:
        logger.error(f"Failed to leave group {group_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Messaging endpoints
@router.post("/messages/send")
async def send_message(
    message_data: TelegramMessage,
    automator: TelegramAutomator = Depends(get_telegram_automator)
):
    """Send a message to a Telegram group"""
    try:
        if not automator.is_connected:
            await automator.connect()
        
        message = await automator.send_message(
            group_id=message_data.group_id,
            text=message_data.text,
            reply_to=message_data.reply_to,
            parse_mode=message_data.parse_mode
        )
        
        if message:
            return {
                "status": "success",
                "message_id": message.id,
                "group_id": message.group_id,
                "text": message.text[:50] + "..." if len(message.text) > 50 else message.text,
                "sent_at": message.date.isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to send message")
            
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/bulk")
async def send_bulk_message(
    bulk_data: TelegramBulkMessage,
    background_tasks: BackgroundTasks,
    automator: TelegramAutomator = Depends(get_telegram_automator)
):
    """Send the same message to multiple groups"""
    try:
        if not automator.is_connected:
            await automator.connect()
        
        # Execute bulk posting in background
        background_tasks.add_task(
            _execute_bulk_post,
            automator,
            bulk_data.group_ids,
            bulk_data.text,
            bulk_data.delay_between_posts
        )
        
        return {
            "status": "success",
            "message": f"Bulk message queued for {len(bulk_data.group_ids)} groups",
            "group_count": len(bulk_data.group_ids),
            "estimated_completion": datetime.now() + timedelta(
                seconds=len(bulk_data.group_ids) * bulk_data.delay_between_posts
            )
        }
        
    except Exception as e:
        logger.error(f"Failed to queue bulk message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/schedule")
async def schedule_message(
    schedule_data: TelegramScheduledMessage,
    background_tasks: BackgroundTasks,
    automator: TelegramAutomator = Depends(get_telegram_automator)
):
    """Schedule a message for future sending"""
    try:
        if not automator.is_connected:
            await automator.connect()
        
        # Schedule message in background
        background_tasks.add_task(
            automator.schedule_post,
            schedule_data.group_id,
            schedule_data.text,
            schedule_data.schedule_time
        )
        
        return {
            "status": "success",
            "message": "Message scheduled successfully",
            "group_id": schedule_data.group_id,
            "schedule_time": schedule_data.schedule_time.isoformat(),
            "text_preview": schedule_data.text[:50] + "..." if len(schedule_data.text) > 50 else schedule_data.text
        }
        
    except Exception as e:
        logger.error(f"Failed to schedule message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/groups/{group_id}/messages")
async def get_group_messages(
    group_id: int,
    limit: int = 100,
    days: int = 7,
    automator: TelegramAutomator = Depends(get_telegram_automator)
):
    """Get recent messages from a group"""
    try:
        if not automator.is_connected:
            await automator.connect()
        
        offset_date = datetime.now() - timedelta(days=days)
        messages = await automator.get_group_messages(
            group_id=group_id,
            limit=limit,
            offset_date=offset_date
        )
        
        return {
            "group_id": group_id,
            "messages": [
                {
                    "id": msg.id,
                    "text": msg.text,
                    "date": msg.date.isoformat(),
                    "sender_id": msg.sender_id,
                    "views": msg.views,
                    "forwards": msg.forwards
                }
                for msg in messages
            ],
            "total": len(messages),
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Failed to get messages from group {group_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Automation endpoints
@router.post("/automation/auto-reply")
async def setup_auto_reply(
    auto_reply_data: TelegramAutoReply,
    automator: TelegramAutomator = Depends(get_telegram_automator)
):
    """Set up automatic replies for specific keywords"""
    try:
        if not automator.is_connected:
            await automator.connect()
        
        await automator.auto_reply(
            group_id=auto_reply_data.group_id,
            keywords=auto_reply_data.keywords,
            reply_text=auto_reply_data.reply_text,
            enabled=auto_reply_data.enabled
        )
        
        return {
            "status": "success",
            "message": "Auto-reply configured successfully",
            "group_id": auto_reply_data.group_id,
            "keywords": auto_reply_data.keywords,
            "enabled": auto_reply_data.enabled
        }
        
    except Exception as e:
        logger.error(f"Failed to setup auto-reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@router.get("/analytics/groups/{group_id}")
async def get_group_analytics(
    group_id: int,
    days: int = 7,
    action_generator: TelegramActionGenerator = Depends(get_telegram_action_generator)
):
    """Get analytics for a specific group"""
    try:
        analytics = await action_generator.analyze_group_performance(group_id, days)
        
        return {
            "group_id": analytics.group_id,
            "group_name": analytics.group_name,
            "members_count": analytics.members_count,
            "messages_count": analytics.messages_count,
            "avg_engagement_rate": analytics.avg_engagement_rate,
            "peak_activity_hours": analytics.peak_activity_hours,
            "top_keywords": analytics.top_keywords,
            "sentiment_score": analytics.sentiment_score,
            "growth_rate": analytics.growth_rate,
            "analysis_period": f"{days} days"
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics for group {group_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview")
async def get_analytics_overview(
    days: int = 7,
    automator: TelegramAutomator = Depends(get_telegram_automator)
):
    """Get overall analytics for all groups"""
    try:
        analytics = automator.get_engagement_analytics(days=days)
        
        return {
            "overview": analytics,
            "analysis_period": f"{days} days",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ML-driven optimization endpoints
@router.post("/optimization/generate-actions")
async def generate_optimization_actions(
    request: TelegramOptimizationRequest,
    action_generator: TelegramActionGenerator = Depends(get_telegram_action_generator)
):
    """Generate ML-driven optimization actions"""
    try:
        actions = await action_generator.generate_optimization_actions(
            target_metrics=request.target_metrics
        )
        
        return {
            "actions": [
                {
                    "action_type": action.action_type,
                    "target_group": action.target_group,
                    "parameters": action.parameters,
                    "priority": action.priority,
                    "expected_impact": action.expected_impact,
                    "reasoning": action.reasoning
                }
                for action in actions
            ],
            "total_actions": len(actions),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate optimization actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimization/content-recommendations")
async def get_content_recommendations(
    group_ids: List[int],
    content_themes: Optional[List[str]] = None,
    action_generator: TelegramActionGenerator = Depends(get_telegram_action_generator)
):
    """Get ML-driven content recommendations"""
    try:
        recommendations = await action_generator.generate_content_recommendations(
            group_ids=group_ids,
            content_themes=content_themes
        )
        
        return {
            "recommendations": [
                {
                    "content_type": rec.content_type,
                    "suggested_text": rec.suggested_text,
                    "optimal_timing": rec.optimal_timing.isoformat(),
                    "target_groups": rec.target_groups,
                    "expected_engagement": rec.expected_engagement,
                    "hashtags": rec.hashtags,
                    "reasoning": rec.reasoning
                }
                for rec in recommendations
            ],
            "total_recommendations": len(recommendations),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get content recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimization/insights")
async def get_performance_insights(
    action_generator: TelegramActionGenerator = Depends(get_telegram_action_generator)
):
    """Get ML-driven performance insights"""
    try:
        insights = action_generator.get_performance_insights()
        
        return {
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility endpoints
@router.get("/groups/{group_id}/metrics/{message_id}")
async def get_message_metrics(
    group_id: int,
    message_id: int,
    automator: TelegramAutomator = Depends(get_telegram_automator)
):
    """Get metrics for a specific message"""
    try:
        if not automator.is_connected:
            await automator.connect()
        
        metrics = await automator.get_post_metrics(group_id, message_id)
        
        if metrics:
            return {
                "message_id": metrics.message_id,
                "group_id": metrics.group_id,
                "views": metrics.views,
                "forwards": metrics.forwards,
                "replies": metrics.replies,
                "reactions": metrics.reactions,
                "engagement_rate": metrics.engagement_rate,
                "timestamp": metrics.timestamp.isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Metrics not found")
            
    except Exception as e:
        logger.error(f"Failed to get metrics for {group_id}/{message_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def _execute_bulk_post(
    automator: TelegramAutomator,
    group_ids: List[int],
    text: str,
    delay: int
):
    """Execute bulk posting in background"""
    try:
        results = await automator.bulk_post(group_ids, text, delay)
        success_count = sum(1 for success in results.values() if success)
        
        logger.info(f"Bulk post completed: {success_count}/{len(group_ids)} successful")
        
    except Exception as e:
        logger.error(f"Bulk post failed: {e}")

# Export router
__all__ = ["router"]