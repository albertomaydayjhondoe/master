"""
📋 PLAN DE ACCIÓN ESPECÍFICO - CANAL UCgohgqLVu1QPdfa64Vkrgeg
Estrategia día a día con Meta Ads €500/mes
"""

from datetime import datetime, timedelta
import json

class DailyActionPlan:
    """Plan detallado de acciones diarias"""
    
    def __init__(self):
        self.start_date = datetime(2025, 10, 28)  # Hoy
        self.channel_id = "UCgohgqLVu1QPdfa64Vkrgeg"
        
    def generate_30_day_plan(self):
        """Genera plan específico de 30 días"""
        
        plan = {}
        
        for day in range(1, 31):
            date = self.start_date + timedelta(days=day-1)
            day_name = date.strftime("%A")
            date_str = date.strftime("%Y-%m-%d")
            
            daily_actions = self.get_daily_actions(day, day_name, date_str)
            plan[f"day_{day:02d}"] = daily_actions
        
        return plan
    
    def get_daily_actions(self, day_num, day_name, date_str):
        """Acciones específicas para cada día"""
        
        # Meta Ads setup (días 1-3)
        if day_num <= 3:
            meta_ads_action = self.get_meta_ads_setup_actions(day_num)
        else:
            meta_ads_action = self.get_meta_ads_optimization_actions(day_num)
        
        # Acciones base para todos los días
        base_actions = {
            "date": date_str,
            "day_name": day_name,
            "day_number": day_num,
            
            # Meta Ads
            "meta_ads": meta_ads_action,
            
            # Morning routine
            "08:00_trending_check": {
                "action": "Check trending hashtags",
                "platforms": ["TikTok", "Twitter", "Instagram"],
                "focus": "Music trends España/LATAM",
                "time_investment": "15 min",
                "tools": "Trend analysis ML"
            },
            
            "09:00_morning_tweet": {
                "action": "Publish morning music insight",
                "platform": "Twitter",
                "content_type": "Quote/Insight/Industry news",
                "hashtags": ["#music", "#producer", "#artist"],
                "expected_engagement": "5-15 interactions"
            },
            
            "10:00_analytics_review": {
                "action": "Review previous day performance",
                "metrics_to_check": [
                    "YouTube channel analytics",
                    "Instagram insights", 
                    "TikTok analytics",
                    "Twitter impressions",
                    "Meta Ads performance"
                ],
                "time_investment": "20 min"
            },
            
            # Content creation
            "11:00_content_creation": self.get_content_creation_action(day_name),
            
            # Afternoon engagement
            "13:00_lunch_engagement": {
                "action": "Twitter trending participation",
                "focus": "Music hashtags trending",
                "interactions": "2-3 tweets",
                "engagement_targets": "Music community accounts"
            },
            
            "15:00_competitor_research": {
                "action": "Research competitors and trends",
                "focus": "Similar music channels España/LATAM",
                "analysis": "Content performing well, timing, hashtags",
                "time_investment": "30 min"
            },
            
            # Evening prime time
            "17:00_meta_ads_check": {
                "action": "Monitor and adjust Meta Ads",
                "tasks": [
                    "Check CPC and reach",
                    "Adjust targeting if needed",
                    "Review landing page performance",
                    "Optimize budget allocation"
                ],
                "time_investment": "15 min"
            },
            
            "19:00_instagram_post": self.get_instagram_post_action(day_name, day_num),
            
            "20:30_tiktok_post": self.get_tiktok_post_action(day_name, day_num),
            
            "21:00_engagement_session": {
                "action": "Cross-platform community engagement",
                "duration": "60 minutes",
                "breakdown": {
                    "instagram": "20 min - likes, comments, stories",
                    "tiktok": "15 min - comments, likes, follows",
                    "youtube": "15 min - comment responses, community",
                    "twitter": "10 min - replies, retweets, engagement"
                },
                "targets": "Music community, potential collaborators, fans"
            },
            
            "22:30_daily_planning": {
                "action": "Review day and plan tomorrow",
                "tasks": [
                    "Log performance metrics",
                    "Plan next day content",
                    "Note trending opportunities",
                    "Update content calendar"
                ],
                "time_investment": "15 min"
            }
        }
        
        # Agregar acciones específicas por día de semana
        weekly_specific = self.get_weekly_specific_actions(day_name, day_num)
        base_actions.update(weekly_specific)
        
        return base_actions
    
    def get_meta_ads_setup_actions(self, day_num):
        """Acciones de setup Meta Ads primeros 3 días"""
        
        if day_num == 1:
            return {
                "phase": "Launch",
                "budget_today": "€16.67",
                "actions": [
                    "Create campaign targeting España 35% + México 25%",
                    "Setup age targeting: 18-34 (80% audience)",
                    "Interest targeting: música, reggaeton, pop, entretenimiento",
                    "Ad creative: YouTube channel trailer/best content",
                    "Landing page: YouTube channel optimizado"
                ],
                "expected_results": "200-400 nuevas visitas canal"
            }
        elif day_num == 2:
            return {
                "phase": "Monitor & Adjust",
                "budget_today": "€16.67", 
                "actions": [
                    "Review day 1 performance metrics",
                    "Adjust targeting if CPC > €0.15",
                    "A/B test ad creative variations",
                    "Monitor channel subscriber growth"
                ],
                "expected_results": "250-450 nuevas visitas canal"
            }
        else:  # day_num == 3
            return {
                "phase": "Optimize",
                "budget_today": "€16.67",
                "actions": [
                    "Optimize best performing audiences",
                    "Expand successful interest categories", 
                    "Test video vs. image ads performance",
                    "Setup retargeting for channel visitors"
                ],
                "expected_results": "300-500 nuevas visitas canal"
            }
    
    def get_meta_ads_optimization_actions(self, day_num):
        """Acciones de optimización Meta Ads ongoing"""
        
        week = (day_num - 1) // 7 + 1
        
        return {
            "phase": f"Optimization Week {week}",
            "budget_today": "€16.67",
            "actions": [
                "Monitor CPC and adjust bids",
                "Refresh ad creative if frequency > 2.5",
                "Test new audience interests",
                "Analyze conversion to subscribers"
            ],
            "expected_results": f"280-480 nuevas visitas canal (semana {week})"
        }
    
    def get_content_creation_action(self, day_name):
        """Sesión de creación de contenido por día"""
        
        content_schedule = {
            "Monday": {
                "focus": "TikTok challenge research + YouTube Shorts",
                "deliverables": ["TikTok video script", "YouTube Short edit"],
                "time": "45 min"
            },
            "Tuesday": {
                "focus": "Instagram content + YouTube community",
                "deliverables": ["Instagram post + stories", "YouTube community post"],
                "time": "60 min"
            },
            "Wednesday": {
                "focus": "Music content + YouTube Shorts",
                "deliverables": ["Original music snippet", "YouTube Short"],
                "time": "45 min"
            },
            "Thursday": {
                "focus": "Behind scenes + Community content",
                "deliverables": ["Instagram stories series", "YouTube community post"],
                "time": "30 min"
            },
            "Friday": {
                "focus": "Main YouTube video preparation",
                "deliverables": ["YouTube main video edit/upload prep"],
                "time": "90 min"
            },
            "Saturday": {
                "focus": "Weekend content + Collaboration prep",
                "deliverables": ["Weekend casual content", "Outreach messages"],
                "time": "45 min"
            },
            "Sunday": {
                "focus": "Week review + Next week planning",
                "deliverables": ["Content calendar update", "Performance analysis"],
                "time": "60 min"
            }
        }
        
        return {
            "action": "Content creation session",
            "focus": content_schedule[day_name]["focus"],
            "deliverables": content_schedule[day_name]["deliverables"],
            "time_investment": content_schedule[day_name]["time"]
        }
    
    def get_instagram_post_action(self, day_name, day_num):
        """Post específico de Instagram por día"""
        
        content_types = [
            "Music studio session photo",
            "Behind the scenes video", 
            "Fan interaction/repost",
            "Music quote graphic",
            "Lifestyle/personal moment",
            "Music equipment/setup",
            "Collaboration announcement"
        ]
        
        content_type = content_types[day_num % len(content_types)]
        
        return {
            "action": "Instagram feed post",
            "content_type": content_type,
            "optimal_time": "19:00",
            "hashtags": [
                "#music", "#producer", "#artist", "#studio", "#newmusic",
                "#spain", "#madrid", "#mexico", "#reggaeton", "#pop"
            ],
            "expected_reach": "1,500-3,500 accounts",
            "expected_engagement": "120-280 likes, 15-35 comments",
            "stories_followup": "3-4 stories promoting the post"
        }
    
    def get_tiktok_post_action(self, day_name, day_num):
        """Post específico de TikTok por día"""
        
        video_concepts = [
            "Music snippet with trending sound",
            "Studio behind the scenes",
            "Music production process",
            "Fan interaction response",
            "Trending challenge participation", 
            "Music tutorial/tips",
            "Day in the life of musician"
        ]
        
        concept = video_concepts[day_num % len(video_concepts)]
        
        return {
            "action": "TikTok video post",
            "concept": concept,
            "optimal_time": "20:30",
            "hashtags": [
                "#fyp", "#music", "#producer", "#viral", "#spain", 
                "#mexico", "#reggaeton", "#pop", "#studio", "#newmusic"
            ],
            "expected_views": "2,000-8,000 views",
            "expected_engagement": "150-400 interactions",
            "trending_sounds": "Use current trending audio"
        }
    
    def get_weekly_specific_actions(self, day_name, day_num):
        """Acciones específicas por día de semana"""
        
        weekly_actions = {}
        
        if day_name == "Monday":
            weekly_actions["19:30_youtube_short"] = {
                "action": "Upload YouTube Short",
                "content": "Music Monday - trending song snippet",
                "expected_views": "800-2,500 views"
            }
        
        elif day_name == "Tuesday":
            weekly_actions["18:00_youtube_community"] = {
                "action": "YouTube community post",
                "content": "Music poll or behind scenes update",
                "expected_engagement": "50-150 interactions"
            }
        
        elif day_name == "Wednesday":
            weekly_actions["19:30_youtube_short"] = {
                "action": "Upload YouTube Short", 
                "content": "Studio session or music tip",
                "expected_views": "800-2,500 views"
            }
        
        elif day_name == "Thursday":
            weekly_actions["18:00_youtube_community"] = {
                "action": "YouTube community post",
                "content": "Fan question response or music update",
                "expected_engagement": "50-150 interactions"
            }
        
        elif day_name == "Friday":
            weekly_actions["20:00_youtube_main"] = {
                "action": "Upload main YouTube video",
                "content": "Main music content/video/collab",
                "expected_views": "1,500-4,000 views primera semana"
            }
            weekly_actions["19:30_youtube_short"] = {
                "action": "Upload YouTube Short",
                "content": "Friday music vibes",
                "expected_views": "1,200-3,500 views"
            }
        
        elif day_name in ["Saturday", "Sunday"]:
            weekly_actions["weekend_engagement"] = {
                "action": "Enhanced weekend community engagement",
                "focus": "More personal interaction with fans",
                "time_investment": "Extra 30 min",
                "platforms": "All platforms - casual interactions"
            }
        
        return weekly_actions
    
    def calculate_weekly_projections(self, week_num):
        """Proyecciones por semana"""
        
        base_growth = {
            1: {"subs": "80-120", "views": "4,500-7,000", "engagement": "3.5-4.2%"},
            2: {"subs": "95-140", "views": "5,200-8,500", "engagement": "4.0-4.8%"},
            3: {"subs": "110-160", "views": "6,000-10,000", "engagement": "4.5-5.5%"},
            4: {"subs": "125-180", "views": "6,800-11,500", "engagement": "5.0-6.2%"}
        }
        
        return base_growth.get(week_num, base_growth[4])

def main():
    """Genera plan completo"""
    
    planner = DailyActionPlan()
    
    print("📋 Generando plan de acción 30 días...")
    daily_plan = planner.generate_30_day_plan()
    
    # Guardar plan
    plan_dir = Path("data/execution")
    plan_dir.mkdir(parents=True, exist_ok=True)
    
    with open(plan_dir / "30_day_action_plan.json", 'w', encoding='utf-8') as f:
        json.dump(daily_plan, f, indent=2, ensure_ascii=False)
    
    print("\n" + "🎯" * 60)
    print("📋 PLAN DE ACCIÓN 30 DÍAS - CANAL UCgohgqLVu1QPdfa64Vkrgeg")
    print("🎯" * 60)
    
    # Mostrar primeros 3 días como ejemplo
    for day in [1, 2, 3]:
        day_key = f"day_{day:02d}"
        day_data = daily_plan[day_key]
        
        print(f"\n📅 DÍA {day} ({day_data['date']}) - {day_data['day_name']}")
        print("─" * 50)
        
        print(f"💰 Meta Ads: {day_data['meta_ads']['phase']} - {day_data['meta_ads']['budget_today']}")
        print(f"   Expected: {day_data['meta_ads']['expected_results']}")
        
        print(f"📱 Contenido clave:")
        print(f"   • 19:00: {day_data['19:00_instagram_post']['content_type']}")
        print(f"   • 20:30: {day_data['20:30_tiktok_post']['concept']}")
        
        if 'youtube_main' in str(day_data):
            print(f"   • YouTube: Main video upload")
        elif 'youtube_short' in str(day_data):
            print(f"   • YouTube: Short video upload")
        
        print(f"⏰ Tiempo total invertido: ~4-5 horas")
    
    # Proyecciones semanales
    print(f"\n📊 PROYECCIONES SEMANALES:")
    for week in range(1, 5):
        projections = planner.calculate_weekly_projections(week)
        print(f"   Semana {week}: {projections['subs']} subs, {projections['views']} views, {projections['engagement']} engagement")
    
    print(f"\n🎯 OBJETIVOS MES 1:")
    print(f"   • Meta Ads investment: €500")
    print(f"   • Nuevos suscriptores: 360-540")
    print(f"   • Views adicionales: 18,000-28,000")
    print(f"   • ROI esperado: 70-140%")
    print(f"   • Engagement rate: De 3.2% a 5.8-7.2%")
    
    print(f"\n📋 PLAN GUARDADO EN: data/execution/30_day_action_plan.json")
    print("✅ READY TO EXECUTE!")

if __name__ == "__main__":
    from pathlib import Path
    main()