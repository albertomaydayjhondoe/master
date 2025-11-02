"""
API Gateway for Telegram Bot System
Provides REST API endpoints for monitoring and control.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime

from main_bot import TelegramBot
from core.metrics_collector import MetricsCollector
from core.priority_engine import PriorityEngine
from database.models import User, EngagementTask, Metrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Telegram Bot API",
    description="API for managing the Telegram engagement exchange bot",
    version="1.0.0"
)

# Global bot instance
bot_instance: Optional[TelegramBot] = None

# Pydantic models
class SystemStatus(BaseModel):
    status: str
    uptime: str
    modules: Dict[str, Any]
    performance: Dict[str, Any]
    active_tasks: int
    managed_accounts: int

class TaskRequest(BaseModel):
    task_type: str
    platform: str
    target_id: str
    priority: str = "medium"
    user_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class UserMetricsResponse(BaseModel):
    user_id: int
    total_engagements: int
    successful_exchanges: int
    platform_breakdown: Dict[str, int]
    activity_score: float
    last_activity: datetime

class PriorityCalculationRequest(BaseModel):
    content_type: str
    engagement_rate: float
    platform: str
    author_followers: int
    additional_factors: Optional[Dict[str, Any]] = None

class EngagementExchangeRequest(BaseModel):
    user_id: int
    platform: str
    content_url: str
    exchange_type: str  # 'like', 'follow', 'comment'
    target_engagement: int
    message: Optional[str] = None

# Dependency to get bot instance
async def get_bot() -> TelegramBot:
    global bot_instance
    if bot_instance is None:
        raise HTTPException(status_code=503, detail="Bot is not initialized")
    return bot_instance

@app.on_event("startup")
async def startup_event():
    """Initialize the bot on startup."""
    global bot_instance
    try:
        bot_instance = TelegramBot()
        # Start bot in background
        asyncio.create_task(bot_instance.start())
        logger.info("Bot initialized and started")
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global bot_instance
    if bot_instance:
        await bot_instance.stop()
        logger.info("Bot stopped")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {"message": "Telegram Bot API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/status", response_model=SystemStatus)
async def get_system_status(bot: TelegramBot = Depends(get_bot)):
    """Get comprehensive system status."""
    try:
        status = await bot.get_system_status()
        return SystemStatus(**status)
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks")
async def create_task(
    task_request: TaskRequest,
    bot: TelegramBot = Depends(get_bot)
):
    """Create a new engagement task."""
    try:
        from core.executor_module import Task, TaskPriority
        
        # Convert priority string to enum
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.URGENT
        }
        
        task = Task(
            task_type=task_request.task_type,
            platform=task_request.platform,
            target_id=task_request.target_id,
            priority=priority_map.get(task_request.priority.lower(), TaskPriority.MEDIUM),
            user_id=task_request.user_id,
            metadata=task_request.metadata or {}
        )
        
        await bot.executor.add_task(task)
        
        return {
            "message": "Task created successfully",
            "task_id": task.task_id,
            "status": "queued"
        }
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def get_tasks(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    user_id: Optional[int] = None,
    bot: TelegramBot = Depends(get_bot)
):
    """Get tasks with optional filtering."""
    try:
        tasks = await bot.executor.get_tasks(
            status=status,
            platform=platform,
            user_id=user_id
        )
        
        return {
            "tasks": [task.to_dict() for task in tasks],
            "count": len(tasks)
        }
        
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/metrics", response_model=UserMetricsResponse)
async def get_user_metrics(
    user_id: int,
    bot: TelegramBot = Depends(get_bot)
):
    """Get metrics for a specific user."""
    try:
        metrics = await bot.metrics_collector.get_user_metrics(user_id)
        
        return UserMetricsResponse(
            user_id=user_id,
            total_engagements=metrics.get('total_engagements', 0),
            successful_exchanges=metrics.get('successful_exchanges', 0),
            platform_breakdown=metrics.get('platform_breakdown', {}),
            activity_score=metrics.get('activity_score', 0.0),
            last_activity=metrics.get('last_activity', datetime.now())
        )
        
    except Exception as e:
        logger.error(f"Error getting user metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/priority/calculate")
async def calculate_priority(
    request: PriorityCalculationRequest,
    bot: TelegramBot = Depends(get_bot)
):
    """Calculate priority for content."""
    try:
        factors = {
            'content_type': request.content_type,
            'engagement_rate': request.engagement_rate,
            'platform': request.platform,
            'author_followers': request.author_followers
        }
        
        if request.additional_factors:
            factors.update(request.additional_factors)
        
        priority_score = await bot.priority_engine.calculate_priority(factors)
        
        return {
            "priority_score": priority_score,
            "priority_level": "high" if priority_score > 0.8 else "medium" if priority_score > 0.5 else "low",
            "factors_used": factors
        }
        
    except Exception as e:
        logger.error(f"Error calculating priority: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/exchange")
async def request_engagement_exchange(
    request: EngagementExchangeRequest,
    bot: TelegramBot = Depends(get_bot)
):
    """Request an engagement exchange."""
    try:
        # Create exchange request
        exchange_data = {
            'user_id': request.user_id,
            'platform': request.platform,
            'content_url': request.content_url,
            'exchange_type': request.exchange_type,
            'target_engagement': request.target_engagement,
            'message': request.message
        }
        
        # Process the exchange request
        result = await bot._process_exchange_request_api(exchange_data)
        
        return {
            "message": "Exchange request processed",
            "exchange_id": result['exchange_id'],
            "estimated_completion": result['estimated_completion'],
            "tasks_created": result['tasks_created']
        }
        
    except Exception as e:
        logger.error(f"Error processing exchange request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/system")
async def get_system_metrics(bot: TelegramBot = Depends(get_bot)):
    """Get system-wide metrics."""
    try:
        metrics = await bot.metrics_collector.get_system_metrics()
        
        return {
            "daily_stats": metrics.get('daily_stats', {}),
            "platform_performance": metrics.get('platform_performance', {}),
            "user_activity": metrics.get('user_activity', {}),
            "task_completion_rate": metrics.get('task_completion_rate', 0.0),
            "average_response_time": metrics.get('average_response_time', 0.0)
        }
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/health")
async def get_account_health(bot: TelegramBot = Depends(get_bot)):
    """Get health status of all managed accounts."""
    try:
        health_report = await bot.account_manager.check_all_accounts_health()
        
        return {
            "overall_health": "healthy",  # Could be calculated from individual accounts
            "accounts": health_report,
            "total_accounts": sum(len(accounts) for accounts in health_report.values()),
            "healthy_accounts": sum(
                1 for accounts in health_report.values()
                for account in accounts.values()
                if account.get('status') == 'healthy'
            )
        }
        
    except Exception as e:
        logger.error(f"Error getting account health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/accounts/{platform}/rotate")
async def rotate_platform_accounts(
    platform: str,
    bot: TelegramBot = Depends(get_bot)
):
    """Rotate accounts for a specific platform."""
    try:
        result = await bot.account_manager.rotate_platform_accounts(platform)
        
        return {
            "message": f"Account rotation completed for {platform}",
            "rotated_accounts": result['rotated_count'],
            "new_active_account": result['new_active_account']
        }
        
    except Exception as e:
        logger.error(f"Error rotating accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/viral/opportunities")
async def get_viral_opportunities(
    platform: Optional[str] = None,
    limit: int = 10,
    bot: TelegramBot = Depends(get_bot)
):
    """Get current viral opportunities."""
    try:
        opportunities = await bot.listener.get_viral_opportunities(
            platform=platform,
            limit=limit
        )
        
        return {
            "opportunities": [opp.to_dict() for opp in opportunities],
            "count": len(opportunities),
            "platforms": list(set(opp.platform for opp in opportunities))
        }
        
    except Exception as e:
        logger.error(f"Error getting viral opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/message/generate")
async def generate_message(
    message_type: str,
    context: Dict[str, Any],
    bot: TelegramBot = Depends(get_bot)
):
    """Generate a message using the message generator."""
    try:
        message = await bot.message_generator.generate_message(message_type, context)
        
        return {
            "message": message,
            "type": message_type,
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error generating message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_recent_logs(
    level: str = "INFO",
    lines: int = 100
):
    """Get recent log entries."""
    try:
        # This would read from log files in production
        return {
            "message": "Log endpoint not implemented in dummy mode",
            "level": level,
            "lines_requested": lines
        }
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)