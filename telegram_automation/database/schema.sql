-- ==================== LIKE4LIKE BOT DATABASE SCHEMA ====================
-- Schema para sistema de automatización de intercambios Like4Like
-- Soporta Telegram, Discord, WhatsApp y YouTube automation

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== CONTACTS TABLE ====================
-- Almacena todos los contactos descubiertos en grupos
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL, -- Telegram/Discord user ID
    username VARCHAR(255),
    display_name VARCHAR(255),
    platform VARCHAR(50) NOT NULL DEFAULT 'telegram', -- telegram, discord, whatsapp
    
    -- Contact discovery info
    discovered_at TIMESTAMP DEFAULT NOW(),
    discovered_in_group VARCHAR(255), -- Nombre del grupo donde se encontró
    discovered_in_group_id BIGINT, -- ID del grupo
    original_message TEXT, -- Mensaje original que detectamos
    original_video_url TEXT, -- URL del video que posteó
    
    -- Contact status and reliability
    status VARCHAR(50) DEFAULT 'discovered', -- discovered, contacted, responded, active_saved, unresponsive, blocked
    reliability_score INTEGER DEFAULT 50, -- 0-100, starts at 50
    total_exchanges INTEGER DEFAULT 0,
    successful_exchanges INTEGER DEFAULT 0,
    failed_exchanges INTEGER DEFAULT 0,
    
    -- Communication tracking
    first_contact_at TIMESTAMP,
    last_contact_at TIMESTAMP,
    last_response_at TIMESTAMP,
    last_exchange_at TIMESTAMP,
    
    -- Contact preferences (learned over time)
    preferred_terms JSONB, -- { "likes": 5, "subs": 1, "comments": 2, "watch_seconds": 60 }
    response_time_avg INTEGER, -- Average response time in minutes
    active_hours_pattern JSONB, -- Pattern when they're most active
    
    -- Notes and tags
    notes TEXT,
    tags TEXT[], -- Array of tags like ['music', 'active', 'reliable']
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, platform)
);

-- ==================== EXCHANGES TABLE ====================
-- Registra todos los intercambios (completados y fallidos)
CREATE TABLE exchanges (
    id SERIAL PRIMARY KEY,
    exchange_uuid UUID DEFAULT uuid_generate_v4(),
    
    -- Participants
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    initiated_by VARCHAR(50) DEFAULT 'us', -- us, them
    
    -- Exchange content
    our_video_url TEXT, -- Nuestro video que queremos promocionar
    their_video_url TEXT, -- Su video que debemos promocionar
    
    -- Terms agreed
    terms JSONB NOT NULL, -- { "likes": 5, "subs": 1, "comments": 2, "watch_seconds": 120 }
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'initiated', -- initiated, negotiating, agreed, my_turn_done, their_turn_done, completed, failed, no_response, partner_did_not_complete
    
    -- Execution tracking
    our_execution_started_at TIMESTAMP,
    our_execution_completed_at TIMESTAMP,
    our_execution_results JSONB, -- { "like": true, "subscribe": true, "comment": true, "watch": true }
    their_execution_verified_at TIMESTAMP,
    their_execution_results JSONB, -- Results of verification
    
    -- Conversation history
    conversation_history JSONB[], -- Array of message objects
    
    -- Timing
    initiated_at TIMESTAMP DEFAULT NOW(),
    agreed_at TIMESTAMP,
    completed_at TIMESTAMP,
    timeout_at TIMESTAMP, -- When this exchange should timeout
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==================== CONVERSATION_STATES TABLE ====================
-- Tracks ongoing conversations and their states
CREATE TABLE conversation_states (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    exchange_id INTEGER REFERENCES exchanges(id) ON DELETE CASCADE,
    
    -- State machine
    current_state VARCHAR(50) NOT NULL, -- waiting_response, negotiating_terms, waiting_execution, verifying_completion, etc.
    previous_state VARCHAR(50),
    
    -- Context for state machine
    context JSONB, -- State-specific data like pending terms, last message, etc.
    
    -- Timing
    state_entered_at TIMESTAMP DEFAULT NOW(),
    state_expires_at TIMESTAMP, -- When this state should timeout
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(contact_id) -- One active conversation per contact
);

-- ==================== MONITORED_GROUPS TABLE ====================
-- Groups we're monitoring for new contacts
CREATE TABLE monitored_groups (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL, -- telegram, discord, whatsapp
    group_id BIGINT NOT NULL,
    group_name VARCHAR(255),
    group_username VARCHAR(255), -- @groupname for Telegram
    
    -- Monitoring config
    is_active BOOLEAN DEFAULT true,
    monitor_keywords TEXT[], -- Keywords to look for
    exclusion_keywords TEXT[], -- Keywords to ignore
    
    -- Statistics
    messages_seen INTEGER DEFAULT 0,
    contacts_found INTEGER DEFAULT 0,
    last_message_at TIMESTAMP,
    
    -- Metadata
    added_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(platform, group_id)
);

-- ==================== MESSAGE_LOG TABLE ====================
-- Log of relevant messages we've seen (for analysis)
CREATE TABLE message_log (
    id SERIAL PRIMARY KEY,
    
    -- Message info
    platform VARCHAR(50) NOT NULL,
    group_id BIGINT,
    group_name VARCHAR(255),
    user_id BIGINT,
    username VARCHAR(255),
    message_id BIGINT,
    
    -- Content
    message_text TEXT,
    video_urls TEXT[], -- Extracted YouTube URLs
    
    -- Classification
    is_like4like BOOLEAN, -- Our ML classifier result
    classification_confidence FLOAT, -- 0.0 - 1.0
    extracted_terms JSONB, -- Terms we extracted from message
    
    -- Processing
    contacted BOOLEAN DEFAULT false,
    contact_created BOOLEAN DEFAULT false,
    
    -- Timing
    message_timestamp TIMESTAMP,
    processed_at TIMESTAMP DEFAULT NOW(),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==================== BOT_ANALYTICS TABLE ====================
-- Analytics and metrics for bot performance
CREATE TABLE bot_analytics (
    id SERIAL PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,
    
    -- Daily metrics
    new_contacts_found INTEGER DEFAULT 0,
    messages_processed INTEGER DEFAULT 0,
    exchanges_initiated INTEGER DEFAULT 0,
    exchanges_completed INTEGER DEFAULT 0,
    exchanges_failed INTEGER DEFAULT 0,
    
    -- Response metrics
    dm_sent INTEGER DEFAULT 0,
    dm_responses_received INTEGER DEFAULT 0,
    average_response_time_minutes INTEGER,
    
    -- Execution metrics
    youtube_actions_attempted INTEGER DEFAULT 0,
    youtube_actions_successful INTEGER DEFAULT 0,
    
    -- Quality metrics
    false_positive_rate FLOAT, -- Messages we contacted that weren't actually like4like
    conversion_rate FLOAT, -- % of contacted users that complete exchanges
    retention_rate FLOAT, -- % of contacts that do multiple exchanges
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(date)
);

-- ==================== MY_VIDEOS TABLE ====================
-- Our videos for promotion and relaunch notifications
CREATE TABLE my_videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL, -- YouTube video ID
    video_url TEXT NOT NULL,
    title VARCHAR(500),
    description TEXT,
    
    -- Video metadata
    published_at TIMESTAMP,
    duration_seconds INTEGER,
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    
    -- Promotion tracking
    promotion_active BOOLEAN DEFAULT true,
    promotion_started_at TIMESTAMP DEFAULT NOW(),
    
    -- Relaunch tracking
    relaunch_sent_count INTEGER DEFAULT 0,
    last_relaunch_at TIMESTAMP,
    
    -- Performance metrics
    exchanges_count INTEGER DEFAULT 0, -- How many exchanges promoted this video
    total_likes_gained INTEGER DEFAULT 0,
    total_subs_gained INTEGER DEFAULT 0,
    total_comments_gained INTEGER DEFAULT 0,
    total_watch_time_gained INTEGER DEFAULT 0, -- in seconds
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(video_id)
);

-- ==================== GOLOGIN_PROFILES TABLE ====================
-- Track GoLogin profiles for YouTube automation
CREATE TABLE gologin_profiles (
    id SERIAL PRIMARY KEY,
    profile_id VARCHAR(255) NOT NULL UNIQUE,
    profile_name VARCHAR(255),
    
    -- Usage tracking
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMP,
    total_uses INTEGER DEFAULT 0,
    successful_uses INTEGER DEFAULT 0,
    failed_uses INTEGER DEFAULT 0,
    
    -- Rate limiting
    daily_actions INTEGER DEFAULT 0,
    daily_actions_date DATE DEFAULT CURRENT_DATE,
    max_daily_actions INTEGER DEFAULT 50,
    
    -- Profile health
    is_banned BOOLEAN DEFAULT false,
    ban_detected_at TIMESTAMP,
    last_health_check TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==================== INDEXES ====================

-- Contacts indexes
CREATE INDEX idx_contacts_status ON contacts(status);
CREATE INDEX idx_contacts_reliability ON contacts(reliability_score DESC);
CREATE INDEX idx_contacts_platform ON contacts(platform);
CREATE INDEX idx_contacts_last_exchange ON contacts(last_exchange_at);
CREATE INDEX idx_contacts_user_platform ON contacts(user_id, platform);

-- Exchanges indexes
CREATE INDEX idx_exchanges_status ON exchanges(status);
CREATE INDEX idx_exchanges_contact ON exchanges(contact_id);
CREATE INDEX idx_exchanges_created_at ON exchanges(created_at DESC);
CREATE INDEX idx_exchanges_timeout ON exchanges(timeout_at);

-- Conversation states indexes
CREATE INDEX idx_conversation_states_contact ON conversation_states(contact_id);
CREATE INDEX idx_conversation_states_state ON conversation_states(current_state);
CREATE INDEX idx_conversation_states_expires ON conversation_states(state_expires_at);

-- Message log indexes
CREATE INDEX idx_message_log_platform_group ON message_log(platform, group_id);
CREATE INDEX idx_message_log_timestamp ON message_log(message_timestamp DESC);
CREATE INDEX idx_message_log_is_like4like ON message_log(is_like4like);
CREATE INDEX idx_message_log_contacted ON message_log(contacted);

-- Analytics indexes
CREATE INDEX idx_bot_analytics_date ON bot_analytics(date DESC);

-- My videos indexes
CREATE INDEX idx_my_videos_promotion_active ON my_videos(promotion_active);
CREATE INDEX idx_my_videos_published_at ON my_videos(published_at DESC);

-- GoLogin profiles indexes
CREATE INDEX idx_gologin_profiles_active ON gologin_profiles(is_active);
CREATE INDEX idx_gologin_profiles_last_used ON gologin_profiles(last_used_at);

-- ==================== FUNCTIONS AND TRIGGERS ====================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to all relevant tables
CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_exchanges_updated_at BEFORE UPDATE ON exchanges FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversation_states_updated_at BEFORE UPDATE ON conversation_states FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_monitored_groups_updated_at BEFORE UPDATE ON monitored_groups FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bot_analytics_updated_at BEFORE UPDATE ON bot_analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_my_videos_updated_at BEFORE UPDATE ON my_videos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_gologin_profiles_updated_at BEFORE UPDATE ON gologin_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate reliability score
CREATE OR REPLACE FUNCTION calculate_reliability_score(
    successful_exchanges INTEGER,
    total_exchanges INTEGER,
    failed_exchanges INTEGER
) RETURNS INTEGER AS $$
BEGIN
    -- Base score starts at 50
    -- +5 points per successful exchange (max +40)
    -- -10 points per failed exchange (max -50)
    -- Success rate bonus: +20 if >80%, +10 if >60%
    
    DECLARE
        base_score INTEGER := 50;
        success_bonus INTEGER := 0;
        failure_penalty INTEGER := 0;
        success_rate FLOAT := 0;
        final_score INTEGER;
    BEGIN
        -- Success bonus (capped at 40 points)
        success_bonus := LEAST(successful_exchanges * 5, 40);
        
        -- Failure penalty (capped at 50 points)
        failure_penalty := LEAST(failed_exchanges * 10, 50);
        
        -- Success rate bonus
        IF total_exchanges > 0 THEN
            success_rate := successful_exchanges::FLOAT / total_exchanges::FLOAT;
            IF success_rate > 0.8 THEN
                success_bonus := success_bonus + 20;
            ELSIF success_rate > 0.6 THEN
                success_bonus := success_bonus + 10;
            END IF;
        END IF;
        
        final_score := base_score + success_bonus - failure_penalty;
        
        -- Cap between 0 and 100
        final_score := GREATEST(0, LEAST(100, final_score));
        
        RETURN final_score;
    END;
END;
$$ LANGUAGE plpgsql;

-- ==================== SAMPLE DATA ====================

-- Insert sample monitored groups
INSERT INTO monitored_groups (platform, group_id, group_name, group_username, monitor_keywords) VALUES
('telegram', -1001234567890, 'YouTube Like4Like Exchange', '@youtube_like4like', ARRAY['like4like', 'sub4sub', 'subscribe', 'youtube']),
('telegram', -1001234567891, 'Music Promotion Group', '@music_promo', ARRAY['music', 'song', 'artist', 'promotion']),
('discord', 987654321098765432, 'Music Marketing Discord', NULL, ARRAY['youtube', 'music', 'promote']);

-- Insert sample video for testing
INSERT INTO my_videos (video_id, video_url, title, published_at) VALUES
('dQw4w9WgXcQ', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'Sample Music Video', NOW() - INTERVAL '1 day');

-- Insert sample GoLogin profiles
INSERT INTO gologin_profiles (profile_id, profile_name) VALUES
('gol_profile_001', 'YouTube Profile 1'),
('gol_profile_002', 'YouTube Profile 2'),
('gol_profile_003', 'YouTube Profile 3');

-- ==================== VIEWS ====================

-- View for active contacts ready for relaunch
CREATE VIEW contacts_ready_for_relaunch AS
SELECT 
    c.*,
    EXTRACT(days FROM (NOW() - c.last_exchange_at)) as days_since_last_exchange
FROM contacts c
WHERE c.reliability_score >= 70
  AND c.status = 'active_saved'
  AND c.total_exchanges >= 1
  AND (
      c.last_exchange_at IS NULL 
      OR c.last_exchange_at < NOW() - INTERVAL '7 days'
  )
ORDER BY c.reliability_score DESC, c.successful_exchanges DESC;

-- View for bot performance summary
CREATE VIEW bot_performance_summary AS
SELECT 
    COUNT(*) as total_contacts,
    COUNT(*) FILTER (WHERE status = 'active_saved') as saved_contacts,
    COUNT(*) FILTER (WHERE status = 'unresponsive') as unresponsive_contacts,
    AVG(reliability_score) as avg_reliability_score,
    SUM(successful_exchanges) as total_successful_exchanges,
    SUM(total_exchanges) as total_exchanges_attempted,
    CASE 
        WHEN SUM(total_exchanges) > 0 
        THEN (SUM(successful_exchanges)::FLOAT / SUM(total_exchanges)::FLOAT * 100)
        ELSE 0 
    END as overall_success_rate
FROM contacts
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';

COMMENT ON DATABASE CURRENT_DATABASE() IS 'Like4Like Bot Database - Telegram automation for YouTube promotion exchanges';