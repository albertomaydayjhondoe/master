"""
Landing Page Analytics Client
Handles Meta Pixel tracking, conversion monitoring, and traffic analytics
Integrates with Supabase for comprehensive landing page performance tracking
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from config.production_config import get_config
from integrations.supabase_client import supabase_client

config = get_config()

class LandingPageClient:
    """Landing Page analytics and conversion tracking client"""
    
    def __init__(self):
        self.meta_pixel_id = config.META_PIXEL_ID
        self.meta_access_token = config.META_ACCESS_TOKEN
        self.landing_page_urls = config.LANDING_PAGE_URLS
        self.base_url = "https://graph.facebook.com/v18.0"
        self.client = httpx.AsyncClient()
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def test_connection(self) -> bool:
        """Test Meta Pixel API connection"""
        try:
            if not self.meta_pixel_id or not self.meta_access_token:
                return False
            
            url = f"{self.base_url}/{self.meta_pixel_id}"
            params = {"access_token": self.meta_access_token}
            
            response = await self.client.get(url, params=params)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Landing page connection test failed: {e}")
            return False
    
    async def get_pixel_events(self, days: int = 7) -> Dict[str, Any]:
        """Get Meta Pixel events for landing page tracking"""
        try:
            if not self.meta_pixel_id or not self.meta_access_token:
                return {"error": "Meta Pixel not configured"}
            
            # Calculate date range
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            url = f"{self.base_url}/{self.meta_pixel_id}/stats"
            params = {
                "access_token": self.meta_access_token,
                "start_time": start_date.isoformat(),
                "end_time": end_date.isoformat(),
                "aggregation": "event_source_group"
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                pixel_stats = {
                    "pixel_id": self.meta_pixel_id,
                    "period_days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "events": data.get("data", []),
                    "fetched_at": datetime.utcnow().isoformat()
                }
                
                # Store in Supabase
                await supabase_client.store_landing_page_metrics(pixel_stats)
                
                return pixel_stats
            
            return {"error": f"API error: {response.status_code}"}
            
        except Exception as e:
            print(f"Error fetching pixel events: {e}")
            return {"error": str(e)}
    
    async def track_conversion_event(self, event_data: Dict[str, Any]) -> bool:
        """Track a conversion event for analytics"""
        try:
            # Validate required fields
            required_fields = ["event_name", "page_url", "timestamp"]
            if not all(field in event_data for field in required_fields):
                return False
            
            # Enrich event data
            enriched_event = {
                "pixel_id": self.meta_pixel_id,
                "event_name": event_data["event_name"],
                "page_url": event_data["page_url"],
                "timestamp": event_data["timestamp"],
                "user_data": event_data.get("user_data", {}),
                "custom_data": event_data.get("custom_data", {}),
                "value": event_data.get("value", 0),
                "currency": event_data.get("currency", "USD"),
                "source": event_data.get("source", "landing_page"),
                "campaign_id": event_data.get("campaign_id"),
                "ad_set_id": event_data.get("ad_set_id"),
                "ad_id": event_data.get("ad_id"),
                "utm_source": event_data.get("utm_source"),
                "utm_medium": event_data.get("utm_medium"),
                "utm_campaign": event_data.get("utm_campaign"),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Supabase
            result = await supabase_client.store_landing_page_metrics({
                "type": "conversion_event",
                "data": enriched_event
            })
            
            return bool(result)
            
        except Exception as e:
            print(f"Error tracking conversion event: {e}")
            return False
    
    async def get_landing_page_performance(self, page_url: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive landing page performance metrics"""
        try:
            # Get stored metrics from Supabase
            metrics = await supabase_client.get_landing_page_metrics(days)
            
            # Filter by specific page URL if provided
            page_metrics = []
            if page_url:
                page_metrics = [
                    metric for metric in metrics 
                    if metric.get("data", {}).get("page_url") == page_url or 
                       metric.get("page_url") == page_url
                ]
            else:
                page_metrics = metrics
            
            # Calculate performance statistics
            total_events = len(page_metrics)
            conversion_events = [m for m in page_metrics if m.get("data", {}).get("event_name") in ["Purchase", "Lead", "CompleteRegistration"]]
            total_conversions = len(conversion_events)
            
            # Calculate conversion value
            total_value = sum(
                float(m.get("data", {}).get("value", 0)) 
                for m in conversion_events
            )
            
            # Event breakdown
            event_breakdown = {}
            for metric in page_metrics:
                event_name = metric.get("data", {}).get("event_name", "Unknown")
                event_breakdown[event_name] = event_breakdown.get(event_name, 0) + 1
            
            # Traffic source analysis
            traffic_sources = {}
            for metric in page_metrics:
                utm_source = metric.get("data", {}).get("utm_source", "Direct")
                traffic_sources[utm_source] = traffic_sources.get(utm_source, 0) + 1
            
            performance = {
                "page_url": page_url,
                "period_days": days,
                "total_events": total_events,
                "total_conversions": total_conversions,
                "conversion_rate": (total_conversions / total_events * 100) if total_events > 0 else 0,
                "total_conversion_value": total_value,
                "avg_conversion_value": total_value / total_conversions if total_conversions > 0 else 0,
                "event_breakdown": event_breakdown,
                "traffic_sources": traffic_sources,
                "recent_conversions": conversion_events[-10:],  # Last 10 conversions
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            # Store performance report
            await supabase_client.store_landing_page_metrics({
                "type": "performance_report",
                "data": performance
            })
            
            return performance
            
        except Exception as e:
            print(f"Error getting landing page performance: {e}")
            return {
                "page_url": page_url,
                "error": str(e),
                "analyzed_at": datetime.utcnow().isoformat()
            }
    
    async def get_funnel_analysis(self, funnel_steps: List[str], days: int = 30) -> Dict[str, Any]:
        """Analyze conversion funnel performance"""
        try:
            # Get all landing page metrics
            all_metrics = await supabase_client.get_landing_page_metrics(days)
            
            # Initialize funnel data
            funnel_data = {step: 0 for step in funnel_steps}
            user_progression = {}
            
            # Analyze user progression through funnel
            for metric in all_metrics:
                event_name = metric.get("data", {}).get("event_name")
                user_id = metric.get("data", {}).get("user_data", {}).get("external_id", "anonymous")
                timestamp = metric.get("data", {}).get("timestamp")
                
                if event_name in funnel_steps:
                    funnel_data[event_name] += 1
                    
                    # Track user progression
                    if user_id not in user_progression:
                        user_progression[user_id] = []
                    user_progression[user_id].append({
                        "step": event_name,
                        "timestamp": timestamp
                    })
            
            # Calculate conversion rates between steps
            conversion_rates = {}
            for i in range(len(funnel_steps) - 1):
                current_step = funnel_steps[i]
                next_step = funnel_steps[i + 1]
                
                current_count = funnel_data[current_step]
                next_count = funnel_data[next_step]
                
                rate = (next_count / current_count * 100) if current_count > 0 else 0
                conversion_rates[f"{current_step}_to_{next_step}"] = round(rate, 2)
            
            # Calculate overall funnel conversion rate
            total_entries = funnel_data[funnel_steps[0]] if funnel_steps else 0
            total_completions = funnel_data[funnel_steps[-1]] if funnel_steps else 0
            overall_rate = (total_completions / total_entries * 100) if total_entries > 0 else 0
            
            funnel_analysis = {
                "funnel_steps": funnel_steps,
                "period_days": days,
                "step_counts": funnel_data,
                "conversion_rates": conversion_rates,
                "overall_conversion_rate": round(overall_rate, 2),
                "total_users": len(user_progression),
                "users_completed_funnel": sum(
                    1 for user_steps in user_progression.values()
                    if len(set(step["step"] for step in user_steps)) == len(funnel_steps)
                ),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            # Store funnel analysis
            await supabase_client.store_landing_page_metrics({
                "type": "funnel_analysis",
                "data": funnel_analysis
            })
            
            return funnel_analysis
            
        except Exception as e:
            print(f"Error analyzing funnel: {e}")
            return {
                "error": str(e),
                "analyzed_at": datetime.utcnow().isoformat()
            }
    
    async def get_traffic_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive traffic analytics"""
        try:
            # Get all landing page metrics
            metrics = await supabase_client.get_landing_page_metrics(days)
            
            # Analyze traffic patterns
            daily_traffic = {}
            hourly_traffic = {}
            source_breakdown = {}
            campaign_performance = {}
            
            for metric in metrics:
                data = metric.get("data", {})
                timestamp_str = data.get("timestamp")
                
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        date_key = timestamp.date().isoformat()
                        hour_key = timestamp.hour
                        
                        # Daily traffic
                        daily_traffic[date_key] = daily_traffic.get(date_key, 0) + 1
                        
                        # Hourly traffic
                        hourly_traffic[hour_key] = hourly_traffic.get(hour_key, 0) + 1
                        
                    except Exception:
                        pass
                
                # Source analysis
                utm_source = data.get("utm_source", "Direct")
                source_breakdown[utm_source] = source_breakdown.get(utm_source, 0) + 1
                
                # Campaign analysis
                campaign_id = data.get("campaign_id")
                if campaign_id:
                    if campaign_id not in campaign_performance:
                        campaign_performance[campaign_id] = {
                            "events": 0,
                            "conversions": 0,
                            "value": 0
                        }
                    
                    campaign_performance[campaign_id]["events"] += 1
                    
                    if data.get("event_name") in ["Purchase", "Lead", "CompleteRegistration"]:
                        campaign_performance[campaign_id]["conversions"] += 1
                        campaign_performance[campaign_id]["value"] += float(data.get("value", 0))
            
            # Calculate peak traffic times
            peak_hour = max(hourly_traffic.items(), key=lambda x: x[1]) if hourly_traffic else (0, 0)
            peak_day = max(daily_traffic.items(), key=lambda x: x[1]) if daily_traffic else ("", 0)
            
            traffic_analytics = {
                "period_days": days,
                "total_events": len(metrics),
                "daily_traffic": daily_traffic,
                "hourly_distribution": hourly_traffic,
                "peak_hour": {"hour": peak_hour[0], "events": peak_hour[1]},
                "peak_day": {"date": peak_day[0], "events": peak_day[1]},
                "traffic_sources": source_breakdown,
                "campaign_performance": campaign_performance,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            # Store traffic analytics
            await supabase_client.store_landing_page_metrics({
                "type": "traffic_analytics",
                "data": traffic_analytics
            })
            
            return traffic_analytics
            
        except Exception as e:
            print(f"Error analyzing traffic: {e}")
            return {
                "error": str(e),
                "analyzed_at": datetime.utcnow().isoformat()
            }
    
    async def collect_comprehensive_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Collect comprehensive landing page analytics"""
        try:
            comprehensive_report = {
                "report_type": "landing_page_comprehensive",
                "period_days": days,
                "pixel_events": {},
                "page_performance": {},
                "traffic_analytics": {},
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Get pixel events
            comprehensive_report["pixel_events"] = await self.get_pixel_events(days)
            
            # Get performance for each configured landing page
            if self.landing_page_urls:
                for url in self.landing_page_urls:
                    page_perf = await self.get_landing_page_performance(url, days)
                    comprehensive_report["page_performance"][url] = page_perf
            
            # Get traffic analytics
            comprehensive_report["traffic_analytics"] = await self.get_traffic_analytics(days)
            
            # Store comprehensive report
            await supabase_client.store_landing_page_metrics({
                "type": "comprehensive_report",
                "data": comprehensive_report
            })
            
            return comprehensive_report
            
        except Exception as e:
            print(f"Error collecting comprehensive analytics: {e}")
            return {
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }

# Global client instance
landing_page_client = LandingPageClient()

async def test_landing_page_connection() -> bool:
    """Test landing page analytics connection"""
    return await landing_page_client.test_connection()

async def track_conversion(event_data: Dict[str, Any]) -> bool:
    """Track a conversion event"""
    return await landing_page_client.track_conversion_event(event_data)

async def get_landing_page_comprehensive_report(days: int = 30) -> Dict[str, Any]:
    """Get comprehensive landing page report"""
    return await landing_page_client.collect_comprehensive_analytics(days)

# Cleanup function
async def cleanup_landing_page_client():
    """Cleanup landing page client resources"""
    await landing_page_client.close()