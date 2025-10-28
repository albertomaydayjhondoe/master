"""
Meta Ads Integration - Campaign management and analytics
Integrates with Facebook Marketing API for ads automation
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import httpx
import json
from config.production_config import get_config
from integrations.supabase_client import supabase_client

config = get_config()


class MetaAdsClient:
    """Meta Ads API client for campaign management and analytics"""
    
    def __init__(self):
        self.app_id = config.META_APP_ID
        self.app_secret = config.META_APP_SECRET
        self.access_token = config.META_ACCESS_TOKEN
        self.pixel_id = config.META_PIXEL_ID
        self.base_url = "https://graph.facebook.com/v18.0"
        
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def _get_auth_params(self) -> Dict[str, str]:
        """Get authentication parameters"""
        return {
            "access_token": self.access_token
        }
    
    async def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Meta API"""
        url = f"{self.base_url}/{endpoint}"
        
        # Add authentication
        request_params = self._get_auth_params()
        if params:
            request_params.update(params)
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=self.headers, params=request_params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=self.headers, params=request_params, json=data)
            elif method.upper() == "PATCH":
                response = await client.patch(url, headers=self.headers, params=request_params, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=self.headers, params=request_params)
            
            response.raise_for_status()
            return response.json() if response.text else {}
    
    # Account and Campaign Management
    async def get_ad_accounts(self) -> List[Dict[str, Any]]:
        """Get available ad accounts"""
        endpoint = "me/adaccounts"
        params = {
            "fields": "id,name,account_status,balance,currency,timezone_name"
        }
        
        result = await self._request("GET", endpoint, params)
        return result.get("data", [])
    
    async def get_campaigns(self, ad_account_id: str) -> List[Dict[str, Any]]:
        """Get campaigns for ad account"""
        endpoint = f"{ad_account_id}/campaigns"
        params = {
            "fields": "id,name,status,objective,daily_budget,lifetime_budget,start_time,stop_time"
        }
        
        result = await self._request("GET", endpoint, params)
        return result.get("data", [])
    
    async def get_campaign_insights(self, campaign_id: str, days: int = 7) -> Dict[str, Any]:
        """Get campaign performance insights"""
        endpoint = f"{campaign_id}/insights"
        
        # Date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "fields": "impressions,clicks,spend,cpc,cpm,ctr,conversions,conversion_values,frequency,reach",
            "time_range": json.dumps({
                "since": start_date.strftime("%Y-%m-%d"),
                "until": end_date.strftime("%Y-%m-%d")
            }),
            "level": "campaign"
        }
        
        result = await self._request("GET", endpoint, params)
        return result.get("data", [])
    
    # Pixel and Conversion Tracking
    async def get_pixel_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get Facebook Pixel statistics"""
        if not self.pixel_id:
            return {"error": "Pixel ID not configured"}
        
        endpoint = f"{self.pixel_id}/stats"
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "start_time": start_date.strftime("%Y-%m-%d"),
            "end_time": end_date.strftime("%Y-%m-%d"),
            "aggregation": "device_type,event"
        }
        
        try:
            result = await self._request("GET", endpoint, params)
            return result
        except Exception as e:
            return {"error": f"Failed to get pixel stats: {e}"}
    
    async def create_custom_conversion(self, conversion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom conversion for tracking"""
        if not self.pixel_id:
            return {"error": "Pixel ID not configured"}
        
        endpoint = f"{self.pixel_id}/customconversions"
        
        data = {
            "name": conversion_data.get("name"),
            "description": conversion_data.get("description", ""),
            "event_type": conversion_data.get("event_type", "COMPLETE_REGISTRATION"),
            "custom_event_type": conversion_data.get("custom_event_type"),
            "default_conversion_value": conversion_data.get("default_value", 1.0),
            "rule": json.dumps(conversion_data.get("rule", {}))
        }
        
        return await self._request("POST", endpoint, data=data)
    
    # Campaign Creation and Management
    async def create_campaign(self, ad_account_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new campaign"""
        endpoint = f"{ad_account_id}/campaigns"
        
        data = {
            "name": campaign_data.get("name"),
            "objective": campaign_data.get("objective", "CONVERSIONS"),
            "status": campaign_data.get("status", "PAUSED"),
            "daily_budget": campaign_data.get("daily_budget"),
            "lifetime_budget": campaign_data.get("lifetime_budget"),
            "start_time": campaign_data.get("start_time"),
            "stop_time": campaign_data.get("stop_time"),
            "special_ad_categories": campaign_data.get("special_ad_categories", [])
        }
        
        return await self._request("POST", endpoint, data=data)
    
    # Analytics and Reporting
    async def get_comprehensive_report(self, ad_account_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive advertising report"""
        try:
            # Get account info
            account_info = await self._request("GET", ad_account_id, {
                "fields": "id,name,account_status,balance,currency,spend_cap"
            })
            
            # Get campaigns
            campaigns = await self.get_campaigns(ad_account_id)
            
            # Get insights for each campaign
            campaign_insights = []
            for campaign in campaigns:
                insights = await self.get_campaign_insights(campaign["id"], days)
                campaign_insights.append({
                    "campaign": campaign,
                    "insights": insights
                })
            
            # Calculate totals
            total_spend = sum(
                float(insight.get("spend", 0)) 
                for campaign_insight in campaign_insights 
                for insight in campaign_insight["insights"]
            )
            
            total_impressions = sum(
                int(insight.get("impressions", 0)) 
                for campaign_insight in campaign_insights 
                for insight in campaign_insight["insights"]
            )
            
            total_clicks = sum(
                int(insight.get("clicks", 0)) 
                for campaign_insight in campaign_insights 
                for insight in campaign_insight["insights"]
            )
            
            # Pixel stats
            pixel_stats = await self.get_pixel_stats(days)
            
            report = {
                "account": account_info,
                "period_days": days,
                "summary": {
                    "total_spend": total_spend,
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "average_cpc": total_spend / total_clicks if total_clicks > 0 else 0,
                    "average_ctr": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
                },
                "campaigns": campaign_insights,
                "pixel_stats": pixel_stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Store in Supabase
            await self._store_metrics_to_supabase(report)
            
            return report
            
        except Exception as e:
            return {"error": f"Failed to generate report: {e}"}
    
    async def _store_metrics_to_supabase(self, report: Dict[str, Any]) -> None:
        """Store Meta Ads metrics to Supabase"""
        try:
            # Store summary metrics
            summary_metrics = {
                "campaign_id": "summary",
                "campaign_name": "Account Summary",
                "impressions": report["summary"]["total_impressions"],
                "clicks": report["summary"]["total_clicks"],
                "spend": report["summary"]["total_spend"],
                "cpc": report["summary"]["average_cpc"],
                "ctr": report["summary"]["average_ctr"],
                "metadata": {
                    "account_info": report["account"],
                    "period_days": report["period_days"]
                }
            }
            
            await supabase_client.store_meta_ads_metrics(summary_metrics)
            
            # Store individual campaign metrics
            for campaign_insight in report["campaigns"]:
                campaign = campaign_insight["campaign"]
                for insight in campaign_insight["insights"]:
                    campaign_metrics = {
                        "campaign_id": campaign["id"],
                        "campaign_name": campaign["name"],
                        "impressions": int(insight.get("impressions", 0)),
                        "clicks": int(insight.get("clicks", 0)),
                        "spend": float(insight.get("spend", 0)),
                        "cpc": float(insight.get("cpc", 0)),
                        "cpm": float(insight.get("cpm", 0)),
                        "ctr": float(insight.get("ctr", 0)),
                        "conversions": int(insight.get("conversions", 0)),
                        "conversion_value": float(insight.get("conversion_values", 0)),
                        "frequency": float(insight.get("frequency", 0)),
                        "reach": int(insight.get("reach", 0)),
                        "metadata": {
                            "campaign_info": campaign,
                            "raw_insights": insight
                        }
                    }
                    
                    await supabase_client.store_meta_ads_metrics(campaign_metrics)
            
        except Exception as e:
            print(f"Warning: Failed to store Meta Ads metrics to Supabase: {e}")


# Global Meta Ads client
meta_ads_client = MetaAdsClient()


async def test_meta_ads_connection() -> bool:
    """Test Meta Ads API connection"""
    try:
        accounts = await meta_ads_client.get_ad_accounts()
        print(f"✅ Meta Ads connection successful. Found {len(accounts)} ad accounts")
        return True
    except Exception as e:
        print(f"❌ Meta Ads connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test Meta Ads integration
    async def test_meta():
        success = await test_meta_ads_connection()
        if success:
            accounts = await meta_ads_client.get_ad_accounts()
            if accounts:
                account_id = accounts[0]["id"]
                report = await meta_ads_client.get_comprehensive_report(account_id, 7)
                print("Sample report:", json.dumps(report, indent=2))
    
    asyncio.run(test_meta())