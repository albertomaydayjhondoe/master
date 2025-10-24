"""
Facebook Pixel Tracker Service - Docker v2.0
Conversion tracking and Custom Audience building
"""

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx
import os
import logging
import hashlib
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pixel Tracker v2.0",
    description="Facebook Pixel & Conversion API Integration",
    version="2.0.0"
)

# ============================================
# CONFIGURATION
# ============================================

DUMMY_MODE = os.getenv("DUMMY_MODE", "true") == "true"
META_PIXEL_ID = os.getenv("META_PIXEL_ID")
META_CONVERSION_API_TOKEN = os.getenv("META_CONVERSION_API_TOKEN")
CONVERSION_API_URL = f"https://graph.facebook.com/v18.0/{META_PIXEL_ID}/events"

# ============================================
# MODELS
# ============================================

class PixelEvent(BaseModel):
    event_name: str = Field(..., description="Event name (e.g., PageView, Purchase, Lead)")
    event_id: Optional[str] = None
    event_time: Optional[int] = None
    user_data: Dict[str, Any] = Field(default_factory=dict)
    custom_data: Dict[str, Any] = Field(default_factory=dict)
    action_source: str = "website"  # website, app, offline

class ConversionEvent(BaseModel):
    """Standard Facebook Conversion Events"""
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    user_ip: Optional[str] = None
    user_agent: Optional[str] = None
    fbp_cookie: Optional[str] = None  # _fbp cookie
    fbc_cookie: Optional[str] = None  # _fbc cookie
    event_source_url: str
    value: Optional[float] = None
    currency: str = "USD"
    content_name: Optional[str] = None
    content_category: Optional[str] = None
    content_ids: Optional[List[str]] = None

# ============================================
# PIXEL TRACKER CLIENT
# ============================================

class PixelTrackerClient:
    def __init__(self):
        self.pixel_id = META_PIXEL_ID
        self.access_token = META_CONVERSION_API_TOKEN
        self.api_url = CONVERSION_API_URL
    
    def _hash_data(self, data: str) -> str:
        """Hash user data for privacy (SHA-256)"""
        if not data:
            return None
        return hashlib.sha256(data.lower().strip().encode()).hexdigest()
    
    async def send_event(
        self,
        event: PixelEvent,
        test_mode: bool = False
    ) -> Dict:
        """Send event to Facebook Conversion API"""
        
        if DUMMY_MODE:
            logger.info(f"DUMMY MODE: Pixel event {event.event_name}")
            return {
                "events_received": 1,
                "events_processed": 1,
                "fbtrace_id": "dummy_trace_id"
            }
        
        # Prepare event data
        event_data = {
            "event_name": event.event_name,
            "event_time": event.event_time or int(datetime.now().timestamp()),
            "action_source": event.action_source,
            "user_data": {},
            "custom_data": event.custom_data
        }
        
        # Hash sensitive user data
        if event.user_data.get("email"):
            event_data["user_data"]["em"] = self._hash_data(event.user_data["email"])
        if event.user_data.get("phone"):
            event_data["user_data"]["ph"] = self._hash_data(event.user_data["phone"])
        if event.user_data.get("first_name"):
            event_data["user_data"]["fn"] = self._hash_data(event.user_data["first_name"])
        if event.user_data.get("last_name"):
            event_data["user_data"]["ln"] = self._hash_data(event.user_data["last_name"])
        
        # Add non-hashed data
        if event.user_data.get("client_ip_address"):
            event_data["user_data"]["client_ip_address"] = event.user_data["client_ip_address"]
        if event.user_data.get("client_user_agent"):
            event_data["user_data"]["client_user_agent"] = event.user_data["client_user_agent"]
        if event.user_data.get("fbp"):
            event_data["user_data"]["fbp"] = event.user_data["fbp"]
        if event.user_data.get("fbc"):
            event_data["user_data"]["fbc"] = event.user_data["fbc"]
        
        if event.event_id:
            event_data["event_id"] = event.event_id
        
        # Prepare payload
        payload = {
            "data": [event_data],
            "access_token": self.access_token
        }
        
        if test_mode:
            payload["test_event_code"] = "TEST12345"
        
        # Send to Conversion API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json=payload,
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"Pixel API Error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Pixel API error: {response.text}"
                )
            
            return response.json()

# ============================================
# STANDARD EVENTS
# ============================================

pixel_client = PixelTrackerClient()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "pixel-tracker-v2",
        "dummy_mode": DUMMY_MODE,
        "pixel_id": META_PIXEL_ID,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/track/pageview")
async def track_page_view(request: Request, event_data: ConversionEvent):
    """Track PageView event"""
    
    user_data = {
        "email": event_data.user_email,
        "phone": event_data.user_phone,
        "client_ip_address": event_data.user_ip or request.client.host,
        "client_user_agent": event_data.user_agent or request.headers.get("user-agent"),
        "fbp": event_data.fbp_cookie,
        "fbc": event_data.fbc_cookie
    }
    
    custom_data = {
        "event_source_url": event_data.event_source_url,
        "content_name": event_data.content_name
    }
    
    event = PixelEvent(
        event_name="PageView",
        event_id=f"pageview_{int(datetime.now().timestamp())}",
        user_data=user_data,
        custom_data=custom_data
    )
    
    result = await pixel_client.send_event(event)
    logger.info(f"PageView tracked: {result}")
    
    return {"status": "success", "result": result}

@app.post("/track/viewcontent")
async def track_view_content(request: Request, event_data: ConversionEvent):
    """Track ViewContent event (music page view)"""
    
    user_data = {
        "email": event_data.user_email,
        "client_ip_address": event_data.user_ip or request.client.host,
        "client_user_agent": event_data.user_agent or request.headers.get("user-agent"),
        "fbp": event_data.fbp_cookie,
        "fbc": event_data.fbc_cookie
    }
    
    custom_data = {
        "content_name": event_data.content_name,  # Song name
        "content_category": event_data.content_category,  # Genre
        "content_ids": event_data.content_ids,  # [artist_id, track_id]
        "event_source_url": event_data.event_source_url,
        "value": event_data.value,
        "currency": event_data.currency
    }
    
    event = PixelEvent(
        event_name="ViewContent",
        event_id=f"viewcontent_{int(datetime.now().timestamp())}",
        user_data=user_data,
        custom_data=custom_data
    )
    
    result = await pixel_client.send_event(event)
    logger.info(f"ViewContent tracked: {result}")
    
    return {"status": "success", "result": result}

@app.post("/track/lead")
async def track_lead(request: Request, event_data: ConversionEvent):
    """Track Lead event (email signup, follow, etc.)"""
    
    user_data = {
        "email": event_data.user_email,
        "phone": event_data.user_phone,
        "client_ip_address": event_data.user_ip or request.client.host,
        "client_user_agent": event_data.user_agent or request.headers.get("user-agent"),
        "fbp": event_data.fbp_cookie,
        "fbc": event_data.fbc_cookie
    }
    
    custom_data = {
        "content_name": event_data.content_name,
        "event_source_url": event_data.event_source_url,
        "value": event_data.value or 1.0,  # Default lead value
        "currency": event_data.currency
    }
    
    event = PixelEvent(
        event_name="Lead",
        event_id=f"lead_{int(datetime.now().timestamp())}",
        user_data=user_data,
        custom_data=custom_data
    )
    
    result = await pixel_client.send_event(event)
    logger.info(f"Lead tracked: {result}")
    
    return {"status": "success", "result": result}

@app.post("/track/custom")
async def track_custom_event(
    request: Request,
    event_name: str,
    event_data: ConversionEvent
):
    """Track custom event (SpotifyClick, YouTubeClick, etc.)"""
    
    user_data = {
        "email": event_data.user_email,
        "client_ip_address": event_data.user_ip or request.client.host,
        "client_user_agent": event_data.user_agent or request.headers.get("user-agent"),
        "fbp": event_data.fbp_cookie,
        "fbc": event_data.fbc_cookie
    }
    
    custom_data = {
        "content_name": event_data.content_name,
        "content_category": event_data.content_category,
        "event_source_url": event_data.event_source_url,
        "value": event_data.value,
        "currency": event_data.currency
    }
    
    event = PixelEvent(
        event_name=event_name,
        event_id=f"{event_name.lower()}_{int(datetime.now().timestamp())}",
        user_data=user_data,
        custom_data=custom_data
    )
    
    result = await pixel_client.send_event(event)
    logger.info(f"Custom event {event_name} tracked: {result}")
    
    return {"status": "success", "result": result}

@app.get("/pixel/snippet")
async def get_pixel_snippet():
    """Get Facebook Pixel JavaScript snippet"""
    
    snippet = f"""
<!-- Facebook Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{META_PIXEL_ID}');
fbq('track', 'PageView');
</script>
<noscript>
  <img height="1" width="1" style="display:none"
       src="https://www.facebook.com/tr?id={META_PIXEL_ID}&ev=PageView&noscript=1"/>
</noscript>
<!-- End Facebook Pixel Code -->
"""
    
    return {"pixel_snippet": snippet}

@app.get("/pixel/music-events")
async def get_music_events_snippet():
    """Get custom music tracking events snippet"""
    
    snippet = """
<script>
// Track Spotify clicks
document.querySelectorAll('a[href*="spotify.com"]').forEach(link => {
  link.addEventListener('click', () => {
    fbq('trackCustom', 'SpotifyClick', {
      content_name: 'Song Name',
      content_category: 'Trap',
      value: 1.00,
      currency: 'USD'
    });
  });
});

// Track YouTube clicks
document.querySelectorAll('a[href*="youtube.com"]').forEach(link => {
  link.addEventListener('click', () => {
    fbq('trackCustom', 'YouTubeClick', {
      content_name: 'Video Name',
      content_category: 'Music Video',
      value: 1.00,
      currency: 'USD'
    });
  });
});

// Track video watch 75%
var video = document.querySelector('video');
if (video) {
  video.addEventListener('timeupdate', function() {
    var percent = (video.currentTime / video.duration) * 100;
    if (percent >= 75 && !video.dataset.tracked75) {
      video.dataset.tracked75 = 'true';
      fbq('trackCustom', 'VideoWatch75', {
        content_name: video.dataset.title || 'Video',
        value: 2.00,
        currency: 'USD'
      });
    }
  });
}
</script>
"""
    
    return {"music_events_snippet": snippet}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)
