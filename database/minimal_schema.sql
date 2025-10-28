
-- 🗄️ SCHEMA MÍNIMO - Solo tablas esenciales
-- Ejecutar en Supabase SQL Editor (una tabla a la vez si hay errores)

-- TABLA 1: Cuentas Meta Ads
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    account_id TEXT UNIQUE NOT NULL,
    account_name TEXT NOT NULL,
    daily_budget DECIMAL(10,2) DEFAULT 400.00,
    created_at TIMESTAMP DEFAULT NOW()
);

-- TABLA 2: Campañas
CREATE TABLE campaigns (
    id SERIAL PRIMARY KEY,
    campaign_id TEXT UNIQUE NOT NULL,
    campaign_name TEXT NOT NULL,
    daily_budget DECIMAL(10,2) NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- TABLA 3: Métricas básicas
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER,
    metric_date DATE DEFAULT CURRENT_DATE,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend DECIMAL(10,2) DEFAULT 0,
    roi_score DECIMAL(5,2) DEFAULT 0,
    region TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- DATOS DE PRUEBA
INSERT INTO accounts (account_id, account_name, daily_budget) VALUES 
('1771115133833816', 'Angel Garcia Meta Ads', 400.00);

INSERT INTO campaigns (campaign_id, campaign_name, daily_budget) VALUES 
('test_campaign_001', 'España-LATAM Viral Campaign', 100.00);

-- VERIFICACIÓN
SELECT 'Schema mínimo creado exitosamente!' as resultado;
SELECT COUNT(*) as total_accounts FROM accounts;
SELECT COUNT(*) as total_campaigns FROM campaigns;
