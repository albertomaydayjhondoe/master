# 🚀 GUÍA CONFIGURACIÓN SUPABASE - 3 MINUTOS

## **Paso 1: Crear Proyecto**
1. Ve a: https://supabase.com/new
2. Clic en **"New Project"**
3. Nombre: `meta-ml-espana-latam`
4. Password: `tu_password_seguro`
5. Region: **Europe (Frankfurt)** - Más cercano a España
6. Clic **"Create new project"**
7. **Espera 2-3 minutos** mientras se crea

## **Paso 2: Obtener Credenciales**
1. Ve a **Settings** → **API**
2. Copia estas 3 claves:

```
URL: https://tu-proyecto-id.supabase.co
anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## **Paso 3: Configurar Base de Datos**
1. Ve a **Database** → **SQL Editor**
2. Clic **"New Query"**
3. Copia y pega TODO el contenido de: `database/supabase_schema.sql`
4. Clic **"Run"** 
5. ✅ Verás: "Schema Meta ML España-LATAM creado exitosamente! 🚀"

## **Paso 4: Actualizar .env**
Abre: `config/production/.env` y reemplaza:

```bash
# Supabase Configuration
SUPABASE_URL=https://tu-proyecto-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:tu-password@db.tu-proyecto-id.supabase.co:5432/postgres
```

## **Paso 5: Verificar Configuración**
Ejecuta:
```bash
python scripts/check_api_status_dynamic.py
```

**✅ Resultado esperado:**
```
🟢 Supabase
   Status: ✅ COMPLETAMENTE CONFIGURADO
   ✅ SUPABASE_URL: Configurado
   ✅ SUPABASE_ANON_KEY: Configurado  
   ✅ SUPABASE_SERVICE_KEY: Configurado
```

## **🎯 Beneficios INMEDIATOS:**

### **Landing Pages con Analytics:**
- 📊 Visitantes en tiempo real
- 🌍 Mapa de conversiones España vs LATAM
- 📈 ROI por región actualizado cada segundo

### **Dashboard ML Avanzado:**
- 🧠 Predicciones ML en vivo
- 🔄 Optimizaciones automáticas aplicadas
- 📊 Cross-platform data (YouTube + Spotify + Meta)

### **Sistema 100% Completo:**
- ✅ Meta Ads €400 campaigns
- ✅ YouTube automation 
- ✅ ML España-LATAM optimization
- ✅ Real-time analytics
- ✅ Cross-platform learning

## **🚨 IMPORTANTE:**
- **Password**: ¡Guárdalo bien! No se puede recuperar
- **Service Role Key**: Solo para backend, nunca en frontend
- **Region**: Europe (Frankfurt) para mejor latencia desde España

## **💡 Próximo Paso:**
Una vez configurado Supabase, tu sistema estará **100% operativo** para:
- Campañas Meta Ads reales
- Analytics en tiempo real  
- Optimización ML automática
- Landing pages avanzadas

**¡Tu sistema estará completo! 🔥**