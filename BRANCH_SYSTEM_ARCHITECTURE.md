# 🌳 Sistema de Ramas - Arquitectura de Desarrollo

## 🎯 ESTRATEGIA DE RAMAS IMPRESCINDIBLES

### 📊 **RAMAS PRINCIPALES**

#### 🏠 `main` - Producción Estable
- **Propósito**: Código en producción
- **Protección**: Solo merge desde `staging`
- **Deploy**: Automático a producción
- **Tests**: 100% coverage requerido

#### 🚀 `staging` - Pre-producción  
- **Propósito**: Testing de integración
- **Merge desde**: `develop` 
- **Deploy**: Entorno de staging
- **Validación**: Tests E2E + UAT

#### 🔧 `develop` - Integración Continua
- **Propósito**: Rama de desarrollo principal
- **Merge desde**: `feature/*`, `hotfix/*`
- **CI/CD**: Tests automáticos
- **Code Review**: Requerido

---

### 🔀 **RAMAS DE FUNCIONALIDAD**

#### 🎨 `meta` - Sistema Meta/TikTok Actual
- **Estado**: ✅ Activa
- **Contenido**: Monitoring, YouTube executor, Telegram
- **Merge target**: `develop`

#### ⚡ `apply` - TikTok Flow System (Durmiente)
- **Estado**: 🟡 Durmiente  
- **Contenido**: Sistema de 8 capas viral
- **Activación**: Cuando APIs estén listas

#### 🧠 `ultralytics-ml` - Machine Learning Core
- **Propósito**: Integración Ultralytics YOLO
- **Contenido**: ML pipelines, modelos, training
- **Conexión**: Con `apply` y `meta`

#### 📊 `analytics-dashboard` - Analytics y Reporting  
- **Propósito**: Dashboards y métricas
- **Tecnologías**: BigQuery, Looker, Grafana
- **Datos**: De todas las ramas

#### 🤖 `automation-core` - Núcleo de Automatización
- **Propósito**: n8n workflows, scheduling
- **Integraciones**: Device farm, GoLogin
- **Orquestación**: Sistema completo

#### 📱 `device-farm` - Gestión de Dispositivos
- **Propósito**: Control dispositivos físicos/virtuales
- **Tecnologías**: Appium, BrowserStack
- **Conexión**: Con automation-core

---

### 🔄 **FLUJO DE TRABAJO**

```
feature/nueva-funcionalidad → develop → staging → main
                           ↑
hotfix/bugfix-critico ──────┘

Ramas especiales:
meta ────────────────→ develop (cuando esté lista)
apply ───────────────→ develop (activación controlada)  
ultralytics-ml ──────→ develop (integración ML)
```

---

### 🛡️ **PROTECCIÓN Y POLÍTICAS**

#### **Branch Protection Rules:**
- `main`: Require PR + 2 approvals + CI pass
- `staging`: Require PR + 1 approval + CI pass  
- `develop`: Require PR + CI pass
- Special branches: Protected, merge only when ready

#### **Merge Strategy:**
- **Squash commits**: Para features limpias
- **Merge commits**: Para mantener historial de ramas principales  
- **Rebase**: Para hotfixes rápidos

---

### 📋 **CHECKLIST DE MERGE**

#### **Antes de merge a develop:**
- [ ] ✅ Tests pasan (4/4)
- [ ] 📊 Coverage > 80%
- [ ] 🔍 Code review completado
- [ ] 📚 Documentación actualizada
- [ ] 🎯 Funcionalidad probada

#### **Antes de merge a main:**
- [ ] ✅ Tests E2E pasan
- [ ] 🚀 Deploy a staging exitoso
- [ ] 👥 UAT completado
- [ ] 📈 Performance verificado
- [ ] 🔒 Security scan limpio

---

### 🎯 **PRÓXIMOS PASOS**

1. **Crear rama `ultralytics-ml`** para integración ML
2. **Setup branch protection** en GitHub
3. **Configurar CI/CD** para cada rama
4. **Documentar workflows** específicos
5. **Integrar sistema de ramas** con desarrollo

Este sistema garantiza desarrollo ordenado y merges controlados.