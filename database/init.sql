-- ═══════════════════════════════════════════════════════════════════════════
-- init.sql - Database Initialization for Docker V3
-- ═══════════════════════════════════════════════════════════════════════════

-- Create databases
CREATE DATABASE IF NOT EXISTS community_manager;
CREATE DATABASE IF NOT EXISTS n8n;

-- Connect to community_manager database
\c community_manager;

-- ═════════════════════════════════════════════════════════════════════════
-- 📊 CAMPAIGNS TABLE
-- ═════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    video_path VARCHAR(500),
    target_platform VARCHAR(100),
    target_views INTEGER,
    organic_budget DECIMAL(10, 2),
    paid_budget DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    launched_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_created_at ON campaigns(created_at);

-- ═════════════════════════════════════════════════════════════════════════
-- 📱 ACCOUNTS TABLE
-- ═════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    platform VARCHAR(50) NOT NULL,
    account_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    is_shadowbanned BOOLEAN DEFAULT FALSE,
    last_health_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_accounts_platform ON accounts(platform);
CREATE INDEX idx_accounts_status ON accounts(status);

-- ═════════════════════════════════════════════════════════════════════════
-- 📊 METRICS TABLE
-- ═════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    platform VARCHAR(50),
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_campaign_id ON metrics(campaign_id);
CREATE INDEX idx_metrics_account_id ON metrics(account_id);
CREATE INDEX idx_metrics_created_at ON metrics(created_at);

-- ═════════════════════════════════════════════════════════════════════════
-- 🤖 ML PREDICTIONS TABLE
-- ═════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS ml_predictions (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    prediction_type VARCHAR(50),
    prediction_value JSONB,
    confidence DECIMAL(5, 4),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ml_predictions_campaign_id ON ml_predictions(campaign_id);
CREATE INDEX idx_ml_predictions_type ON ml_predictions(prediction_type);

-- ═════════════════════════════════════════════════════════════════════════
-- 💰 META ADS TABLE
-- ═════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS meta_ads_campaigns (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    meta_campaign_id VARCHAR(255),
    meta_adset_id VARCHAR(255),
    meta_ad_id VARCHAR(255),
    budget DECIMAL(10, 2),
    spend DECIMAL(10, 2) DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_meta_ads_campaign_id ON meta_ads_campaigns(campaign_id);
CREATE INDEX idx_meta_ads_status ON meta_ads_campaigns(status);

-- ═════════════════════════════════════════════════════════════════════════
-- 📊 PIXEL EVENTS TABLE
-- ═════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS pixel_events (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    event_name VARCHAR(100),
    event_data JSONB,
    user_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pixel_events_campaign_id ON pixel_events(campaign_id);
CREATE INDEX idx_pixel_events_name ON pixel_events(event_name);

-- ═════════════════════════════════════════════════════════════════════════
-- 🎥 YOUTUBE UPLOADS TABLE
-- ═════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS youtube_uploads (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    video_id VARCHAR(255),
    video_url VARCHAR(500),
    title VARCHAR(255),
    description TEXT,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_youtube_campaign_id ON youtube_uploads(campaign_id);
CREATE INDEX idx_youtube_status ON youtube_uploads(status);

-- ═════════════════════════════════════════════════════════════════════════
-- 🔄 N8N WORKFLOW EXECUTIONS TABLE
-- ═════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS n8n_executions (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255),
    execution_id VARCHAR(255),
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    status VARCHAR(50),
    execution_data JSONB,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_n8n_workflow_id ON n8n_executions(workflow_id);
CREATE INDEX idx_n8n_campaign_id ON n8n_executions(campaign_id);

-- ═════════════════════════════════════════════════════════════════════════
-- 📱 DEVICE FARM ACTIONS TABLE
-- ═════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS device_actions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    device_id VARCHAR(100),
    action_type VARCHAR(50),
    action_data JSONB,
    success BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_device_actions_account_id ON device_actions(account_id);
CREATE INDEX idx_device_actions_campaign_id ON device_actions(campaign_id);

-- ═════════════════════════════════════════════════════════════════════════
-- 🚨 ALERTS TABLE
-- ═════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    message TEXT,
    metadata JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_resolved ON alerts(resolved);

-- ═════════════════════════════════════════════════════════════════════════
-- 📈 INSERT SAMPLE DATA (Development/Testing)
-- ═════════════════════════════════════════════════════════════════════════

-- Sample accounts
INSERT INTO accounts (username, platform, account_type, status) VALUES
('viral_music_1', 'tiktok', 'creator', 'active'),
('viral_music_2', 'tiktok', 'creator', 'active'),
('viral_music_3', 'instagram', 'creator', 'active'),
('viral_music_4', 'instagram', 'creator', 'active'),
('viral_music_5', 'tiktok', 'creator', 'active')
ON CONFLICT (username) DO NOTHING;

-- Sample campaign
INSERT INTO campaigns (name, target_platform, target_views, organic_budget, paid_budget, status) VALUES
('Test Campaign', 'tiktok', 100000, 0, 100.00, 'pending')
ON CONFLICT DO NOTHING;

-- ═════════════════════════════════════════════════════════════════════════
-- ✅ SETUP COMPLETE
-- ═════════════════════════════════════════════════════════════════════════

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE community_manager TO postgres;
GRANT ALL PRIVILEGES ON DATABASE n8n TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Done
SELECT 'Database initialized successfully' AS status;
