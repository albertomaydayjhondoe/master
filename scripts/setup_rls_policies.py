"""
🔒 CONFIGURAR RLS (ROW LEVEL SECURITY)
Permite que anon key funcione con las tablas
"""

def generate_rls_policies():
    """Genera políticas RLS para permitir acceso con anon key"""
    
    rls_sql = """
-- 🔒 POLÍTICAS RLS PARA ANON KEY
-- Ejecutar DESPUÉS de crear las tablas

-- Habilitar RLS en todas las tablas
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE metrics ENABLE ROW LEVEL SECURITY;

-- Política: Permitir SELECT a anon
CREATE POLICY "Allow anon select on accounts" ON accounts
    FOR SELECT TO anon
    USING (true);

CREATE POLICY "Allow anon select on campaigns" ON campaigns
    FOR SELECT TO anon
    USING (true);

CREATE POLICY "Allow anon select on metrics" ON metrics
    FOR SELECT TO anon
    USING (true);

-- Política: Permitir INSERT a anon (para testing)
CREATE POLICY "Allow anon insert on metrics" ON metrics
    FOR INSERT TO anon
    WITH CHECK (true);

-- Verificar políticas
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public';
"""
    
    print("🔒 CONFIGURAR RLS PARA ANON KEY")
    print("=" * 40)
    print("Ejecuta esto DESPUÉS de crear tablas:")
    print()
    print(rls_sql)
    
    # Guardar en archivo
    with open('database/rls_policies.sql', 'w', encoding='utf-8') as f:
        f.write(rls_sql)
    
    print("💾 Guardado en: database/rls_policies.sql")

if __name__ == "__main__":
    generate_rls_policies()