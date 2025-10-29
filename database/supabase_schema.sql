-- 🗄️ SUPABASE SCHEMA - Sistema Meta ML España-LATAM
-- Schema completo para analytics en tiempo real

-- ============================================
-- TABLA 1: CUENTAS META ADS
-- ============================================
CREATE TABLE IF NOT EXISTS accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    account_id TEXT UNIQUE NOT NULL,
    account_name TEXT NOT NULL,
    access_token TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    daily_budget DECIMAL(10,2) DEFAULT 0,
    total_spend DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- TABLA 2: CAMPAÑAS €400
-- ============================================
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id TEXT UNIQUE NOT NULL,
    account_id UUID REFERENCES accounts(id),
    campaign_name TEXT NOT NULL,
    campaign_type TEXT DEFAULT 'meta_ml',
    daily_budget DECIMAL(10,2) NOT NULL,
    total_budget DECIMAL(10,2),
    status TEXT DEFAULT 'active',
    geo_targeting JSONB DEFAULT '{"espana": 35, "latam": 65}',
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- TABLA 3: MÉTRICAS EN TIEMPO REAL
-- ============================================
CREATE TABLE IF NOT EXISTS metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    metric_date DATE DEFAULT CURRENT_DATE,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend DECIMAL(10,2) DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    ctr DECIMAL(5,4) DEFAULT 0,
    cpm DECIMAL(10,2) DEFAULT 0,
    roi_score DECIMAL(5,2) DEFAULT 0,
    region TEXT NOT NULL, -- 'espana' or 'latam' or specific country
    platform TEXT DEFAULT 'meta_ads', -- 'meta_ads', 'youtube', 'spotify'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- TABLA 4: PREDICCIONES ML
-- ============================================
CREATE TABLE IF NOT EXISTS ml_predictions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    prediction_type TEXT NOT NULL, -- 'roi', 'geo_optimization', 'budget_reallocation'
    predicted_value DECIMAL(10,4) NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.5,
    model_version TEXT DEFAULT 'v1.0',
    input_features JSONB,
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actual_value DECIMAL(10,4), -- Para evaluar precisión del modelo
    is_applied BOOLEAN DEFAULT FALSE
);

-- ============================================
-- TABLA 5: DATOS CROSS-PLATFORM
-- ============================================
CREATE TABLE IF NOT EXISTS cross_platform_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    platform TEXT NOT NULL, -- 'youtube', 'spotify', 'meta_ads'
    engagement_type TEXT NOT NULL, -- 'view', 'like', 'share', 'click', 'conversion'
    region TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    campaign_id UUID REFERENCES campaigns(id),
    metadata JSONB DEFAULT '{}', -- Datos adicionales específicos de plataforma
    quality_score DECIMAL(3,2) DEFAULT 1.0 -- Filtro de usuarios orgánicos vs bots
);

-- ============================================
-- TABLA 6: PERFORMANCE GEOGRÁFICO
-- ============================================
CREATE TABLE IF NOT EXISTS geographic_performance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    country_code TEXT NOT NULL, -- 'ES', 'MX', 'AR', 'CO', etc.
    region_group TEXT NOT NULL, -- 'espana' or 'latam'
    current_budget_pct DECIMAL(5,2) NOT NULL, -- Porcentaje actual del presupuesto
    performance_score DECIMAL(5,2) DEFAULT 0, -- Score de performance relativo
    optimization_suggestion TEXT, -- 'increase', 'decrease', 'maintain'
    last_optimization TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- TABLA 7: LOGS DE OPTIMIZACIÓN
-- ============================================
CREATE TABLE IF NOT EXISTS optimization_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    optimization_type TEXT NOT NULL, -- 'budget_reallocation', 'geo_targeting', 'audience_expansion'
    old_value JSONB,
    new_value JSONB,
    ml_confidence DECIMAL(3,2) DEFAULT 0,
    performance_improvement DECIMAL(5,2), -- % mejora esperada
    actual_improvement DECIMAL(5,2), -- % mejora real (calculada posteriormente)
    applied_by TEXT DEFAULT 'ml_system',
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================
CREATE INDEX IF NOT EXISTS idx_metrics_campaign_date ON metrics(campaign_id, metric_date);
CREATE INDEX IF NOT EXISTS idx_metrics_region ON metrics(region);
CREATE INDEX IF NOT EXISTS idx_cross_platform_user ON cross_platform_data(user_id, platform);
CREATE INDEX IF NOT EXISTS idx_geographic_country ON geographic_performance(country_code);
CREATE INDEX IF NOT EXISTS idx_optimization_campaign ON optimization_logs(campaign_id);

-- ============================================
-- TRIGGERS PARA TIMESTAMPS AUTOMÁTICOS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_geographic_updated_at BEFORE UPDATE ON geographic_performance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- DATOS DE EJEMPLO PARA TESTING
-- ============================================
INSERT INTO accounts (account_id, account_name, access_token, daily_budget) VALUES 
('1771115133833816', 'ASampayo Meta Ads', 'EAAlZBjrH0WtYBP4...', 400.00)
ON CONFLICT (account_id) DO NOTHING;

INSERT INTO campaigns (campaign_id, account_id, campaign_name, daily_budget, total_budget) VALUES 
('test_campaign_001', (SELECT id FROM accounts WHERE account_id = '1771115133833816'), 'Test España-LATAM ML', 100.00, 3000.00)
ON CONFLICT (campaign_id) DO NOTHING;

-- ============================================
-- VISTAS PARA DASHBOARDS
-- ============================================

-- Vista: Performance por región
CREATE OR REPLACE VIEW v_regional_performance AS
SELECT 
    c.campaign_name,
    gp.region_group,
    SUM(m.spend) as total_spend,
    SUM(m.impressions) as total_impressions,
    SUM(m.clicks) as total_clicks,
    AVG(m.roi_score) as avg_roi,
    AVG(gp.performance_score) as region_performance
FROM campaigns c
JOIN geographic_performance gp ON c.id = gp.campaign_id
JOIN metrics m ON c.id = m.campaign_id
GROUP BY c.campaign_name, gp.region_group;

-- Vista: Datos ML para optimización
CREATE OR REPLACE VIEW v_ml_optimization_data AS
SELECT 
    c.campaign_name,
    c.geo_targeting,
    AVG(m.roi_score) as current_roi,
    COUNT(cpd.user_id) as cross_platform_users,
    AVG(cpd.quality_score) as avg_quality_score,
    COUNT(ol.id) as total_optimizations
FROM campaigns c
LEFT JOIN metrics m ON c.id = m.campaign_id
LEFT JOIN cross_platform_data cpd ON c.id = cpd.campaign_id
LEFT JOIN optimization_logs ol ON c.id = ol.campaign_id
WHERE c.status = 'active'
GROUP BY c.id, c.campaign_name, c.geo_targeting;

COMMENT ON TABLE accounts IS 'Cuentas de Meta Ads con tokens y configuración';
COMMENT ON TABLE campaigns IS 'Campañas €400 con targeting España-LATAM';
COMMENT ON TABLE metrics IS 'Métricas en tiempo real por región y plataforma';
COMMENT ON TABLE ml_predictions IS 'Predicciones del sistema ML para optimización';
COMMENT ON TABLE cross_platform_data IS 'Datos unificados YouTube + Spotify + Meta';
COMMENT ON TABLE geographic_performance IS 'Performance por país para redistribución';
COMMENT ON TABLE optimization_logs IS 'Historial de cambios automáticos del ML';

-- ============================================
-- ROW LEVEL SECURITY (RLS) - OPCIONAL
-- ============================================
-- ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE metrics ENABLE ROW LEVEL SECURITY;

SELECT 'Schema Meta ML España-LATAM creado exitosamente! 🚀' as resultado;