-- 🎯 Supabase Database Schema for Meta Ads €400 Campaign System
-- Esquema completo de base de datos para sistema de campañas Meta Ads con UTM tracking

-- ============================================
-- TABLAS PRINCIPALES
-- ============================================

-- Tabla de campañas Meta Ads
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id VARCHAR UNIQUE NOT NULL,
    campaign_name VARCHAR NOT NULL,
    artist_name VARCHAR NOT NULL,
    song_name VARCHAR NOT NULL,
    budget_euros DECIMAL(10,2) DEFAULT 400.00,
    daily_budget DECIMAL(10,2) DEFAULT 20.00,
    genre VARCHAR DEFAULT 'pop',
    target_countries TEXT[] DEFAULT '{"ES","MX","US"}',
    youtube_channel VARCHAR,
    instagram_handle VARCHAR,
    tiktok_handle VARCHAR,
    twitter_handle VARCHAR,
    landing_page_template VARCHAR DEFAULT 'music_release',
    auto_approve_budget DECIMAL(10,2) DEFAULT 50.00,
    page_id VARCHAR UNIQUE,
    page_url VARCHAR,
    status VARCHAR DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'draft')),
    meta_ads_campaign_id VARCHAR,
    meta_ads_account_id VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Tabla de visitas UTM con geolocalización
CREATE TABLE IF NOT EXISTS utm_visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id VARCHAR NOT NULL,
    campaign_id VARCHAR NOT NULL,
    session_id VARCHAR,
    utm_source VARCHAR,
    utm_medium VARCHAR,
    utm_campaign VARCHAR,
    utm_content VARCHAR,
    utm_term VARCHAR,
    visitor_ip INET,
    user_agent TEXT,
    referrer TEXT,
    country VARCHAR(2),
    country_name VARCHAR(100),
    region VARCHAR(100),
    city VARCHAR(100),
    device_type VARCHAR CHECK (device_type IN ('mobile', 'desktop', 'tablet')),
    browser VARCHAR(50),
    os VARCHAR(50),
    screen_resolution VARCHAR(20),
    language VARCHAR(10),
    is_unique_visitor BOOLEAN DEFAULT TRUE,
    page_load_time INTEGER, -- milisegundos
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE
);

-- Tabla de conversiones UTM con valor de conversión
CREATE TABLE IF NOT EXISTS utm_conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id VARCHAR NOT NULL,
    campaign_id VARCHAR NOT NULL,
    session_id VARCHAR,
    action_type VARCHAR NOT NULL, -- 'youtube_click', 'spotify_click', 'download', etc.
    platform VARCHAR NOT NULL, -- 'youtube', 'spotify', 'apple', 'instagram', etc.
    conversion_value DECIMAL(10,2) DEFAULT 1.00,
    revenue_attributed DECIMAL(10,2) DEFAULT 0.00,
    utm_source VARCHAR,
    utm_medium VARCHAR,
    utm_campaign VARCHAR,
    visitor_ip INET,
    country VARCHAR(2),
    device_type VARCHAR,
    is_first_conversion BOOLEAN DEFAULT TRUE,
    conversion_path TEXT, -- JSON con el camino de conversión
    time_to_conversion INTEGER, -- segundos desde la visita inicial
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE
);

-- Tabla de métricas agregadas por campaña
CREATE TABLE IF NOT EXISTS campaign_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id VARCHAR UNIQUE NOT NULL,
    
    -- Métricas de tráfico
    total_visits INTEGER DEFAULT 0,
    unique_visits INTEGER DEFAULT 0,
    returning_visits INTEGER DEFAULT 0,
    bounce_rate DECIMAL(5,2) DEFAULT 0.00,
    avg_session_duration INTEGER DEFAULT 0, -- segundos
    pages_per_session DECIMAL(3,1) DEFAULT 1.0,
    
    -- Métricas de conversión
    total_conversions INTEGER DEFAULT 0,
    unique_conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    revenue_euros DECIMAL(10,2) DEFAULT 0.00,
    avg_conversion_value DECIMAL(10,2) DEFAULT 0.00,
    
    -- Métricas de coste y ROI
    cost_euros DECIMAL(10,2) DEFAULT 0.00,
    cost_per_visit DECIMAL(10,4) DEFAULT 0.00,
    cost_per_conversion DECIMAL(10,4) DEFAULT 0.00,
    roi_percentage DECIMAL(8,2) DEFAULT 0.00,
    roas DECIMAL(8,2) DEFAULT 0.00, -- Return on Ad Spend
    
    -- Top performers
    top_utm_source VARCHAR,
    top_utm_medium VARCHAR,
    top_platform VARCHAR,
    top_country VARCHAR(2),
    top_device_type VARCHAR,
    
    -- Timestamps
    last_visit_at TIMESTAMP WITH TIME ZONE,
    last_conversion_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE
);

-- Tabla de sesiones de usuario para tracking avanzado
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR UNIQUE NOT NULL,
    campaign_id VARCHAR,
    page_id VARCHAR,
    visitor_ip INET,
    user_agent TEXT,
    country VARCHAR(2),
    device_type VARCHAR,
    
    -- Datos de sesión
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    duration_seconds INTEGER DEFAULT 0,
    page_views INTEGER DEFAULT 1,
    conversions_count INTEGER DEFAULT 0,
    
    -- UTM de entrada
    entry_utm_source VARCHAR,
    entry_utm_medium VARCHAR,
    entry_utm_campaign VARCHAR,
    
    -- Estado de sesión
    is_active BOOLEAN DEFAULT TRUE,
    ended_at TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE
);

-- Tabla de eventos de página para tracking detallado
CREATE TABLE IF NOT EXISTS page_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR NOT NULL,
    page_id VARCHAR NOT NULL,
    event_type VARCHAR NOT NULL, -- 'page_view', 'click', 'scroll', 'time_spent', etc.
    event_data JSONB, -- Datos específicos del evento
    element_clicked VARCHAR, -- Para eventos de click
    scroll_depth INTEGER, -- Para eventos de scroll (0-100)
    time_on_element INTEGER, -- milisegundos
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE CASCADE
);

-- Tabla de experimentos A/B para landing pages
CREATE TABLE IF NOT EXISTS ab_experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_name VARCHAR NOT NULL,
    campaign_id VARCHAR,
    
    -- Configuración del experimento
    variant_a_config JSONB, -- Configuración de la variante A
    variant_b_config JSONB, -- Configuración de la variante B
    traffic_split DECIMAL(3,2) DEFAULT 0.50, -- 50/50 por defecto
    
    -- Métricas del experimento
    variant_a_visitors INTEGER DEFAULT 0,
    variant_b_visitors INTEGER DEFAULT 0,
    variant_a_conversions INTEGER DEFAULT 0,
    variant_b_conversions INTEGER DEFAULT 0,
    variant_a_conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    variant_b_conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Estado del experimento
    status VARCHAR DEFAULT 'active' CHECK (status IN ('draft', 'active', 'paused', 'completed')),
    winner_variant VARCHAR, -- 'A', 'B', o NULL si no hay ganador claro
    confidence_level DECIMAL(5,2), -- Nivel de confianza estadística
    
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE
);

-- ============================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================

-- Índices para utm_visits
CREATE INDEX IF NOT EXISTS idx_utm_visits_campaign_id ON utm_visits(campaign_id);
CREATE INDEX IF NOT EXISTS idx_utm_visits_timestamp ON utm_visits(timestamp);
CREATE INDEX IF NOT EXISTS idx_utm_visits_page_id ON utm_visits(page_id);
CREATE INDEX IF NOT EXISTS idx_utm_visits_country ON utm_visits(country);
CREATE INDEX IF NOT EXISTS idx_utm_visits_device ON utm_visits(device_type);
CREATE INDEX IF NOT EXISTS idx_utm_visits_utm_source ON utm_visits(utm_source);
CREATE INDEX IF NOT EXISTS idx_utm_visits_session_id ON utm_visits(session_id);

-- Índices para utm_conversions
CREATE INDEX IF NOT EXISTS idx_utm_conversions_campaign_id ON utm_conversions(campaign_id);
CREATE INDEX IF NOT EXISTS idx_utm_conversions_timestamp ON utm_conversions(timestamp);
CREATE INDEX IF NOT EXISTS idx_utm_conversions_platform ON utm_conversions(platform);
CREATE INDEX IF NOT EXISTS idx_utm_conversions_action_type ON utm_conversions(action_type);
CREATE INDEX IF NOT EXISTS idx_utm_conversions_session_id ON utm_conversions(session_id);

-- Índices para campaigns
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON campaigns(created_at);
CREATE INDEX IF NOT EXISTS idx_campaigns_artist_name ON campaigns(artist_name);
CREATE INDEX IF NOT EXISTS idx_campaigns_genre ON campaigns(genre);

-- Índices para user_sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_campaign_id ON user_sessions(campaign_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_started_at ON user_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);

-- Índices para page_events
CREATE INDEX IF NOT EXISTS idx_page_events_session_id ON page_events(session_id);
CREATE INDEX IF NOT EXISTS idx_page_events_event_type ON page_events(event_type);
CREATE INDEX IF NOT EXISTS idx_page_events_timestamp ON page_events(timestamp);

-- ============================================
-- FUNCIONES STORED PROCEDURES
-- ============================================

-- Función para actualizar métricas de campaña
CREATE OR REPLACE FUNCTION update_campaign_metrics(campaign_id_param VARCHAR)
RETURNS VOID AS $$
DECLARE
    v_total_visits INTEGER;
    v_unique_visits INTEGER;
    v_returning_visits INTEGER;
    v_total_conversions INTEGER;
    v_unique_conversions INTEGER;
    v_revenue_euros DECIMAL(10,2);
    v_conversion_rate DECIMAL(5,2);
    v_avg_session_duration INTEGER;
    v_bounce_rate DECIMAL(5,2);
    v_top_utm_source VARCHAR;
    v_top_platform VARCHAR;
    v_top_country VARCHAR(2);
    v_top_device VARCHAR;
BEGIN
    -- Calcular métricas de visitas
    SELECT 
        COUNT(*),
        COUNT(DISTINCT visitor_ip),
        COUNT(*) - COUNT(DISTINCT visitor_ip)
    INTO v_total_visits, v_unique_visits, v_returning_visits
    FROM utm_visits 
    WHERE campaign_id = campaign_id_param;
    
    -- Calcular métricas de conversión
    SELECT 
        COUNT(*),
        COUNT(DISTINCT visitor_ip),
        COALESCE(SUM(conversion_value), 0)
    INTO v_total_conversions, v_unique_conversions, v_revenue_euros
    FROM utm_conversions 
    WHERE campaign_id = campaign_id_param;
    
    -- Calcular conversion rate
    v_conversion_rate := CASE 
        WHEN v_total_visits > 0 THEN (v_total_conversions * 100.0 / v_total_visits)
        ELSE 0 
    END;
    
    -- Calcular duración promedio de sesión
    SELECT COALESCE(AVG(duration_seconds), 0)
    INTO v_avg_session_duration
    FROM user_sessions 
    WHERE campaign_id = campaign_id_param AND duration_seconds > 0;
    
    -- Calcular bounce rate (sesiones con una sola página vista)
    SELECT 
        CASE 
            WHEN COUNT(*) > 0 THEN 
                (COUNT(CASE WHEN page_views = 1 THEN 1 END) * 100.0 / COUNT(*))
            ELSE 0 
        END
    INTO v_bounce_rate
    FROM user_sessions 
    WHERE campaign_id = campaign_id_param;
    
    -- Obtener top UTM source
    SELECT utm_source
    INTO v_top_utm_source
    FROM utm_visits 
    WHERE campaign_id = campaign_id_param AND utm_source IS NOT NULL
    GROUP BY utm_source 
    ORDER BY COUNT(*) DESC 
    LIMIT 1;
    
    -- Obtener top platform de conversiones
    SELECT platform
    INTO v_top_platform
    FROM utm_conversions 
    WHERE campaign_id = campaign_id_param
    GROUP BY platform 
    ORDER BY COUNT(*) DESC 
    LIMIT 1;
    
    -- Obtener top country
    SELECT country
    INTO v_top_country
    FROM utm_visits 
    WHERE campaign_id = campaign_id_param AND country IS NOT NULL
    GROUP BY country 
    ORDER BY COUNT(*) DESC 
    LIMIT 1;
    
    -- Obtener top device type
    SELECT device_type
    INTO v_top_device
    FROM utm_visits 
    WHERE campaign_id = campaign_id_param AND device_type IS NOT NULL
    GROUP BY device_type 
    ORDER BY COUNT(*) DESC 
    LIMIT 1;
    
    -- Insertar o actualizar métricas
    INSERT INTO campaign_metrics (
        campaign_id, total_visits, unique_visits, returning_visits,
        total_conversions, unique_conversions, conversion_rate, 
        revenue_euros, avg_session_duration, bounce_rate,
        top_utm_source, top_platform, top_country, top_device_type,
        last_visit_at, last_conversion_at, updated_at
    )
    VALUES (
        campaign_id_param, v_total_visits, v_unique_visits, v_returning_visits,
        v_total_conversions, v_unique_conversions, v_conversion_rate,
        v_revenue_euros, v_avg_session_duration, v_bounce_rate,
        v_top_utm_source, v_top_platform, v_top_country, v_top_device,
        (SELECT MAX(timestamp) FROM utm_visits WHERE campaign_id = campaign_id_param),
        (SELECT MAX(timestamp) FROM utm_conversions WHERE campaign_id = campaign_id_param),
        NOW()
    )
    ON CONFLICT (campaign_id) 
    DO UPDATE SET
        total_visits = EXCLUDED.total_visits,
        unique_visits = EXCLUDED.unique_visits,
        returning_visits = EXCLUDED.returning_visits,
        total_conversions = EXCLUDED.total_conversions,
        unique_conversions = EXCLUDED.unique_conversions,
        conversion_rate = EXCLUDED.conversion_rate,
        revenue_euros = EXCLUDED.revenue_euros,
        avg_session_duration = EXCLUDED.avg_session_duration,
        bounce_rate = EXCLUDED.bounce_rate,
        top_utm_source = EXCLUDED.top_utm_source,
        top_platform = EXCLUDED.top_platform,
        top_country = EXCLUDED.top_country,
        top_device_type = EXCLUDED.top_device_type,
        last_visit_at = EXCLUDED.last_visit_at,
        last_conversion_at = EXCLUDED.last_conversion_at,
        updated_at = NOW();
        
END;
$$ LANGUAGE plpgsql;

-- Función para obtener tráfico por horas
CREATE OR REPLACE FUNCTION get_hourly_traffic(campaign_id_param VARCHAR)
RETURNS TABLE (
    hour_of_day INTEGER,
    total_visits INTEGER,
    total_conversions INTEGER,
    conversion_rate DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        EXTRACT(HOUR FROM v.timestamp)::INTEGER as hour_of_day,
        COUNT(v.*)::INTEGER as total_visits,
        COUNT(c.*)::INTEGER as total_conversions,
        CASE 
            WHEN COUNT(v.*) > 0 THEN (COUNT(c.*) * 100.0 / COUNT(v.*))::DECIMAL(5,2)
            ELSE 0::DECIMAL(5,2)
        END as conversion_rate
    FROM utm_visits v
    LEFT JOIN utm_conversions c ON v.session_id = c.session_id
    WHERE v.campaign_id = campaign_id_param
    GROUP BY EXTRACT(HOUR FROM v.timestamp)
    ORDER BY hour_of_day;
END;
$$ LANGUAGE plpgsql;

-- Función para detectar visitantes únicos
CREATE OR REPLACE FUNCTION is_unique_visitor(visitor_ip_param INET, campaign_id_param VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    visitor_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO visitor_count
    FROM utm_visits 
    WHERE visitor_ip = visitor_ip_param 
    AND campaign_id = campaign_id_param;
    
    RETURN visitor_count = 0;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS AUTOMÁTICOS
-- ============================================

-- Trigger para actualizar métricas automáticamente
CREATE OR REPLACE FUNCTION trigger_update_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar métricas de la campaña
    PERFORM update_campaign_metrics(NEW.campaign_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para utm_visits
DROP TRIGGER IF EXISTS update_metrics_on_visit ON utm_visits;
CREATE TRIGGER update_metrics_on_visit
    AFTER INSERT ON utm_visits
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_metrics();

-- Triggers para utm_conversions
DROP TRIGGER IF EXISTS update_metrics_on_conversion ON utm_conversions;
CREATE TRIGGER update_metrics_on_conversion
    AFTER INSERT ON utm_conversions
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_metrics();

-- Trigger para marcar visitantes únicos
CREATE OR REPLACE FUNCTION mark_unique_visitor()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_unique_visitor := is_unique_visitor(NEW.visitor_ip, NEW.campaign_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS mark_unique_on_visit ON utm_visits;
CREATE TRIGGER mark_unique_on_visit
    BEFORE INSERT ON utm_visits
    FOR EACH ROW
    EXECUTE FUNCTION mark_unique_visitor();

-- Trigger para actualizar timestamp de campaigns
CREATE OR REPLACE FUNCTION update_campaign_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_campaign_timestamp ON campaigns;
CREATE TRIGGER update_campaign_timestamp
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_campaign_updated_at();

-- ============================================
-- VISTAS ÚTILES PARA ANALYTICS
-- ============================================

-- Vista de performance de campañas
CREATE OR REPLACE VIEW campaign_performance AS
SELECT 
    c.campaign_id,
    c.campaign_name,
    c.artist_name,
    c.song_name,
    c.genre,
    c.budget_euros,
    c.status,
    COALESCE(m.total_visits, 0) as total_visits,
    COALESCE(m.unique_visits, 0) as unique_visits,
    COALESCE(m.total_conversions, 0) as total_conversions,
    COALESCE(m.conversion_rate, 0) as conversion_rate,
    COALESCE(m.revenue_euros, 0) as revenue_euros,
    COALESCE(m.roi_percentage, 0) as roi_percentage,
    m.top_utm_source,
    m.top_platform,
    c.created_at,
    m.updated_at as metrics_updated_at
FROM campaigns c
LEFT JOIN campaign_metrics m ON c.campaign_id = m.campaign_id
ORDER BY c.created_at DESC;

-- Vista de top performing campaigns
CREATE OR REPLACE VIEW top_campaigns AS
SELECT 
    cp.*,
    RANK() OVER (ORDER BY cp.conversion_rate DESC, cp.total_conversions DESC) as performance_rank
FROM campaign_performance cp
WHERE cp.total_visits > 10 -- Solo campañas con tráfico significativo
ORDER BY performance_rank
LIMIT 20;

-- Vista de daily statistics
CREATE OR REPLACE VIEW daily_campaign_stats AS
SELECT 
    v.campaign_id,
    DATE(v.timestamp) as date,
    COUNT(v.*) as daily_visits,
    COUNT(DISTINCT v.visitor_ip) as daily_unique_visits,
    COUNT(c.*) as daily_conversions,
    CASE 
        WHEN COUNT(v.*) > 0 THEN (COUNT(c.*) * 100.0 / COUNT(v.*))
        ELSE 0 
    END as daily_conversion_rate,
    COALESCE(SUM(c.conversion_value), 0) as daily_revenue
FROM utm_visits v
LEFT JOIN utm_conversions c ON v.session_id = c.session_id 
    AND DATE(v.timestamp) = DATE(c.timestamp)
GROUP BY v.campaign_id, DATE(v.timestamp)
ORDER BY date DESC, daily_conversions DESC;

-- ============================================
-- DATOS DE EJEMPLO PARA TESTING
-- ============================================

-- Insertar campaña de ejemplo (solo para desarrollo)
INSERT INTO campaigns (
    campaign_id, campaign_name, artist_name, song_name, 
    budget_euros, genre, target_countries, page_id, page_url, status
) VALUES (
    'example_campaign_001',
    'Verano 2024 - Nueva Canción',
    'Artista Demo',
    'Canción de Verano',
    400.00,
    'reggaeton',
    '{"ES","MX","CO","AR"}',
    'page_example_001',
    'https://meta-ads-centric.railway.app/landing/page_example_001',
    'active'
) ON CONFLICT (campaign_id) DO NOTHING;

-- Insertar métricas de ejemplo
INSERT INTO campaign_metrics (
    campaign_id, total_visits, unique_visits, total_conversions,
    conversion_rate, revenue_euros, top_utm_source, top_platform
) VALUES (
    'example_campaign_001',
    1250, 980, 89, 7.12, 156.80,
    'meta_ads', 'spotify'
) ON CONFLICT (campaign_id) DO NOTHING;