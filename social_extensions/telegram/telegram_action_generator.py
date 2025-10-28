"""
Telegram Action Generator - ML-Driven Content Generation
Generates optimized content and posting strategies for Telegram groups
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime, timedelta
import random
import json

# ML and data processing
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Import from base action generator
if TYPE_CHECKING:
    from ...ml_core.action_generation.action_generator import ActionGenerator
else:
    try:
        from ...ml_core.action_generation.action_generator import ActionGenerator
    except ImportError:
        # Fallback base class
        class ActionGenerator:
            def __init__(self):
                self.logger = logging.getLogger(__name__)

from ...config.app_settings import is_dummy_mode

class TelegramActionGenerator(ActionGenerator):
    """ML-Driven Telegram Content Generator"""
    
    def __init__(self):
        super().__init__()
        self.dummy_mode = is_dummy_mode()
        self.logger = logging.getLogger(__name__)
        
        # Telegram-specific configuration
        self.max_message_length = 4096
        self.optimal_posting_times = [9, 12, 15, 18, 21]  # Peak hours
        
        # Content templates for different group types
        self.content_templates = {
            "crypto": {
                "promotional": [
                    "🚀 BREAKING: Major crypto update!\n\n📊 Analysis shows {trend}\n💎 Opportunity for {group_name} members\n📈 Current signals pointing to {direction}\n\n⚡ Act fast - limited time window!",
                    "🔥 Crypto Alert for {group_name}!\n\n💰 {asset_name} showing strong momentum\n📊 Technical analysis: {analysis}\n🎯 Target levels: {targets}\n\n💎 Join {members_count}+ smart investors!",
                    "📈 Market Update - {group_name}:\n\n🎯 Today's focus: {focus_area}\n📊 Key levels to watch: {levels}\n💡 Pro tip: {tip}\n\n🤝 Share your thoughts below!"
                ],
                "educational": [
                    "🧠 Crypto Education - {group_name}:\n\n📚 Topic: {topic}\n💡 Key concept: {concept}\n📊 Real example: {example}\n\n❓ Questions? Ask in comments!",
                    "🎓 Daily Learning for {group_name}:\n\n🔍 Understanding: {subject}\n📖 Why it matters: {importance}\n💰 Profit potential: {potential}\n\n📝 Test your knowledge below!",
                    "💎 Crypto Wisdom - {group_name}:\n\n🧮 Formula for success: {formula}\n📊 Historical data shows: {data}\n🎯 Application: {application}\n\n💬 Share your experience!"
                ]
            },
            "marketing": {
                "promotional": [
                    "🚀 Marketing Breakthrough for {group_name}!\n\n📈 New strategy showing {results}% improvement\n💰 Revenue impact: {impact}\n🎯 Perfect for: {target_audience}\n\n🔥 Limited spots available!",
                    "💡 Game-Changer Alert - {group_name}:\n\n🎯 Revolutionary approach to {approach}\n📊 Case study results: {case_results}\n💎 Exclusive access for members\n\n⚡ Grab your spot now!",
                    "📊 Marketing Intel - {group_name}:\n\n🔍 Latest trend: {trend}\n📈 Growth opportunity: {opportunity}\n💰 ROI potential: {roi}\n\n🤝 Join {members_count}+ marketers winning!"
                ],
                "educational": [
                    "📚 Marketing Mastery - {group_name}:\n\n🎯 Today's lesson: {lesson}\n💡 Key insight: {insight}\n📊 Implementation: {implementation}\n\n❓ Questions welcome!",
                    "🧠 Strategy Session - {group_name}:\n\n📖 Focus area: {focus}\n🔍 Deep dive: {deep_dive}\n💰 Monetization: {monetization}\n\n💬 Share your wins!",
                    "🎓 Marketing Education - {group_name}:\n\n📊 Analysis technique: {technique}\n💡 Pro tip: {pro_tip}\n🚀 Scale factor: {scale}\n\n🤝 Help others learn!"
                ]
            },
            "general": {
                "promotional": [
                    "🎉 Exciting News for {group_name}!\n\n✨ New opportunity: {opportunity}\n🎯 Perfect timing for: {timing}\n💎 Exclusive for our {members_count} members\n\n🚀 Don't miss out!",
                    "🔥 Special Announcement - {group_name}:\n\n💰 Limited offer: {offer}\n📊 Success rate: {success_rate}\n🎯 Ideal for: {ideal_for}\n\n⏰ Act quickly!",
                    "📈 Growth Update - {group_name}:\n\n🎯 Milestone reached: {milestone}\n💪 Community power: {power}\n🚀 Next level: {next_level}\n\n🤝 Celebrate with us!"
                ],
                "engagement": [
                    "🗨️ Community Question - {group_name}:\n\n❓ {question}\n💭 Share your thoughts\n🤝 Let's learn together\n\n📊 Poll in comments!",
                    "🎯 Weekly Challenge - {group_name}:\n\n🏆 This week's focus: {focus}\n💪 Your goal: {goal}\n🎉 Reward: {reward}\n\n💬 Who's in?",
                    "🤝 Community Connection - {group_name}:\n\n👥 Introduce yourself\n🎯 Share your expertise\n💡 Help others grow\n\n🌟 Build our network!"
                ]
            }
        }
        
        if self.dummy_mode:
            self.logger.info("🎭 Running Telegram action generator in dummy mode")
    
    async def generate_post_content(self, group_context: Dict[str, Any], 
                                  content_type: str = "promotional") -> Dict[str, Any]:
        """Generate optimized post content for Telegram groups"""
        
        if self.dummy_mode:
            return await self._generate_smart_content(group_context, content_type)
        
        # Real ML-driven content generation
        return await self._generate_ml_content(group_context, content_type)
    
    async def _generate_smart_content(self, group_context: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Generate smart content based on group context"""
        
        group_name = group_context.get("title", "Community")
        members_count = group_context.get("members_count", 1000)
        group_category = self._detect_group_category(group_name, group_context)
        
        # Get appropriate template
        category_templates = self.content_templates.get(group_category, self.content_templates["general"])
        content_templates = category_templates.get(content_type, category_templates.get("promotional", []))
        
        if not content_templates:
            content_templates = self.content_templates["general"]["promotional"]
        
        # Select and customize template
        selected_template = random.choice(content_templates)
        
        # Generate dynamic content based on category
        dynamic_content = self._generate_dynamic_content(group_category, group_context)
        
        # Fill template with dynamic content
        try:
            formatted_content = selected_template.format(
                group_name=group_name,
                members_count=members_count,
                **dynamic_content
            )
        except KeyError:
            # Fallback if template variables don't match
            formatted_content = selected_template.replace("{group_name}", group_name)
            formatted_content = formatted_content.replace("{members_count}", str(members_count))
        
        # Generate additional metadata
        hashtags = await self._generate_contextual_hashtags(group_category, content_type)
        optimal_time = await self._calculate_optimal_time(group_context)
        engagement_prediction = await self._predict_engagement(formatted_content, group_context)
        
        return {
            "content": formatted_content,
            "content_type": content_type,
            "group_category": group_category,
            "estimated_engagement": engagement_prediction,
            "optimal_time": optimal_time,
            "hashtags": hashtags,
            "call_to_action": self._generate_cta(content_type),
            "media_recommendation": self._recommend_media(content_type, group_category),
            "character_count": len(formatted_content),
            "reading_time_seconds": len(formatted_content) // 10,  # Rough estimate
            "sentiment": self._analyze_sentiment(formatted_content)
        }
    
    def _detect_group_category(self, group_name: str, group_context: Dict[str, Any]) -> str:
        """Detect group category based on name and context"""
        
        name_lower = group_name.lower()
        
        # Crypto indicators
        crypto_keywords = ["crypto", "bitcoin", "eth", "trading", "signals", "coin", "defi", "nft"]
        if any(keyword in name_lower for keyword in crypto_keywords):
            return "crypto"
        
        # Marketing indicators  
        marketing_keywords = ["marketing", "business", "entrepreneur", "sales", "growth", "startup"]
        if any(keyword in name_lower for keyword in marketing_keywords):
            return "marketing"
        
        # Check member count for category hints
        members_count = group_context.get("members_count", 0)
        if members_count > 5000:
            # Large groups often crypto or marketing
            if "signal" in name_lower or "trade" in name_lower:
                return "crypto"
            elif "market" in name_lower or "business" in name_lower:
                return "marketing"
        
        return "general"
    
    def _generate_dynamic_content(self, category: str, group_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dynamic content variables based on category"""
        
        if category == "crypto":
            return {
                "trend": random.choice(["bullish momentum", "consolidation phase", "breakout pattern"]),
                "direction": random.choice(["upward", "consolidation", "accumulation zone"]),
                "asset_name": random.choice(["BTC", "ETH", "Major altcoins", "DeFi tokens"]),
                "analysis": random.choice(["strong support levels", "bullish divergence", "volume confirmation"]),
                "targets": random.choice(["$45K-$48K", "key resistance zones", "fibonacci levels"]),
                "focus_area": random.choice(["Bitcoin dominance", "Altcoin season", "Market structure"]),
                "levels": random.choice(["$42K support", "$47K resistance", "MA convergence"]),
                "tip": random.choice(["Dollar-cost averaging", "Risk management", "Position sizing"]),
                "topic": random.choice(["Technical Analysis", "Fundamental Analysis", "Risk Management"]),
                "concept": random.choice(["Support/Resistance", "Market Psychology", "Trend Analysis"]),
                "example": random.choice(["2021 bull run", "2020 accumulation", "DeFi summer"]),
                "subject": random.choice(["Market cycles", "Trading psychology", "Blockchain fundamentals"]),
                "importance": random.choice(["Risk mitigation", "Profit optimization", "Long-term success"]),
                "potential": random.choice(["High with proper risk", "Moderate but steady", "Exponential growth"]),
                "formula": random.choice(["Research + Patience", "Strategy + Discipline", "Knowledge + Action"]),
                "data": random.choice(["70% of traders lose", "HODLers outperform", "DCA beats timing"]),
                "application": random.choice(["Portfolio allocation", "Entry/exit timing", "Risk assessment"])
            }
        
        elif category == "marketing":
            return {
                "results": random.choice(["300", "250", "400"]),
                "impact": random.choice(["$10K monthly", "500% ROI", "2x conversion rate"]),
                "target_audience": random.choice(["e-commerce", "SaaS businesses", "local services"]),
                "approach": random.choice(["content marketing", "social media", "email automation"]),
                "case_results": random.choice(["500% increase", "2M+ views", "$50K revenue"]),
                "trend": random.choice(["AI-powered content", "Video marketing", "Personalization"]),
                "opportunity": random.choice(["Untapped niche", "Emerging platform", "New algorithm"]),
                "roi": random.choice(["300-500%", "10x investment", "Exponential growth"]),
                "lesson": random.choice(["Customer psychology", "Conversion optimization", "Brand building"]),
                "insight": random.choice(["Emotion drives decisions", "Value-first approach", "Consistency wins"]),
                "implementation": random.choice(["A/B testing", "Funnel optimization", "Content strategy"]),
                "focus": random.choice(["Lead generation", "Customer retention", "Brand awareness"]),
                "deep_dive": random.choice(["Psychological triggers", "Data analysis", "Campaign optimization"]),
                "monetization": random.choice(["Subscription model", "Affiliate marketing", "Product sales"]),
                "technique": random.choice(["Cohort analysis", "Attribution modeling", "Conversion tracking"]),
                "pro_tip": random.choice(["Test everything", "Know your numbers", "Focus on LTV"]),
                "scale": random.choice(["Automation systems", "Team building", "Process optimization"])
            }
        
        else:  # general
            return {
                "opportunity": random.choice(["Skill development", "Network building", "Knowledge sharing"]),
                "timing": random.choice(["career growth", "skill building", "networking"]),
                "offer": random.choice(["Free resources", "Exclusive access", "Community benefits"]),
                "success_rate": random.choice(["90%+ satisfaction", "High engagement", "Proven results"]),
                "ideal_for": random.choice(["ambitious learners", "active members", "growth-minded people"]),
                "milestone": random.choice([f"{random.randint(1000, 5000)} members", "100+ success stories", "1 year anniversary"]),
                "power": random.choice(["Collective knowledge", "Shared experiences", "Mutual support"]),
                "next_level": random.choice(["Premium resources", "Expert sessions", "Advanced training"]),
                "question": random.choice(["What's your biggest challenge?", "How can we help you grow?", "What would you like to learn?"]),
                "focus": random.choice(["Personal development", "Skill building", "Goal achievement"]),
                "goal": random.choice(["Learn something new", "Help someone else", "Share your knowledge"]),
                "reward": random.choice(["Recognition", "Special access", "Community spotlight"])
            }
    
    async def _generate_contextual_hashtags(self, category: str, content_type: str) -> List[str]:
        """Generate contextual hashtags based on category and content type"""
        
        base_hashtags = {
            "crypto": ["#crypto", "#bitcoin", "#ethereum", "#trading", "#blockchain", "#defi"],
            "marketing": ["#marketing", "#business", "#growth", "#entrepreneur", "#sales", "#success"],
            "general": ["#community", "#learning", "#growth", "#networking", "#success", "#motivation"]
        }
        
        content_hashtags = {
            "promotional": ["#opportunity", "#exclusive", "#limited", "#special"],
            "educational": ["#education", "#tips", "#knowledge", "#learning"],
            "engagement": ["#discussion", "#community", "#sharing", "#question"]
        }
        
        category_tags = base_hashtags.get(category, base_hashtags["general"])
        type_tags = content_hashtags.get(content_type, [])
        
        # Mix base category tags with content type tags
        selected_tags = random.sample(category_tags, 3) + random.sample(type_tags, 2)
        return selected_tags[:5]  # Limit to 5 hashtags
    
    async def _calculate_optimal_time(self, group_context: Dict[str, Any]) -> int:
        """Calculate optimal posting time based on group analytics"""
        
        # If we have peak hours from analytics, use them
        peak_hours = group_context.get("peak_hours", self.optimal_posting_times)
        
        # Weight current time and peak hours
        current_hour = datetime.now().hour
        
        # Find closest peak hour
        closest_peak = min(peak_hours, key=lambda x: abs(x - current_hour))
        
        return closest_peak
    
    async def _predict_engagement(self, content: str, group_context: Dict[str, Any]) -> float:
        """Predict engagement rate for content"""
        
        base_rate = group_context.get("engagement_rate", 0.15)
        
        # Engagement factors
        factors = 1.0
        
        # Length factor (optimal around 200-400 chars)
        content_length = len(content)
        if 200 <= content_length <= 400:
            factors *= 1.2
        elif content_length > 800:
            factors *= 0.8
        
        # Emoji factor
        emoji_count = sum(1 for char in content if ord(char) > 0x1F600)
        if 3 <= emoji_count <= 8:
            factors *= 1.15
        
        # Call-to-action factor
        cta_words = ["share", "comment", "thoughts", "question", "join", "help"]
        if any(word in content.lower() for word in cta_words):
            factors *= 1.1
        
        # Urgency factor
        urgency_words = ["limited", "exclusive", "now", "today", "urgent"]
        if any(word in content.lower() for word in urgency_words):
            factors *= 1.05
        
        return min(base_rate * factors, 1.0)  # Cap at 100%
    
    def _generate_cta(self, content_type: str) -> str:
        """Generate call-to-action based on content type"""
        
        ctas = {
            "promotional": [
                "💬 Comment if interested!",
                "🚀 Join us now!",
                "⚡ Don't miss out!",
                "🎯 Secure your spot!"
            ],
            "educational": [
                "💭 Share your thoughts!",
                "❓ Questions welcome!",
                "📝 What's your experience?",
                "🤝 Help others learn!"
            ],
            "engagement": [
                "💬 Join the discussion!",
                "🗨️ Share below!",
                "🤝 Let's connect!",
                "🎯 What do you think?"
            ]
        }
        
        return random.choice(ctas.get(content_type, ctas["engagement"]))
    
    def _recommend_media(self, content_type: str, category: str) -> Optional[str]:
        """Recommend media type for content"""
        
        media_recommendations = {
            ("crypto", "promotional"): "chart_image",
            ("crypto", "educational"): "infographic", 
            ("marketing", "promotional"): "success_screenshot",
            ("marketing", "educational"): "diagram",
            ("general", "promotional"): "announcement_image",
            ("general", "educational"): "infographic",
            ("general", "engagement"): None
        }
        
        return media_recommendations.get((category, content_type))
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of content"""
        
        positive_words = ["amazing", "great", "excellent", "success", "win", "opportunity", "growth"]
        negative_words = ["problem", "issue", "difficult", "challenge", "fail", "loss"]
        
        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def _generate_ml_content(self, group_context: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Generate ML-driven content (production mode)"""
        # In production, this would use actual ML models
        # For now, return enhanced smart content
        return await self._generate_smart_content(group_context, content_type)
    
    async def optimize_posting_schedule(self, group_analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimal posting schedule based on group analytics"""
        
        peak_hours = group_analytics.get("peak_hours", [10, 14, 19, 21])
        engagement_rate = group_analytics.get("engagement_rate", 0.15)
        members_count = group_analytics.get("members_count", 1000)
        
        # Determine posting frequency based on engagement and size
        if engagement_rate > 0.2 and members_count > 5000:
            frequency = "4_times_daily"
            daily_posts = 4
        elif engagement_rate > 0.15 or members_count > 2000:
            frequency = "3_times_daily" 
            daily_posts = 3
        else:
            frequency = "2_times_daily"
            daily_posts = 2
        
        # Content mix based on performance
        content_mix = {
            "promotional": 0.4 if engagement_rate > 0.15 else 0.3,
            "educational": 0.4 if engagement_rate > 0.15 else 0.5,
            "engagement": 0.2
        }
        
        return {
            "recommended_times": peak_hours[:daily_posts],
            "posting_frequency": frequency,
            "daily_posts": daily_posts,
            "content_mix": content_mix,
            "optimal_intervals": {
                "morning": f"{peak_hours[0] if peak_hours else 9}:00",
                "afternoon": f"{peak_hours[1] if len(peak_hours) > 1 else 14}:00", 
                "evening": f"{peak_hours[2] if len(peak_hours) > 2 else 19}:00"
            },
            "weekly_schedule": await self._generate_weekly_schedule(peak_hours, daily_posts),
            "engagement_optimization": {
                "best_day": "Wednesday",
                "avoid_times": ["02:00-06:00", "23:00-01:00"],
                "peak_engagement_window": f"{peak_hours[0] if peak_hours else 19}:00-{peak_hours[0]+2 if peak_hours else 21}:00"
            }
        }
    
    async def _generate_weekly_schedule(self, peak_hours: List[int], daily_posts: int) -> Dict[str, List]:
        """Generate detailed weekly posting schedule"""
        
        schedule = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        content_rotation = ["promotional", "educational", "engagement", "promotional"]
        
        for i, day in enumerate(days):
            daily_schedule = []
            
            # Adjust posting times for weekends
            if day in ["Saturday", "Sunday"]:
                adjusted_hours = [h + 1 for h in peak_hours[:daily_posts]]  # Later on weekends
            else:
                adjusted_hours = peak_hours[:daily_posts]
            
            for j, hour in enumerate(adjusted_hours):
                content_type = content_rotation[j % len(content_rotation)]
                priority = "high" if j == 0 else "medium"
                
                daily_schedule.append({
                    "time": f"{hour:02d}:00",
                    "content_type": content_type,
                    "priority": priority,
                    "estimated_reach": self._calculate_reach_estimate(hour, day, content_type)
                })
            
            schedule[day] = daily_schedule
        
        return schedule
    
    def _calculate_reach_estimate(self, hour: int, day: str, content_type: str) -> int:
        """Estimate reach for specific time and content type"""
        
        base_reach = 100
        
        # Hour multiplier
        if 9 <= hour <= 11 or 14 <= hour <= 16 or 19 <= hour <= 21:
            hour_multiplier = 1.5
        elif 12 <= hour <= 13 or 17 <= hour <= 18:
            hour_multiplier = 1.2
        else:
            hour_multiplier = 0.8
        
        # Day multiplier
        if day in ["Wednesday", "Thursday", "Friday"]:
            day_multiplier = 1.3
        elif day in ["Tuesday", "Saturday"]:
            day_multiplier = 1.1
        else:
            day_multiplier = 0.9
        
        # Content type multiplier
        content_multiplier = {
            "promotional": 1.1,
            "educational": 1.4,
            "engagement": 1.2
        }.get(content_type, 1.0)
        
        return int(base_reach * hour_multiplier * day_multiplier * content_multiplier)
    
    async def analyze_content_performance(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance of different content types"""
        
        if not messages:
            return self._get_default_performance_analysis()
        
        # Analyze message performance
        performance_by_type = {}
        time_performance = {}
        
        for message in messages:
            content_type = message.get("content_type", "unknown")
            engagement = message.get("engagement", {})
            timestamp = message.get("timestamp", datetime.now().isoformat())
            
            # Parse timestamp and get hour
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
            except:
                hour = 12  # Default
            
            # Calculate engagement rate
            views = engagement.get("views", 1)
            reactions = engagement.get("reactions", 0)
            replies = engagement.get("replies", 0)
            
            engagement_rate = (reactions + replies) / max(views, 1)
            
            # Store by content type
            if content_type not in performance_by_type:
                performance_by_type[content_type] = []
            performance_by_type[content_type].append(engagement_rate)
            
            # Store by time
            if hour not in time_performance:
                time_performance[hour] = []
            time_performance[hour].append(engagement_rate)
        
        # Calculate averages
        avg_by_type = {
            content_type: sum(rates) / len(rates) 
            for content_type, rates in performance_by_type.items()
        }
        
        avg_by_time = {
            hour: sum(rates) / len(rates)
            for hour, rates in time_performance.items()
        }
        
        # Find best performing elements
        best_content_type = max(avg_by_type.items(), key=lambda x: x[1])[0] if avg_by_type else "educational"
        best_times = sorted(avg_by_time.items(), key=lambda x: x[1], reverse=True)[:3]
        best_hours = [hour for hour, _ in best_times]
        
        return {
            "top_performing_content": best_content_type,
            "engagement_by_type": avg_by_type,
            "best_posting_times": best_hours,
            "performance_summary": {
                "total_messages_analyzed": len(messages),
                "avg_engagement_rate": sum(avg_by_type.values()) / len(avg_by_type) if avg_by_type else 0.15,
                "improvement_opportunities": self._generate_improvement_recommendations(avg_by_type, best_hours)
            },
            "content_recommendations": self._generate_content_recommendations(avg_by_type, best_content_type),
            "time_recommendations": {
                "optimal_hours": best_hours,
                "avoid_hours": self._get_low_performance_hours(avg_by_time),
                "peak_window": f"{best_hours[0]:02d}:00-{best_hours[0]+2:02d}:00" if best_hours else "19:00-21:00"
            }
        }
    
    def _get_default_performance_analysis(self) -> Dict[str, Any]:
        """Return default performance analysis when no data available"""
        
        return {
            "top_performing_content": "educational",
            "engagement_by_type": {
                "promotional": 0.12,
                "educational": 0.18,
                "engagement": 0.15
            },
            "best_posting_times": [14, 19, 21],
            "performance_summary": {
                "total_messages_analyzed": 0,
                "avg_engagement_rate": 0.15,
                "improvement_opportunities": [
                    "Increase educational content ratio",
                    "Post during peak hours (14:00, 19:00, 21:00)",
                    "Add more interactive elements"
                ]
            },
            "content_recommendations": [
                "Focus on educational content (18% avg engagement)",
                "Include more interactive elements",
                "Use visual aids and infographics",
                "Ask questions to drive engagement"
            ],
            "time_recommendations": {
                "optimal_hours": [14, 19, 21],
                "avoid_hours": [2, 3, 4, 5, 6],
                "peak_window": "19:00-21:00"
            }
        }
    
    def _generate_improvement_recommendations(self, performance_by_type: Dict[str, float], best_hours: List[int]) -> List[str]:
        """Generate improvement recommendations based on performance data"""
        
        recommendations = []
        
        if not performance_by_type:
            return ["Collect more performance data for better recommendations"]
        
        # Content type recommendations
        best_type = max(performance_by_type.items(), key=lambda x: x[1])[0]
        worst_type = min(performance_by_type.items(), key=lambda x: x[1])[0]
        
        recommendations.append(f"Increase {best_type} content ratio for better engagement")
        
        if performance_by_type[worst_type] < 0.1:
            recommendations.append(f"Improve {worst_type} content quality or reduce frequency")
        
        # Timing recommendations
        if best_hours:
            recommendations.append(f"Schedule more content during peak hours: {', '.join(f'{h}:00' for h in best_hours[:3])}")
        
        # General recommendations
        avg_engagement = sum(performance_by_type.values()) / len(performance_by_type)
        if avg_engagement < 0.15:
            recommendations.append("Overall engagement is low - consider more interactive content")
        
        return recommendations
    
    def _generate_content_recommendations(self, performance_by_type: Dict[str, float], best_type: str) -> List[str]:
        """Generate specific content recommendations"""
        
        recommendations = []
        
        if best_type == "educational":
            recommendations.extend([
                "Continue focus on educational content (highest engagement)",
                "Create tutorial-style posts",
                "Share industry insights and tips",
                "Use infographics and visual explanations"
            ])
        elif best_type == "promotional":
            recommendations.extend([
                "Promotional content performs well - maintain balance",
                "Include clear value propositions",
                "Use urgency and scarcity effectively",
                "Add social proof and testimonials"
            ])
        else:  # engagement
            recommendations.extend([
                "Interactive content drives engagement",
                "Ask more questions to community",
                "Create polls and discussions", 
                "Encourage user-generated content"
            ])
        
        # Add general recommendations
        recommendations.extend([
            "Use 3-5 relevant hashtags per post",
            "Include clear call-to-action",
            "Optimize post length (200-400 characters)",
            "Use emojis strategically (3-8 per post)"
        ])
        
        return recommendations
    
    def _get_low_performance_hours(self, time_performance: Dict[int, float]) -> List[int]:
        """Get hours with low engagement performance"""
        
        if not time_performance:
            return [2, 3, 4, 5, 6]  # Default low hours
        
        avg_performance = sum(time_performance.values()) / len(time_performance)
        low_hours = [hour for hour, perf in time_performance.items() if perf < avg_performance * 0.7]
        
        return sorted(low_hours)
    
    async def generate_hashtag_strategy(self, group_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive hashtag strategy"""
        
        group_name = group_context.get("title", "")
        group_category = self._detect_group_category(group_name, group_context)
        members_count = group_context.get("members_count", 1000)
        
        hashtag_strategies = {
            "crypto": {
                "primary": ["#crypto", "#bitcoin", "#ethereum", "#trading"],
                "secondary": ["#blockchain", "#defi", "#altcoins", "#hodl", "#btc", "#eth"],
                "trending": ["#web3", "#nft", "#metaverse", "#dao"]
            },
            "marketing": {
                "primary": ["#marketing", "#business", "#entrepreneur", "#growth"],
                "secondary": ["#sales", "#startup", "#success", "#leadership", "#innovation", "#strategy"],
                "trending": ["#digitalmarketing", "#socialmedia", "#ai", "#automation"]
            },
            "general": {
                "primary": ["#community", "#networking", "#learning", "#growth"],
                "secondary": ["#success", "#motivation", "#tips", "#knowledge", "#sharing", "#support"],
                "trending": ["#skills", "#development", "#career", "#innovation"]
            }
        }
        
        strategy = hashtag_strategies.get(group_category, hashtag_strategies["general"])
        
        # Adjust strategy based on group size
        if members_count > 10000:
            # Large groups can use more competitive hashtags
            max_hashtags = 5
            trending_weight = 0.3
        elif members_count > 1000:
            max_hashtags = 4
            trending_weight = 0.2
        else:
            # Smaller groups should focus on niche hashtags
            max_hashtags = 3
            trending_weight = 0.1
        
        return {
            "primary_hashtags": strategy["primary"][:2],
            "secondary_hashtags": strategy["secondary"][:3],
            "trending_hashtags": strategy["trending"][:2],
            "strategy_rules": {
                "max_per_post": max_hashtags,
                "mix_formula": "2_primary + 2_secondary + 1_trending",
                "placement": "end_of_message",
                "trending_weight": trending_weight,
                "rotation_frequency": "weekly"
            },
            "performance_tracking": {
                "track_reach": True,
                "track_engagement": True,
                "a_b_test": True,
                "optimize_weekly": True
            },
            "category_specific_tips": self._get_hashtag_tips(group_category)
        }
    
    def _get_hashtag_tips(self, category: str) -> List[str]:
        """Get category-specific hashtag tips"""
        
        tips_by_category = {
            "crypto": [
                "Use asset-specific hashtags (#BTC, #ETH) for targeted content",
                "Include trading-related tags during market analysis",
                "Avoid overusing pump-related hashtags",
                "Mix technical and fundamental analysis tags"
            ],
            "marketing": [
                "Use industry-specific hashtags (#B2B, #SaaS, #ecommerce)",
                "Include outcome-based tags (#ROI, #conversion, #growth)",
                "Mix strategy and tactical hashtags",
                "Use platform-specific tags when relevant"
            ],
            "general": [
                "Focus on community-building hashtags",
                "Use skill and development related tags",
                "Include motivational and inspirational hashtags",
                "Mix broad and niche community tags"
            ]
        }
        
        return tips_by_category.get(category, tips_by_category["general"])
    
    async def _get_trending_hashtags(self, category: str) -> List[str]:
        """Get current trending hashtags for category"""
        
        # In production, this would analyze real trend data
        trending_by_category = {
            "crypto": ["#altseason", "#defi2024", "#btchalving", "#cryptoadoption"],
            "marketing": ["#aimarketing", "#contentcreator", "#digitalstrategy", "#conversionrate"],
            "general": ["#skillbuilding", "#networking2024", "#personaldevelopment", "#careergrowth"]
        }
        
        return trending_by_category.get(category, ["#trending", "#popular", "#community"])
    
    async def generate_campaign_strategy(self, campaign_goals: Dict[str, Any], group_contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive campaign strategy for multiple groups"""
        
        total_reach = sum(group.get("members_count", 0) for group in group_contexts)
        avg_engagement = sum(group.get("engagement_rate", 0.15) for group in group_contexts) / len(group_contexts)
        
        # Determine campaign approach based on goals
        campaign_type = campaign_goals.get("type", "awareness")
        duration_days = campaign_goals.get("duration", 7)
        
        strategy = {
            "campaign_overview": {
                "type": campaign_type,
                "duration": f"{duration_days} days",
                "target_groups": len(group_contexts),
                "estimated_reach": total_reach,
                "expected_engagement_rate": avg_engagement
            },
            "content_calendar": await self._generate_campaign_calendar(duration_days, group_contexts),
            "group_specific_strategies": await self._generate_group_strategies(group_contexts, campaign_type),
            "success_metrics": {
                "primary_kpis": self._get_campaign_kpis(campaign_type),
                "tracking_schedule": "Daily monitoring with weekly reports",
                "optimization_triggers": self._get_optimization_triggers(campaign_type)
            },
            "budget_allocation": await self._calculate_budget_allocation(group_contexts, campaign_type),
            "risk_mitigation": {
                "rate_limiting": "5-second delays between group posts",
                "content_variations": "3+ versions per message",
                "fallback_groups": "20% backup group list",
                "monitoring_alerts": "Real-time engagement tracking"
            }
        }
        
        return strategy
    
    async def _generate_campaign_calendar(self, days: int, group_contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed campaign calendar"""
        
        calendar = {}
        content_types = ["promotional", "educational", "engagement"]
        
        for day in range(1, days + 1):
            day_key = f"day_{day}"
            
            # Determine daily theme
            if day <= 2:
                theme = "awareness"
                primary_content = "educational"
            elif day <= days - 2:
                theme = "engagement"
                primary_content = "engagement"
            else:
                theme = "conversion"
                primary_content = "promotional"
            
            calendar[day_key] = {
                "theme": theme,
                "primary_content_type": primary_content,
                "posting_schedule": self._generate_daily_schedule(len(group_contexts)),
                "content_variations": 3,  # Number of content variations to create
                "success_targets": {
                    "min_engagement_rate": 0.12 if day <= 2 else 0.15,
                    "target_reach": len(group_contexts) * 0.8,  # 80% successful posts
                    "interaction_goal": "10+ reactions per group"
                }
            }
        
        return calendar
    
    def _generate_daily_schedule(self, num_groups: int) -> List[Dict[str, Any]]:
        """Generate daily posting schedule for campaign"""
        
        # Stagger posts across peak hours to avoid spam detection
        peak_hours = [10, 14, 18, 21]
        
        schedule = []
        groups_per_hour = max(1, num_groups // len(peak_hours))
        
        for i, hour in enumerate(peak_hours):
            start_group = i * groups_per_hour
            end_group = min((i + 1) * groups_per_hour, num_groups)
            
            if start_group < num_groups:
                schedule.append({
                    "time": f"{hour:02d}:00",
                    "groups": list(range(start_group, end_group)),
                    "delay_between_posts": 30,  # seconds
                    "content_variation": f"variation_{i + 1}"
                })
        
        return schedule
    
    async def _generate_group_strategies(self, group_contexts: List[Dict[str, Any]], campaign_type: str) -> Dict[str, Any]:
        """Generate specific strategies for each group"""
        
        strategies = {}
        
        for i, group in enumerate(group_contexts):
            group_id = group.get("id", f"group_{i}")
            group_category = self._detect_group_category(group.get("title", ""), group)
            
            strategies[str(group_id)] = {
                "group_name": group.get("title", f"Group {i+1}"),
                "category": group_category,
                "members": group.get("members_count", 1000),
                "engagement_rate": group.get("engagement_rate", 0.15),
                "content_focus": self._get_content_focus(group_category, campaign_type),
                "posting_frequency": self._calculate_posting_frequency(group),
                "optimization_approach": self._get_optimization_approach(group),
                "success_metrics": {
                    "target_engagement": group.get("engagement_rate", 0.15) * 1.2,  # 20% improvement
                    "reach_goal": group.get("members_count", 1000) * 0.3,  # 30% reach
                    "interaction_target": max(10, group.get("members_count", 1000) // 100)
                }
            }
        
        return strategies
    
    def _get_content_focus(self, category: str, campaign_type: str) -> str:
        """Get content focus based on group category and campaign type"""
        
        focus_matrix = {
            ("crypto", "awareness"): "Educational crypto content with market insights",
            ("crypto", "engagement"): "Interactive trading discussions and Q&A",
            ("crypto", "conversion"): "Exclusive trading signals and premium content",
            ("marketing", "awareness"): "Business growth tips and success stories",
            ("marketing", "engagement"): "Case studies and strategy discussions",
            ("marketing", "conversion"): "Tool recommendations and course promotions",
            ("general", "awareness"): "Community value and knowledge sharing",
            ("general", "engagement"): "Interactive discussions and networking",
            ("general", "conversion"): "Premium community access and resources"
        }
        
        return focus_matrix.get((category, campaign_type), "General valuable content")
    
    def _calculate_posting_frequency(self, group: Dict[str, Any]) -> str:
        """Calculate optimal posting frequency for group"""
        
        engagement_rate = group.get("engagement_rate", 0.15)
        members_count = group.get("members_count", 1000)
        
        if engagement_rate > 0.2 and members_count > 5000:
            return "3_times_daily"
        elif engagement_rate > 0.15 or members_count > 2000:
            return "2_times_daily"
        else:
            return "1_time_daily"
    
    def _get_optimization_approach(self, group: Dict[str, Any]) -> str:
        """Get optimization approach for specific group"""
        
        engagement_rate = group.get("engagement_rate", 0.15)
        
        if engagement_rate > 0.2:
            return "maintain_quality"
        elif engagement_rate > 0.1:
            return "improve_engagement"
        else:
            return "rebuild_connection"
    
    def _get_campaign_kpis(self, campaign_type: str) -> List[str]:
        """Get KPIs for campaign type"""
        
        kpi_mapping = {
            "awareness": ["Reach", "Impressions", "New member engagement", "Content shares"],
            "engagement": ["Comments", "Reactions", "Discussion threads", "User-generated content"],
            "conversion": ["Click-through rate", "Sign-ups", "Sales", "Lead generation"]
        }
        
        return kpi_mapping.get(campaign_type, kpi_mapping["awareness"])
    
    def _get_optimization_triggers(self, campaign_type: str) -> List[str]:
        """Get optimization triggers for campaign type"""
        
        triggers = {
            "awareness": ["Low reach (<50% target)", "Poor engagement (<10% rate)", "High negative feedback"],
            "engagement": ["Declining interaction", "Low comment rate", "Reduced sharing"],
            "conversion": ["Poor CTR (<2%)", "Low conversion rate", "High cost per acquisition"]
        }
        
        return triggers.get(campaign_type, triggers["awareness"])
    
    async def _calculate_budget_allocation(self, group_contexts: List[Dict[str, Any]], campaign_type: str) -> Dict[str, Any]:
        """Calculate budget allocation across groups"""
        
        total_reach = sum(group.get("members_count", 0) for group in group_contexts)
        
        allocations = {}
        for group in group_contexts:
            group_id = str(group.get("id", "unknown"))
            group_reach = group.get("members_count", 1000)
            group_engagement = group.get("engagement_rate", 0.15)
            
            # Weight by reach and engagement
            weight = (group_reach / total_reach) * (1 + group_engagement)
            
            allocations[group_id] = {
                "reach_percentage": round((group_reach / total_reach) * 100, 1),
                "engagement_weight": round(group_engagement, 3),
                "recommended_budget_percentage": round(weight * 100, 1),
                "priority": "high" if group_engagement > 0.2 else "medium" if group_engagement > 0.1 else "low"
            }
        
        return {
            "group_allocations": allocations,
            "strategy_summary": {
                "high_priority_groups": len([a for a in allocations.values() if a["priority"] == "high"]),
                "total_estimated_reach": total_reach,
                "budget_distribution": "Weighted by reach and engagement rate"
            }
        }

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import json

from config.app_settings import is_dummy_mode
from orchestration.actions.action_generator import ActionGenerator

logger = logging.getLogger(__name__)

@dataclass
class TelegramGroupAnalytics:
    """Analytics data for a Telegram group"""
    group_id: int
    group_name: str
    members_count: int
    messages_count: int
    avg_engagement_rate: float
    peak_activity_hours: List[int]
    top_keywords: List[str]
    sentiment_score: float
    growth_rate: float

@dataclass 
class TelegramContentRecommendation:
    """Content recommendation for Telegram posting"""
    content_type: str  # text, media, poll, etc.
    suggested_text: str
    optimal_timing: datetime
    target_groups: List[int]
    expected_engagement: float
    hashtags: List[str]
    reasoning: str

@dataclass
class TelegramOptimizationAction:
    """Optimization action for Telegram management"""
    action_type: str  # join_group, leave_group, schedule_post, etc.
    target_group: Optional[int]
    parameters: Dict[str, Any]
    priority: float
    expected_impact: str
    reasoning: str

class TelegramActionGenerator(ActionGenerator):
    """Generates ML-driven actions for Telegram automation"""
    
    def __init__(self, telegram_automator=None):
        super().__init__()
        self.platform = "telegram"
        self.automator = telegram_automator
        
        # ML model configurations
        self.engagement_threshold = 0.05
        self.growth_target = 0.1  # 10% monthly growth
        self.optimal_posting_frequency = 3  # posts per day
        
        # Tracking
        self.group_analytics: Dict[int, TelegramGroupAnalytics] = {}
        self.content_performance: List[Dict] = []
        self.action_history: List[TelegramOptimizationAction] = []
        
        if is_dummy_mode():
            logger.info("🤖 Telegram Action Generator initialized in dummy mode")
    
    async def analyze_group_performance(
        self,
        group_id: int,
        days: int = 7
    ) -> TelegramGroupAnalytics:
        """Analyze performance metrics for a specific group"""
        if is_dummy_mode():
            return self._generate_dummy_analytics(group_id)
            
        if not self.automator:
            logger.error("Telegram automator not available")
            return self._generate_dummy_analytics(group_id)
        
        try:
            # Get group info
            groups = await self.automator.get_groups()
            group_info = next((g for g in groups if g.id == group_id), None)
            
            if not group_info:
                logger.error(f"Group {group_id} not found")
                return self._generate_dummy_analytics(group_id)
            
            # Get recent messages
            messages = await self.automator.get_group_messages(
                group_id, 
                limit=200,
                offset_date=datetime.now() - timedelta(days=days)
            )
            
            # Analyze engagement patterns
            engagement_rates = []
            keywords_count = {}
            activity_hours = [0] * 24
            
            for message in messages:
                # Get metrics for each message
                metrics = await self.automator.get_post_metrics(group_id, message.id)
                if metrics:
                    # Calculate engagement rate
                    engagement_rate = (metrics.views + metrics.forwards * 2) / max(group_info.members_count, 1)
                    engagement_rates.append(engagement_rate)
                
                # Track activity hours
                hour = message.date.hour
                activity_hours[hour] += 1
                
                # Extract keywords (simple approach)
                words = message.text.lower().split()
                for word in words:
                    if len(word) > 3 and word.isalpha():
                        keywords_count[word] = keywords_count.get(word, 0) + 1
            
            # Calculate analytics
            avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
            peak_hours = sorted(range(24), key=lambda x: activity_hours[x], reverse=True)[:3]
            top_keywords = sorted(keywords_count.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Estimate sentiment (dummy calculation)
            sentiment_score = 0.6 + (avg_engagement * 0.8)  # Simplified
            
            # Calculate growth rate (dummy for now)
            growth_rate = 0.05  # Would need historical data
            
            analytics = TelegramGroupAnalytics(
                group_id=group_id,
                group_name=group_info.title,
                members_count=group_info.members_count,
                messages_count=len(messages),
                avg_engagement_rate=avg_engagement,
                peak_activity_hours=peak_hours,
                top_keywords=[word for word, _ in top_keywords],
                sentiment_score=sentiment_score,
                growth_rate=growth_rate
            )
            
            self.group_analytics[group_id] = analytics
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to analyze group {group_id}: {e}")
            return self._generate_dummy_analytics(group_id)
    
    async def generate_content_recommendations(
        self,
        group_ids: List[int],
        content_themes: Optional[List[str]] = None
    ) -> List[TelegramContentRecommendation]:
        """Generate ML-driven content recommendations"""
        if is_dummy_mode():
            return self._generate_dummy_recommendations(group_ids)
        
        recommendations = []
        
        for group_id in group_ids:
            try:
                # Analyze group first
                analytics = await self.analyze_group_performance(group_id)
                
                # Generate recommendations based on analytics
                peak_hour = analytics.peak_activity_hours[0] if analytics.peak_activity_hours else 12
                optimal_time = datetime.now().replace(hour=peak_hour, minute=0, second=0, microsecond=0)
                
                # If it's past the peak hour today, schedule for tomorrow
                if optimal_time < datetime.now():
                    optimal_time += timedelta(days=1)
                
                # Generate content based on top keywords
                if analytics.top_keywords:
                    suggested_text = self._generate_content_from_keywords(
                        analytics.top_keywords[:3],
                        content_themes
                    )
                else:
                    suggested_text = self._generate_default_content(content_themes)
                
                recommendation = TelegramContentRecommendation(
                    content_type="text",
                    suggested_text=suggested_text,
                    optimal_timing=optimal_time,
                    target_groups=[group_id],
                    expected_engagement=min(analytics.avg_engagement_rate * 1.2, 1.0),
                    hashtags=self._extract_hashtags(analytics.top_keywords),
                    reasoning=f"Based on peak activity at {peak_hour}:00 and trending keywords"
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Failed to generate recommendations for group {group_id}: {e}")
        
        return recommendations
    
    async def generate_optimization_actions(
        self,
        target_metrics: Optional[Dict[str, float]] = None
    ) -> List[TelegramOptimizationAction]:
        """Generate optimization actions based on performance analysis"""
        if is_dummy_mode():
            return self._generate_dummy_actions()
        
        actions = []
        
        # Default target metrics
        if not target_metrics:
            target_metrics = {
                "engagement_rate": 0.1,
                "growth_rate": 0.05,
                "posting_frequency": 2.0
            }
        
        try:
            # Analyze all managed groups
            if self.automator:
                groups = await self.automator.get_groups()
                
                for group in groups:
                    analytics = await self.analyze_group_performance(group.id)
                    
                    # Check if engagement is below target
                    if analytics.avg_engagement_rate < target_metrics["engagement_rate"]:
                        action = TelegramOptimizationAction(
                            action_type="increase_posting_frequency",
                            target_group=group.id,
                            parameters={
                                "current_frequency": 1.0,
                                "target_frequency": 2.5,
                                "content_types": ["text", "media"]
                            },
                            priority=0.8,
                            expected_impact="15-25% engagement increase",
                            reasoning=f"Group engagement ({analytics.avg_engagement_rate:.3f}) below target ({target_metrics['engagement_rate']})"
                        )
                        actions.append(action)
                    
                    # Check if growth is stagnant
                    if analytics.growth_rate < target_metrics["growth_rate"]:
                        action = TelegramOptimizationAction(
                            action_type="cross_promotion",
                            target_group=group.id,
                            parameters={
                                "promotion_groups": self._find_similar_groups(analytics),
                                "promotion_message": "Check out this amazing community!"
                            },
                            priority=0.6,
                            expected_impact="10-20% member growth",
                            reasoning=f"Group growth ({analytics.growth_rate:.3f}) below target"
                        )
                        actions.append(action)
                    
                    # Optimize posting times
                    if analytics.peak_activity_hours:
                        action = TelegramOptimizationAction(
                            action_type="optimize_posting_schedule",
                            target_group=group.id,
                            parameters={
                                "optimal_hours": analytics.peak_activity_hours,
                                "current_schedule": "random",
                                "new_schedule": f"Daily at {analytics.peak_activity_hours[0]}:00"
                            },
                            priority=0.7,
                            expected_impact="20-30% visibility increase",
                            reasoning="Align posting with peak activity hours"
                        )
                        actions.append(action)
            
            # Sort by priority
            actions.sort(key=lambda x: x.priority, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to generate optimization actions: {e}")
        
        return actions
    
    async def execute_action(self, action: TelegramOptimizationAction) -> bool:
        """Execute a specific optimization action"""
        if is_dummy_mode():
            logger.info(f"🤖 Executing dummy action: {action.action_type}")
            return True
        
        if not self.automator:
            logger.error("Telegram automator not available")
            return False
        
        try:
            if action.action_type == "increase_posting_frequency":
                # Schedule more posts for the group
                return await self._schedule_frequent_posts(action)
                
            elif action.action_type == "cross_promotion":
                # Cross-promote between groups
                return await self._execute_cross_promotion(action)
                
            elif action.action_type == "optimize_posting_schedule":
                # Update posting schedule
                return await self._optimize_posting_schedule(action)
                
            elif action.action_type == "join_group":
                # Join a new group
                group_link = action.parameters.get("group_link")
                if group_link:
                    return await self.automator.join_group(group_link)
                    
            elif action.action_type == "leave_group":
                # Leave an underperforming group
                if action.target_group:
                    return await self.automator.leave_group(action.target_group)
            
            # Record successful action
            self.action_history.append(action)
            logger.info(f"✅ Executed action: {action.action_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute action {action.action_type}: {e}")
            return False
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """Get ML-driven insights about Telegram performance"""
        if is_dummy_mode():
            return self._get_dummy_insights()
        
        if not self.group_analytics:
            return {"status": "No data available"}
        
        # Aggregate analytics
        total_groups = len(self.group_analytics)
        avg_engagement = sum(a.avg_engagement_rate for a in self.group_analytics.values()) / total_groups
        total_members = sum(a.members_count for a in self.group_analytics.values())
        
        # Find best performing groups
        best_groups = sorted(
            self.group_analytics.values(),
            key=lambda x: x.avg_engagement_rate,
            reverse=True
        )[:3]
        
        # Identify optimization opportunities
        underperforming_groups = [
            a for a in self.group_analytics.values()
            if a.avg_engagement_rate < self.engagement_threshold
        ]
        
        return {
            "total_groups": total_groups,
            "total_members": total_members,
            "avg_engagement_rate": avg_engagement,
            "best_performing_groups": [
                {"name": g.group_name, "engagement": g.avg_engagement_rate}
                for g in best_groups
            ],
            "optimization_opportunities": len(underperforming_groups),
            "recommended_actions": len(self.action_history),
            "peak_activity_pattern": self._analyze_activity_patterns(),
            "growth_trend": "positive" if avg_engagement > self.engagement_threshold else "needs_improvement"
        }
    
    # Helper methods
    def _generate_content_from_keywords(
        self,
        keywords: List[str],
        themes: Optional[List[str]] = None
    ) -> str:
        """Generate content based on trending keywords"""
        if themes:
            theme = themes[0]
            return f"🔥 Trending: {', '.join(keywords)} in {theme}! What do you think about the latest developments? Share your thoughts below! 💭"
        else:
            return f"🚀 Hot topic: {', '.join(keywords)}! Join the discussion and let us know your perspective! 👇"
    
    def _generate_default_content(self, themes: Optional[List[str]] = None) -> str:
        """Generate default engaging content"""
        if themes:
            theme = themes[0]
            return f"💡 Let's discuss {theme}! What's your experience with this topic? Share your insights with the community! 🤝"
        else:
            return "🌟 Community check-in! How's everyone doing today? Share what's on your mind! 💬"
    
    def _extract_hashtags(self, keywords: List[str]) -> List[str]:
        """Extract relevant hashtags from keywords"""
        return [f"#{word}" for word in keywords[:5] if len(word) > 3]
    
    def _find_similar_groups(self, analytics: TelegramGroupAnalytics) -> List[int]:
        """Find similar groups for cross-promotion"""
        # Simple similarity based on keywords overlap
        similar = []
        for group_id, other_analytics in self.group_analytics.items():
            if group_id != analytics.group_id:
                # Check keyword overlap
                common_keywords = set(analytics.top_keywords) & set(other_analytics.top_keywords)
                if len(common_keywords) >= 2:  # At least 2 common keywords
                    similar.append(group_id)
        
        return similar[:3]  # Return top 3 similar groups
    
    def _analyze_activity_patterns(self) -> Dict[str, Any]:
        """Analyze activity patterns across all groups"""
        if not self.group_analytics:
            return {}
        
        # Aggregate peak hours
        all_peak_hours = []
        for analytics in self.group_analytics.values():
            all_peak_hours.extend(analytics.peak_activity_hours)
        
        # Count frequency of each hour
        hour_counts = {}
        for hour in all_peak_hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Find most common peak hours
        top_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "global_peak_hours": [hour for hour, _ in top_hours],
            "activity_distribution": hour_counts,
            "most_active_period": f"{top_hours[0][0]}:00" if top_hours else "Unknown"
        }
    
    async def _schedule_frequent_posts(self, action: TelegramOptimizationAction) -> bool:
        """Schedule more frequent posts for a group"""
        if not action.target_group:
            return False
        
        # Generate content recommendations
        recommendations = await self.generate_content_recommendations([action.target_group])
        
        # Schedule posts based on recommendations
        for rec in recommendations[:3]:  # Schedule up to 3 posts
            success = await self.automator.schedule_post(
                action.target_group,
                rec.suggested_text,
                rec.optimal_timing
            )
            if not success:
                return False
        
        return True
    
    async def _execute_cross_promotion(self, action: TelegramOptimizationAction) -> bool:
        """Execute cross-promotion between groups"""
        promotion_groups = action.parameters.get("promotion_groups", [])
        message = action.parameters.get("promotion_message", "")
        
        if not promotion_groups or not message:
            return False
        
        # Send promotion message to related groups
        results = await self.automator.bulk_post(
            promotion_groups,
            message,
            delay_between_posts=120  # 2 minutes delay
        )
        
        return all(results.values())
    
    async def _optimize_posting_schedule(self, action: TelegramOptimizationAction) -> bool:
        """Optimize posting schedule for a group"""
        # This would integrate with a task scheduler in production
        # For now, we'll just log the optimization
        optimal_hours = action.parameters.get("optimal_hours", [])
        
        logger.info(f"Optimized posting schedule for group {action.target_group}: {optimal_hours}")
        return True
    
    # Dummy mode methods
    def _generate_dummy_analytics(self, group_id: int) -> TelegramGroupAnalytics:
        """Generate dummy analytics for testing"""
        return TelegramGroupAnalytics(
            group_id=group_id,
            group_name=f"Test Group {group_id}",
            members_count=1500,
            messages_count=450,
            avg_engagement_rate=0.08,
            peak_activity_hours=[9, 14, 20],
            top_keywords=["crypto", "trading", "blockchain", "defi", "nft"],
            sentiment_score=0.75,
            growth_rate=0.03
        )
    
    def _generate_dummy_recommendations(self, group_ids: List[int]) -> List[TelegramContentRecommendation]:
        """Generate dummy content recommendations"""
        recommendations = []
        
        for group_id in group_ids:
            rec = TelegramContentRecommendation(
                content_type="text",
                suggested_text="🚀 What's your take on the latest market trends? Share your insights! 💭 #crypto #trading",
                optimal_timing=datetime.now() + timedelta(hours=2),
                target_groups=[group_id],
                expected_engagement=0.12,
                hashtags=["#crypto", "#trading", "#discussion"],
                reasoning="Based on peak activity patterns and trending keywords"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_dummy_actions(self) -> List[TelegramOptimizationAction]:
        """Generate dummy optimization actions"""
        return [
            TelegramOptimizationAction(
                action_type="increase_posting_frequency",
                target_group=1001,
                parameters={"target_frequency": 3},
                priority=0.8,
                expected_impact="20% engagement increase",
                reasoning="Low engagement detected"
            ),
            TelegramOptimizationAction(
                action_type="optimize_posting_schedule",
                target_group=1002,
                parameters={"optimal_hours": [9, 14, 20]},
                priority=0.7,
                expected_impact="25% visibility increase",
                reasoning="Posting outside peak hours"
            )
        ]
    
    def _get_dummy_insights(self) -> Dict[str, Any]:
        """Generate dummy performance insights"""
        return {
            "total_groups": 8,
            "total_members": 12500,
            "avg_engagement_rate": 0.09,
            "best_performing_groups": [
                {"name": "Crypto Trading Pro", "engagement": 0.15},
                {"name": "DeFi Discussions", "engagement": 0.12},
                {"name": "NFT Community", "engagement": 0.10}
            ],
            "optimization_opportunities": 3,
            "recommended_actions": 5,
            "peak_activity_pattern": {
                "global_peak_hours": [9, 14, 20],
                "most_active_period": "14:00"
            },
            "growth_trend": "positive"
        }

# Factory function for dependency injection
def create_telegram_action_generator(**kwargs) -> TelegramActionGenerator:
    """Create TelegramActionGenerator instance with dependency injection"""
    return TelegramActionGenerator(**kwargs)