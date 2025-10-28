-- Seed data for Stakas MVP development
-- Canal: UCgohgqLVu1QPdfa64Vkrgeg
-- Genre: Drill/Rap Español

INSERT INTO channels (id, name, platform, external_id, genre, country, created_at) VALUES
('stakas-mvp-yt', 'Stakas MVP', 'youtube', 'UCgohgqLVu1QPdfa64Vkrgeg', 'drill_rap_espanol', 'ES', NOW()),
('stakas-mvp-tt', 'Stakas MVP', 'tiktok', '@stakasmvp', 'drill_rap_espanol', 'ES', NOW()),
('stakas-mvp-ig', 'Stakas MVP', 'instagram', '@stakas.mvp', 'drill_rap_espanol', 'ES', NOW());

INSERT INTO campaigns (id, name, platform, channel_id, budget_euros, start_date, end_date, status, created_at) VALUES
('camp-meta-001', 'Stakas MVP Launch Campaign', 'meta_ads', 'stakas-mvp-yt', 500.00, NOW(), NOW() + INTERVAL '30 days', 'active', NOW()),
('camp-organic-001', 'Organic Growth Push', 'cross_platform', 'stakas-mvp-yt', 0.00, NOW(), NOW() + INTERVAL '60 days', 'active', NOW());

INSERT INTO videos (id, title, platform, channel_id, external_id, duration_seconds, views, likes, comments, upload_date, created_at) VALUES
('vid-001', 'Stakas MVP - Primer Track Oficial', 'youtube', 'stakas-mvp-yt', 'dummy_video_1', 180, 15420, 892, 156, NOW() - INTERVAL '7 days', NOW()),
('vid-002', 'Behind the Scenes - Studio Session', 'youtube', 'stakas-mvp-yt', 'dummy_video_2', 240, 8930, 445, 89, NOW() - INTERVAL '5 days', NOW()),
('vid-003', 'Stakas MVP - Freestyle Callejero', 'youtube', 'stakas-mvp-yt', 'dummy_video_3', 120, 12650, 678, 234, NOW() - INTERVAL '3 days', NOW());

INSERT INTO analytics_daily (date, channel_id, platform, views, likes, comments, subscribers, revenue_euros, created_at) VALUES
(CURRENT_DATE - INTERVAL '7 days', 'stakas-mvp-yt', 'youtube', 1200, 89, 23, 145, 0.00, NOW()),
(CURRENT_DATE - INTERVAL '6 days', 'stakas-mvp-yt', 'youtube', 1850, 134, 45, 167, 0.00, NOW()),
(CURRENT_DATE - INTERVAL '5 days', 'stakas-mvp-yt', 'youtube', 2340, 189, 67, 189, 0.00, NOW()),
(CURRENT_DATE - INTERVAL '4 days', 'stakas-mvp-yt', 'youtube', 1980, 156, 43, 203, 0.00, NOW()),
(CURRENT_DATE - INTERVAL '3 days', 'stakas-mvp-yt', 'youtube', 3210, 234, 89, 234, 0.00, NOW()),
(CURRENT_DATE - INTERVAL '2 days', 'stakas-mvp-yt', 'youtube', 2890, 198, 76, 256, 0.00, NOW()),
(CURRENT_DATE - INTERVAL '1 days', 'stakas-mvp-yt', 'youtube', 4120, 298, 134, 289, 0.00, NOW());

INSERT INTO ml_predictions (id, model_name, input_data, prediction_result, confidence, created_at) VALUES
('pred-001', 'engagement_predictor', '{"video_title": "Stakas MVP Track", "genre": "drill_rap"}', '{"predicted_views": 15000, "predicted_engagement": 0.078}', 0.85, NOW()),
('pred-002', 'viral_potential', '{"artist": "Stakas MVP", "genre": "drill_rap_espanol"}', '{"viral_score": 0.73, "peak_day": 5}', 0.79, NOW()),
('pred-003', 'optimal_posting_time', '{"channel": "UCgohgqLVu1QPdfa64Vkrgeg", "genre": "drill_rap"}', '{"hour": 21, "day": "friday", "timezone": "Europe/Madrid"}', 0.82, NOW());

INSERT INTO meta_ads_campaigns (id, name, objective, budget_daily_euros, target_audience, ad_creative, status, created_at) VALUES
('meta-001', 'Stakas MVP - Video Views Campaign', 'VIDEO_VIEWS', 16.67, '{"age_min": 16, "age_max": 28, "interests": ["rap", "drill", "musica_urbana"], "locations": ["ES", "AR", "MX"]}', '{"video_url": "dummy_video_url", "headline": "Nuevo artista de drill español"}', 'ACTIVE', NOW()),
('meta-002', 'Stakas MVP - Traffic Campaign', 'LINK_CLICKS', 10.00, '{"age_min": 18, "age_max": 35, "interests": ["musica", "rap_espanol"], "locations": ["ES"]}', '{"image_url": "dummy_image_url", "headline": "Descubre Stakas MVP"}', 'ACTIVE', NOW());

-- Configuración del sistema
INSERT INTO system_config (key, value, description) VALUES
('channel_primary_id', 'UCgohgqLVu1QPdfa64Vkrgeg', 'Canal principal de YouTube'),
('meta_ads_budget_monthly', '500', 'Presupuesto mensual en Meta Ads (EUR)'),
('target_demographics', '{"age_range": "16-28", "locations": ["ES", "LATAM"], "interests": ["drill", "rap", "musica_urbana"]}', 'Demografía objetivo'),
('optimal_posting_schedule', '{"youtube": "21:00", "tiktok": "19:00", "instagram": "20:30"}', 'Horarios óptimos de publicación'),
('ml_model_versions', '{"engagement": "v2.1", "viral": "v1.8", "posting_time": "v1.5"}', 'Versiones de modelos ML activos');