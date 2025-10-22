"""
Bidirectional API Gateway
API interface for managing the complete bidirectional ML flow
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import traceback
try:
    from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    print("⚠️ FastAPI not available - API gateway will not start")
    FASTAPI_AVAILABLE = False
    # Create dummy classes for type hints
    class BaseModel:
        pass
    class Field:
        def __init__(self, *args, **kwargs):
            pass

# Import ML components
try:
    from .bidirectional_engine import BidirectionalMLEngine, create_bidirectional_ml_engine
    from .data_acquisition import RealTimeDataAcquisitionEngine, create_data_acquisition_engine
    from .cloud_processing import CloudMLProcessingPipeline, create_cloud_processing_pipeline
    from .action_generation import UniversalActionGenerationSystem, create_action_generation_system
    from .platform_toggle import UniversalPlatformToggleSystem, create_platform_toggle_system, PlatformMode, PlatformCapability
except ImportError:
    import sys
    sys.path.append('/workspaces/master')
    from ml_core.bidirectional_engine import BidirectionalMLEngine, create_bidirectional_ml_engine
    from ml_core.data_acquisition import RealTimeDataAcquisitionEngine, create_data_acquisition_engine
    from ml_core.cloud_processing import CloudMLProcessingPipeline, create_cloud_processing_pipeline
    from ml_core.action_generation import UniversalActionGenerationSystem, create_action_generation_system
    from ml_core.platform_toggle import UniversalPlatformToggleSystem, create_platform_toggle_system, PlatformMode, PlatformCapability

# Pydantic models for API requests/responses
class PlatformActivationRequest(BaseModel):
    platform_id: str = Field(..., description="Platform identifier")
    mode: str = Field(default="dummy", description="Platform mode: dummy, testing, production")
    capabilities: List[str] = Field(default=[], description="Capabilities to enable")

class CapabilityRequest(BaseModel):
    platform_id: str = Field(..., description="Platform identifier")
    capability: str = Field(..., description="Capability to enable/disable")

class GlobalModeRequest(BaseModel):
    mode: str = Field(..., description="Global mode: dummy, testing, production")

class ActionExecutionRequest(BaseModel):
    action_id: str = Field(..., description="Action ID to execute")
    force_execute: bool = Field(default=False, description="Force immediate execution")

class SystemConfigRequest(BaseModel):
    config: Dict[str, Any] = Field(..., description="System configuration parameters")

class DataCollectionRequest(BaseModel):
    platforms: List[str] = Field(default=[], description="Platforms to collect data from")
    duration_hours: int = Field(default=24, description="Collection duration in hours")
    metrics: List[str] = Field(default=[], description="Specific metrics to collect")

class MLProcessingRequest(BaseModel):
    data_source: str = Field(..., description="Data source identifier")
    model_types: List[str] = Field(default=[], description="ML models to use")
    priority: str = Field(default="medium", description="Processing priority")

# Response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    status: str
    uptime: float
    components: Dict[str, str]
    metrics: Dict[str, float]
    timestamp: datetime = Field(default_factory=datetime.now)

class MetricsResponse(BaseModel):
    system_metrics: Dict[str, Any]
    platform_metrics: Dict[str, Any]
    ml_metrics: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

# Global instances (initialized on startup)
bidirectional_engine: Optional[BidirectionalMLEngine] = None
data_acquisition_engine: Optional[RealTimeDataAcquisitionEngine] = None
cloud_processing_pipeline: Optional[CloudMLProcessingPipeline] = None
action_generation_system: Optional[UniversalActionGenerationSystem] = None
platform_toggle_system: Optional[UniversalPlatformToggleSystem] = None

# FastAPI application (only if available)
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Bidirectional ML API Gateway",
        description="API interface for managing complete bidirectional ML social media automation system",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
else:
    app = None

# CORS middleware (only if FastAPI available)
if FASTAPI_AVAILABLE and app:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Global state tracking
system_state = {
    "startup_time": None,
    "is_initialized": False,
    "components_status": {},
    "last_health_check": None
}

# Logging setup
logger = logging.getLogger(__name__)

# Helper functions
async def get_system_health():
    """Get comprehensive system health status"""
    if not system_state["is_initialized"]:
        return {"status": "initializing", "components": {}}
    
    components = {}
    
    # Check bidirectional engine
    if bidirectional_engine:
        components["bidirectional_engine"] = "healthy" if bidirectional_engine.is_running else "inactive"
    
    # Check data acquisition
    if data_acquisition_engine:
        components["data_acquisition"] = "healthy" if data_acquisition_engine.is_collecting else "inactive"
    
    # Check cloud processing
    if cloud_processing_pipeline:
        components["cloud_processing"] = "healthy" if cloud_processing_pipeline.is_processing else "inactive"
    
    # Check action generation
    if action_generation_system:
        components["action_generation"] = "healthy" if action_generation_system.is_executing else "inactive"
    
    # Check platform toggle
    if platform_toggle_system:
        components["platform_toggle"] = "healthy" if platform_toggle_system.is_initialized else "inactive"
    
    # Overall status
    all_healthy = all(status == "healthy" for status in components.values())
    overall_status = "healthy" if all_healthy else "degraded"
    
    return {
        "status": overall_status,
        "components": components,
        "uptime": (datetime.now() - system_state["startup_time"]).total_seconds() if system_state["startup_time"] else 0
    }

async def ensure_system_initialized():
    """Ensure the system is initialized"""
    if not system_state["is_initialized"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System not initialized. Please call /system/initialize first."
        )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    global system_state
    system_state["startup_time"] = datetime.now()
    logger.info("🚀 Starting Bidirectional ML API Gateway...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Bidirectional ML API Gateway...")
    
    # Stop all components
    if bidirectional_engine and bidirectional_engine.is_running:
        await bidirectional_engine.stop_processing()
    
    if data_acquisition_engine and data_acquisition_engine.is_collecting:
        await data_acquisition_engine.stop_data_collection()
    
    if action_generation_system and action_generation_system.is_executing:
        await action_generation_system.stop_action_execution_engine()

# System Management Endpoints

@app.post("/system/initialize", response_model=APIResponse)
async def initialize_system(background_tasks: BackgroundTasks):
    """Initialize the complete bidirectional ML system"""
    global bidirectional_engine, data_acquisition_engine, cloud_processing_pipeline
    global action_generation_system, platform_toggle_system
    
    try:
        logger.info("🔄 Initializing bidirectional ML system...")
        
        # Initialize platform toggle system first
        platform_toggle_system = create_platform_toggle_system()
        await platform_toggle_system.initialize()
        
        # Initialize data acquisition engine
        data_acquisition_engine = create_data_acquisition_engine()
        await data_acquisition_engine.initialize()
        
        # Initialize cloud processing pipeline
        cloud_processing_pipeline = create_cloud_processing_pipeline()
        await cloud_processing_pipeline.initialize()
        
        # Initialize action generation system
        action_generation_system = create_action_generation_system()
        await action_generation_system.initialize()
        
        # Initialize bidirectional engine (orchestrates everything)
        bidirectional_engine = create_bidirectional_ml_engine()
        await bidirectional_engine.initialize()
        
        # Connect components
        bidirectional_engine.data_acquisition_engine = data_acquisition_engine
        bidirectional_engine.cloud_processing_pipeline = cloud_processing_pipeline
        bidirectional_engine.action_generation_system = action_generation_system
        bidirectional_engine.platform_toggle_system = platform_toggle_system
        
        system_state["is_initialized"] = True
        system_state["components_status"] = await get_system_health()
        
        logger.info("✅ Bidirectional ML system initialized successfully!")
        
        return APIResponse(
            success=True,
            message="System initialized successfully",
            data={
                "components": system_state["components_status"],
                "initialization_time": datetime.now().isoformat()
            }
        )
    
    except Exception as e:
        logger.error(f"❌ System initialization failed: {e}")
        logger.error(traceback.format_exc())
        
        return APIResponse(
            success=False,
            message=f"System initialization failed: {str(e)}"
        )

@app.get("/system/health", response_model=HealthResponse)
async def get_health():
    """Get system health status"""
    try:
        health = await get_system_health()
        system_state["last_health_check"] = datetime.now()
        
        # Calculate metrics
        metrics = {}
        if system_state["startup_time"]:
            metrics["uptime_hours"] = (datetime.now() - system_state["startup_time"]).total_seconds() / 3600
        
        if bidirectional_engine:
            engine_metrics = await bidirectional_engine.get_system_metrics()
            metrics.update(engine_metrics.get("performance_metrics", {}))
        
        return HealthResponse(
            status=health["status"],
            uptime=health["uptime"],
            components=health["components"],
            metrics=metrics
        )
    
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

@app.get("/system/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get comprehensive system metrics"""
    await ensure_system_initialized()
    
    try:
        system_metrics = {}
        platform_metrics = {}
        ml_metrics = {}
        
        # Get bidirectional engine metrics
        if bidirectional_engine:
            engine_metrics = await bidirectional_engine.get_system_metrics()
            system_metrics.update(engine_metrics)
        
        # Get platform metrics
        if platform_toggle_system:
            platform_status = await platform_toggle_system.get_platform_status()
            platform_metrics = platform_status
        
        # Get ML metrics
        if cloud_processing_pipeline:
            ml_pipeline_metrics = await cloud_processing_pipeline.get_processing_metrics()
            ml_metrics.update(ml_pipeline_metrics)
        
        if action_generation_system:
            action_metrics = await action_generation_system.get_execution_metrics()
            ml_metrics.update(action_metrics)
        
        return MetricsResponse(
            system_metrics=system_metrics,
            platform_metrics=platform_metrics,
            ml_metrics=ml_metrics
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to get metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )

@app.post("/system/start", response_model=APIResponse)
async def start_system():
    """Start the complete bidirectional ML system"""
    await ensure_system_initialized()
    
    try:
        # Start all components
        tasks = []
        
        if data_acquisition_engine:
            tasks.append(data_acquisition_engine.start_real_time_collection())
        
        if cloud_processing_pipeline:
            tasks.append(cloud_processing_pipeline.start_processing_engine())
        
        if action_generation_system:
            tasks.append(action_generation_system.start_action_execution_engine())
        
        if bidirectional_engine:
            tasks.append(bidirectional_engine.start_processing())
        
        # Execute all startup tasks
        await asyncio.gather(*tasks)
        
        return APIResponse(
            success=True,
            message="System started successfully",
            data=await get_system_health()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to start system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start system: {str(e)}"
        )

@app.post("/system/stop", response_model=APIResponse)
async def stop_system():
    """Stop the complete bidirectional ML system"""
    await ensure_system_initialized()
    
    try:
        # Stop all components
        tasks = []
        
        if bidirectional_engine and bidirectional_engine.is_running:
            tasks.append(bidirectional_engine.stop_processing())
        
        if data_acquisition_engine and data_acquisition_engine.is_collecting:
            tasks.append(data_acquisition_engine.stop_data_collection())
        
        if cloud_processing_pipeline and cloud_processing_pipeline.is_processing:
            tasks.append(cloud_processing_pipeline.stop_processing_engine())
        
        if action_generation_system and action_generation_system.is_executing:
            tasks.append(action_generation_system.stop_action_execution_engine())
        
        # Execute all shutdown tasks
        await asyncio.gather(*tasks)
        
        return APIResponse(
            success=True,
            message="System stopped successfully",
            data=await get_system_health()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to stop system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop system: {str(e)}"
        )

# Platform Management Endpoints

@app.get("/platforms", response_model=APIResponse)
async def get_platforms():
    """Get all available platforms and their status"""
    await ensure_system_initialized()
    
    try:
        platforms = await platform_toggle_system.get_platform_status()
        
        return APIResponse(
            success=True,
            message="Platforms retrieved successfully",
            data=platforms
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to get platforms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platforms: {str(e)}"
        )

@app.post("/platforms/{platform_id}/activate", response_model=APIResponse)
async def activate_platform(platform_id: str, request: PlatformActivationRequest):
    """Activate a specific platform"""
    await ensure_system_initialized()
    
    try:
        # Set platform mode if specified
        if request.mode:
            mode = PlatformMode(request.mode.lower())
            await platform_toggle_system.set_platform_mode(platform_id, mode)
        
        # Enable capabilities if specified
        for capability_str in request.capabilities:
            capability = PlatformCapability(capability_str.lower())
            await platform_toggle_system.enable_platform_capability(platform_id, capability)
        
        # Activate platform
        success = await platform_toggle_system.activate_platform(platform_id)
        
        if success:
            # Update bidirectional engine
            if bidirectional_engine:
                await bidirectional_engine.activate_platform(platform_id)
            
            platform_status = await platform_toggle_system.get_platform_status(platform_id)
            
            return APIResponse(
                success=True,
                message=f"Platform {platform_id} activated successfully",
                data=platform_status
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to activate platform {platform_id}"
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Failed to activate platform {platform_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate platform: {str(e)}"
        )

@app.post("/platforms/{platform_id}/deactivate", response_model=APIResponse)
async def deactivate_platform(platform_id: str):
    """Deactivate a specific platform"""
    await ensure_system_initialized()
    
    try:
        success = await platform_toggle_system.deactivate_platform(platform_id)
        
        if success:
            # Update bidirectional engine
            if bidirectional_engine:
                await bidirectional_engine.deactivate_platform(platform_id)
            
            platform_status = await platform_toggle_system.get_platform_status(platform_id)
            
            return APIResponse(
                success=True,
                message=f"Platform {platform_id} deactivated successfully",
                data=platform_status
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to deactivate platform {platform_id}"
            )
    
    except Exception as e:
        logger.error(f"❌ Failed to deactivate platform {platform_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate platform: {str(e)}"
        )

@app.post("/platforms/{platform_id}/capabilities/enable", response_model=APIResponse)
async def enable_platform_capability(platform_id: str, request: CapabilityRequest):
    """Enable a capability for a platform"""
    await ensure_system_initialized()
    
    try:
        capability = PlatformCapability(request.capability.lower())
        success = await platform_toggle_system.enable_platform_capability(platform_id, capability)
        
        if success:
            return APIResponse(
                success=True,
                message=f"Capability {request.capability} enabled for {platform_id}",
                data=await platform_toggle_system.get_platform_status(platform_id)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to enable capability {request.capability}"
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid capability: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Failed to enable capability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable capability: {str(e)}"
        )

@app.post("/platforms/{platform_id}/capabilities/disable", response_model=APIResponse)
async def disable_platform_capability(platform_id: str, request: CapabilityRequest):
    """Disable a capability for a platform"""
    await ensure_system_initialized()
    
    try:
        capability = PlatformCapability(request.capability.lower())
        success = await platform_toggle_system.disable_platform_capability(platform_id, capability)
        
        if success:
            return APIResponse(
                success=True,
                message=f"Capability {request.capability} disabled for {platform_id}",
                data=await platform_toggle_system.get_platform_status(platform_id)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to disable capability {request.capability}"
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid capability: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Failed to disable capability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable capability: {str(e)}"
        )

@app.post("/platforms/global-mode", response_model=APIResponse)
async def set_global_mode(request: GlobalModeRequest):
    """Set global mode for all platforms"""
    await ensure_system_initialized()
    
    try:
        mode = PlatformMode(request.mode.lower())
        await platform_toggle_system.set_global_mode(mode)
        
        return APIResponse(
            success=True,
            message=f"Global mode set to {request.mode}",
            data=await platform_toggle_system.get_platform_status()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Failed to set global mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set global mode: {str(e)}"
        )

# Data Collection Endpoints

@app.post("/data/collect/start", response_model=APIResponse)
async def start_data_collection(request: DataCollectionRequest):
    """Start data collection from specified platforms"""
    await ensure_system_initialized()
    
    try:
        # Configure collection parameters
        config = {
            "target_platforms": request.platforms or ["instagram", "twitter", "linkedin", "whatsapp"],
            "collection_duration": request.duration_hours,
            "target_metrics": request.metrics or ["engagement", "reach", "impressions"]
        }
        
        # Update data acquisition engine configuration
        if data_acquisition_engine:
            await data_acquisition_engine.update_collection_config(config)
            
            if not data_acquisition_engine.is_collecting:
                await data_acquisition_engine.start_real_time_collection()
        
        return APIResponse(
            success=True,
            message="Data collection started successfully",
            data={
                "platforms": config["target_platforms"],
                "duration_hours": config["collection_duration"],
                "metrics": config["target_metrics"]
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to start data collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start data collection: {str(e)}"
        )

@app.post("/data/collect/stop", response_model=APIResponse)
async def stop_data_collection():
    """Stop data collection"""
    await ensure_system_initialized()
    
    try:
        if data_acquisition_engine and data_acquisition_engine.is_collecting:
            await data_acquisition_engine.stop_data_collection()
        
        return APIResponse(
            success=True,
            message="Data collection stopped successfully"
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to stop data collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop data collection: {str(e)}"
        )

@app.get("/data/metrics", response_model=APIResponse)
async def get_data_metrics():
    """Get current data collection metrics"""
    await ensure_system_initialized()
    
    try:
        metrics = {}
        
        if data_acquisition_engine:
            metrics = await data_acquisition_engine.get_collection_metrics()
        
        return APIResponse(
            success=True,
            message="Data metrics retrieved successfully",
            data=metrics
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to get data metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data metrics: {str(e)}"
        )

# ML Processing Endpoints

@app.post("/ml/process/start", response_model=APIResponse)
async def start_ml_processing(request: MLProcessingRequest):
    """Start ML processing pipeline"""
    await ensure_system_initialized()
    
    try:
        # Configure processing parameters
        config = {
            "data_source": request.data_source,
            "model_types": request.model_types or ["engagement_predictor", "viral_detector"],
            "priority": request.priority,
            "processing_mode": "continuous"
        }
        
        # Update cloud processing pipeline
        if cloud_processing_pipeline:
            await cloud_processing_pipeline.update_processing_config(config)
            
            if not cloud_processing_pipeline.is_processing:
                await cloud_processing_pipeline.start_processing_engine()
        
        return APIResponse(
            success=True,
            message="ML processing started successfully",
            data=config
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to start ML processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start ML processing: {str(e)}"
        )

@app.post("/ml/process/stop", response_model=APIResponse)
async def stop_ml_processing():
    """Stop ML processing pipeline"""
    await ensure_system_initialized()
    
    try:
        if cloud_processing_pipeline and cloud_processing_pipeline.is_processing:
            await cloud_processing_pipeline.stop_processing_engine()
        
        return APIResponse(
            success=True,
            message="ML processing stopped successfully"
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to stop ML processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop ML processing: {str(e)}"
        )

@app.get("/ml/insights", response_model=APIResponse)
async def get_ml_insights():
    """Get recent ML insights and predictions"""
    await ensure_system_initialized()
    
    try:
        insights = []
        
        if cloud_processing_pipeline:
            recent_insights = await cloud_processing_pipeline.get_recent_insights()
            insights = [asdict(insight) for insight in recent_insights]
        
        return APIResponse(
            success=True,
            message="ML insights retrieved successfully",
            data={"insights": insights}
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to get ML insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ML insights: {str(e)}"
        )

# Action Management Endpoints

@app.get("/actions/pending", response_model=APIResponse)
async def get_pending_actions():
    """Get pending actions"""
    await ensure_system_initialized()
    
    try:
        actions = []
        
        if action_generation_system:
            pending_actions = action_generation_system.pending_actions
            actions = [asdict(action) for action in pending_actions]
        
        return APIResponse(
            success=True,
            message="Pending actions retrieved successfully",
            data={"actions": actions}
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to get pending actions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending actions: {str(e)}"
        )

@app.post("/actions/execute", response_model=APIResponse)
async def execute_action(request: ActionExecutionRequest):
    """Execute a specific action"""
    await ensure_system_initialized()
    
    try:
        action = await action_generation_system.get_action_status(request.action_id)
        
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action {request.action_id} not found"
            )
        
        if request.force_execute:
            result = await action_generation_system.execute_action_immediately(action)
        else:
            # Add to execution queue
            result = {"status": "queued", "action_id": request.action_id}
        
        return APIResponse(
            success=True,
            message=f"Action {request.action_id} execution initiated",
            data=asdict(result) if hasattr(result, '__dict__') else result
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to execute action: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute action: {str(e)}"
        )

@app.get("/actions/{action_id}/status", response_model=APIResponse)
async def get_action_status(action_id: str):
    """Get status of a specific action"""
    await ensure_system_initialized()
    
    try:
        action = await action_generation_system.get_action_status(action_id)
        
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action {action_id} not found"
            )
        
        return APIResponse(
            success=True,
            message="Action status retrieved successfully",
            data=asdict(action)
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to get action status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get action status: {str(e)}"
        )

# Bidirectional Flow Endpoints

@app.post("/flow/start-complete", response_model=APIResponse)
async def start_complete_bidirectional_flow():
    """Start the complete bidirectional ML flow"""
    await ensure_system_initialized()
    
    try:
        # Start all components in the correct order
        await start_data_collection(DataCollectionRequest())
        await start_ml_processing(MLProcessingRequest(data_source="real_time"))
        
        if action_generation_system and not action_generation_system.is_executing:
            await action_generation_system.start_action_execution_engine()
        
        if bidirectional_engine and not bidirectional_engine.is_running:
            await bidirectional_engine.start_processing()
        
        return APIResponse(
            success=True,
            message="Complete bidirectional flow started successfully",
            data=await get_system_health()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to start complete flow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start complete flow: {str(e)}"
        )

@app.post("/flow/stop-complete", response_model=APIResponse)
async def stop_complete_bidirectional_flow():
    """Stop the complete bidirectional ML flow"""
    await ensure_system_initialized()
    
    try:
        # Stop all components
        if bidirectional_engine and bidirectional_engine.is_running:
            await bidirectional_engine.stop_processing()
        
        if action_generation_system and action_generation_system.is_executing:
            await action_generation_system.stop_action_execution_engine()
        
        await stop_ml_processing()
        await stop_data_collection()
        
        return APIResponse(
            success=True,
            message="Complete bidirectional flow stopped successfully",
            data=await get_system_health()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to stop complete flow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop complete flow: {str(e)}"
        )

@app.get("/flow/status", response_model=APIResponse)
async def get_flow_status():
    """Get status of the complete bidirectional flow"""
    await ensure_system_initialized()
    
    try:
        flow_status = {
            "data_acquisition_active": data_acquisition_engine.is_collecting if data_acquisition_engine else False,
            "ml_processing_active": cloud_processing_pipeline.is_processing if cloud_processing_pipeline else False,
            "action_generation_active": action_generation_system.is_executing if action_generation_system else False,
            "bidirectional_engine_active": bidirectional_engine.is_running if bidirectional_engine else False,
            "overall_status": "active" if all([
                data_acquisition_engine and data_acquisition_engine.is_collecting,
                cloud_processing_pipeline and cloud_processing_pipeline.is_processing,
                action_generation_system and action_generation_system.is_executing,
                bidirectional_engine and bidirectional_engine.is_running
            ]) else "inactive"
        }
        
        return APIResponse(
            success=True,
            message="Flow status retrieved successfully",
            data=flow_status
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to get flow status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get flow status: {str(e)}"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            success=False,
            message=exc.detail
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"❌ Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            success=False,
            message="Internal server error"
        ).dict()
    )

# Main function to run the API
def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the Bidirectional ML API Gateway"""
    if not FASTAPI_AVAILABLE:
        print("❌ Cannot start API Gateway - FastAPI dependencies not installed")
        print("💡 Run: pip install fastapi uvicorn pydantic")
        return
    
    logger.info(f"🌐 Starting Bidirectional ML API Gateway on {host}:{port}")
    
    uvicorn.run(
        "ml_core.api_gateway:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    run_api()