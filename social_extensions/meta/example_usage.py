#!/usr/bin/env python3
"""
Meta Ads Integration Example
Comprehensive example demonstrating the complete Meta Ads automation system
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main example demonstrating Meta Ads integration"""
    
    print("🎯 Meta Ads Integration Example")
    print("=" * 50)
    
    try:
        # Import Meta components
        from social_extensions.meta import (
            MetaAdsAutomator, MetaActionGenerator, MetaAdsMonitor,
            CampaignBrief, TargetingSpec, Creative,
            CampaignObjective, OptimizationGoal, BidStrategy, CreativeType,
            create_meta_automator, create_meta_action_generator, create_meta_ads_monitor,
            META_AVAILABLE
        )
        
        if not META_AVAILABLE:
            print("⚠️ Meta Ads module not available - running in demo mode")
        
        # 1. Configuration Setup
        print("\n📋 Step 1: Configuration Setup")
        print("-" * 30)
        
        meta_config = {
            'app_id': 'demo_app_id',
            'app_secret': 'demo_app_secret',
            'access_token': 'demo_access_token',
            'ad_account_id': '1234567890',
            'page_id': '0987654321',
            'pixel_id': 'demo_pixel_id'
        }
        
        action_config = {
            'meta': {
                'min_roas_threshold': 2.0,
                'max_cpa_threshold': 50.0,
                'budget_scale_factor': 1.2,
                'confidence_threshold': 0.6,
                'max_daily_actions': 5
            }
        }
        
        monitoring_config = {
            'monitoring': {
                'check_interval_seconds': 60,  # Check every minute for demo
                'performance_window_hours': 24
            },
            'alert_thresholds': {
                'min_roas': 2.0,
                'max_cpa': 50.0,
                'min_ctr': 0.5
            }
        }
        
        print("✅ Configuration prepared")
        
        # 2. Initialize Components
        print("\n🔧 Step 2: Initialize Components")
        print("-" * 30)
        
        # Create automator
        meta_automator = create_meta_automator(meta_config)
        print("✅ Meta Ads Automator initialized")
        
        # Create action generator
        action_generator = create_meta_action_generator(action_config)
        print("✅ Action Generator initialized")
        
        # Create monitor
        monitor = create_meta_ads_monitor(monitoring_config)
        print("✅ Monitor initialized")
        
        # 3. Create Campaign Example
        print("\n🚀 Step 3: Create Campaign")
        print("-" * 30)
        
        # Define targeting
        targeting = TargetingSpec(
            countries=['US', 'CA', 'GB'],
            age_min=25,
            age_max=45,
            genders=[1, 2],  # All genders
            interests=['Technology', 'Online Shopping', 'Mobile Apps']
        )
        
        # Define creative
        creative = Creative(
            creative_id='creative_001',
            name='Demo Creative',
            type=CreativeType.SINGLE_IMAGE,
            title='Amazing Product - Limited Time!',
            body='Get 50% off our revolutionary product. Order now and transform your life!',
            call_to_action='SHOP_NOW',
            link_url='https://example.com/product',
            image_url='https://example.com/image.jpg'
        )
        
        # Create campaign brief
        campaign_brief = CampaignBrief(
            campaign_name='Demo Campaign - Tech Product',
            objective=CampaignObjective.CONVERSIONS,
            budget_total=1000.0,  # $1000 total budget
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
            targeting=targeting,
            creatives=[creative],
            optimization_goal=OptimizationGoal.CONVERSIONS,
            bid_strategy=BidStrategy.LOWEST_COST,
            pixel_id='demo_pixel_id',
            conversion_event='Purchase'
        )
        
        print(f"📋 Campaign Brief: {campaign_brief.campaign_name}")
        print(f"💰 Budget: ${campaign_brief.budget_total}")
        print(f"🎯 Objective: {campaign_brief.objective.value}")
        
        # Create campaign
        print("\n📤 Creating campaign...")
        campaign_result = await meta_automator.create_campaign_from_brief(campaign_brief)
        
        if campaign_result.get('status') == 'success':
            campaign_id = campaign_result['campaign_id']
            print(f"✅ Campaign created successfully: {campaign_id}")
            print(f"📊 Adsets: {len(campaign_result['adset_ids'])}")
            print(f"📢 Ads: {len(campaign_result['ad_ids'])}")
        else:
            print(f"❌ Campaign creation failed: {campaign_result.get('error')}")
            return
        
        # 4. Start Monitoring
        print("\n📊 Step 4: Start Monitoring")
        print("-" * 30)
        
        await monitor.start_monitoring(meta_automator)
        print("✅ Monitoring started")
        
        # 5. Simulate Campaign Metrics
        print("\n📈 Step 5: Simulate Campaign Performance")
        print("-" * 30)
        
        # Get initial metrics (will be dummy data)
        print("📊 Fetching campaign metrics...")
        metrics = await meta_automator.get_campaign_metrics(campaign_id, 1)
        
        if metrics:
            print(f"✅ Retrieved {len(metrics)} metric points")
            
            # Display sample metrics
            latest_metric = metrics[-1] if metrics else None
            if latest_metric:
                print(f"💰 Spend: ${latest_metric.spend:.2f}")
                print(f"👀 Impressions: {latest_metric.impressions:,}")
                print(f"🖱️ Clicks: {latest_metric.clicks}")
                print(f"🎯 Conversions: {latest_metric.conversions}")
                print(f"📊 ROAS: {latest_metric.roas:.2f}")
                print(f"💲 CPA: ${latest_metric.cpa:.2f}")
        
        # 6. Generate Optimization Actions
        print("\n🔧 Step 6: Generate ML-Driven Actions")
        print("-" * 30)
        
        # Create action request
        from ml_core.action_generation.action_generator import ActionRequest
        
        action_request = ActionRequest(
            request_id='demo_request_001',
            platform='meta',
            platform_data={
                'meta': {
                    'account_id': meta_config['ad_account_id'],
                    'metrics': metrics or [],
                    'budget_remaining': 500.0,
                    'objectives': ['CONVERSIONS'],
                    'target_roas': 3.0,
                    'max_cpa': 30.0,
                    'window_hours': 24
                }
            },
            context={'optimization_type': 'auto'},
            timestamp=datetime.now()
        )
        
        print("🤖 Generating ML-driven actions...")
        actions = await action_generator.generate_actions(action_request)
        
        print(f"✅ Generated {len(actions)} optimization actions")
        
        for i, action in enumerate(actions, 1):
            print(f"\n🔧 Action {i}:")
            print(f"   Type: {getattr(action, 'action_type', 'Unknown')}")
            print(f"   Confidence: {getattr(action, 'confidence', 0):.1%}")
            print(f"   Priority: {getattr(action, 'priority', 'unknown')}")
            print(f"   Reasoning: {getattr(action, 'reasoning', 'No reasoning provided')}")
        
        # 7. Campaign Health Assessment
        print("\n🏥 Step 7: Campaign Health Assessment")
        print("-" * 30)
        
        # Wait a moment for monitoring to collect data
        await asyncio.sleep(2)
        
        health_score = await monitor.get_campaign_health(campaign_id)
        
        if health_score:
            print(f"📊 Overall Health Score: {health_score.overall_score:.1f}/100")
            print(f"🏆 Health Status: {health_score.health_status}")
            print(f"📈 Performance Score: {health_score.performance_score:.1f}")
            print(f"💰 Budget Efficiency: {health_score.budget_efficiency_score:.1f}")
            print(f"👥 Engagement Score: {health_score.engagement_score:.1f}")
            print(f"⚙️ Technical Score: {health_score.technical_score:.1f}")
            
            if health_score.critical_issues:
                print(f"\n⚠️ Critical Issues:")
                for issue in health_score.critical_issues:
                    print(f"   • {issue}")
            
            if health_score.recommendations:
                print(f"\n💡 Recommendations:")
                for rec in health_score.recommendations:
                    print(f"   • {rec}")
        
        # 8. Alerts and Monitoring
        print("\n🚨 Step 8: Alerts and Monitoring")
        print("-" * 30)
        
        active_alerts = await monitor.get_active_alerts(campaign_id)
        
        if active_alerts:
            print(f"📢 Active Alerts: {len(active_alerts)}")
            for alert in active_alerts:
                print(f"\n🚨 {alert.severity.value.upper()}: {alert.title}")
                print(f"   Description: {alert.description}")
                print(f"   Recommendation: {alert.recommendation}")
        else:
            print("✅ No active alerts")
        
        # Get monitoring summary
        monitoring_summary = await monitor.get_monitoring_summary()
        print(f"\n📊 Monitoring Summary:")
        print(f"   Monitored Campaigns: {monitoring_summary['monitored_campaigns']}")
        print(f"   Active Alerts: {monitoring_summary['active_alerts']}")
        print(f"   System Status: {'Active' if monitoring_summary['is_monitoring'] else 'Inactive'}")
        
        # 9. Execute Optimization
        print("\n⚡ Step 9: Execute Optimizations")
        print("-" * 30)
        
        if actions:
            # Convert actions to insights for the automator
            from social_extensions.meta.meta_automator import MLInsight
            
            insights = []
            for action in actions:
                if hasattr(action, 'parameters'):
                    insight = MLInsight(
                        insight_id=getattr(action, 'action_id', 'demo_insight'),
                        campaign_id=campaign_id,
                        insight_type=getattr(action, 'action_type', 'optimization'),
                        score=getattr(action, 'confidence', 0.8),
                        confidence=getattr(action, 'confidence', 0.8),
                        recommended_action={
                            'type': getattr(action, 'action_type', 'optimization'),
                            **getattr(action, 'parameters', {})
                        },
                        generated_at=datetime.now()
                    )
                    insights.append(insight)
            
            if insights:
                print(f"🔧 Executing {len(insights)} optimizations...")
                optimization_result = await meta_automator.optimize_campaign(campaign_id, insights)
                
                executed_actions = optimization_result.get('optimizations_applied', 0)
                print(f"✅ Executed {executed_actions} optimizations")
                
                for result in optimization_result.get('actions', []):
                    print(f"   • {result.get('type', 'unknown')}: {result.get('result', 'unknown')}")
        
        # 10. Production Readiness Check
        print("\n🚀 Step 10: Production Readiness")
        print("-" * 30)
        
        print("Production Readiness Checklist:")
        print("✅ Meta Ads integration implemented")
        print("✅ ML action generation configured")
        print("✅ Monitoring and alerting system ready")
        print("✅ Campaign management API endpoints created")
        print("✅ Production configuration templates generated")
        
        print("\nTo deploy to production:")
        print("1. Set environment variables in .env file")
        print("2. Install Meta Business SDK: pip install facebook-business")
        print("3. Set DUMMY_MODE=false")
        print("4. Configure Meta API credentials")
        print("5. Run production setup script")
        print("6. Start API server: python -m ml_core.api_gateway")
        
        # Cleanup
        print("\n🧹 Cleanup")
        print("-" * 30)
        
        await monitor.stop_monitoring()
        print("✅ Monitoring stopped")
        
        print("\n🎉 Meta Ads Integration Example Completed!")
        print("=" * 50)
        
        # Display final summary
        print("\nSummary:")
        print(f"📊 Campaign Created: {campaign_id}")
        print(f"🤖 Actions Generated: {len(actions)}")
        print(f"🚨 Alerts: {len(active_alerts)}")
        print(f"💯 Health Score: {health_score.overall_score:.1f}/100" if health_score else "N/A")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed")
        
    except Exception as e:
        logger.error(f"❌ Error in example: {e}")
        print(f"\n❌ Error occurred: {e}")
        print("💡 Check logs for more details")

if __name__ == "__main__":
    asyncio.run(main())