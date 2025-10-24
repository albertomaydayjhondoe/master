# 🎛️ Dashboard de Control de Producción - Acceso Rápido

## ✅ Estado: ACTIVO

### 🌐 URLs de Acceso

#### Acceso Local (HTTP)
```
http://localhost:8501
```
- ✅ Disponible inmediatamente en este entorno
- 🔓 Sin cifrado (solo para desarrollo local)
- ⚡ Baja latencia

#### Acceso Público (HTTPS)
```
https://orange-chainsaw-jjp449674r4rhp7ww-8501.app.github.dev
```
- 🔒 Conexión cifrada con SSL
- 🌍 Accesible desde cualquier navegador
- ✅ No requiere VPN o configuración adicional
- 🛡️ Certificado SSL automático de GitHub

### 🎯 Funcionalidades del Dashboard

#### 🔴 Red Button Dashboard
Sistema de control de producción con las siguientes capacidades:

1. **Control Granular de Módulos**
   - Activar/desactivar funcionalidades individuales
   - Transición de modo dummy a producción
   - Control independiente por módulo

2. **Monitoreo en Tiempo Real**
   - Estado de dependencias
   - Métricas del sistema
   - Logs en vivo

3. **Gestión de Dependencias**
   - Verificación de paquetes instalados
   - Detección de fallbacks activos
   - Instalación de dependencias faltantes

4. **Sistema de Emergencia**
   - Botón rojo para detener operaciones
   - Rollback rápido a modo dummy
   - Logs de auditoría

### 🔧 Configuración de Seguridad

- ✅ **CORS:** Habilitado
- ✅ **XSRF Protection:** Activa
- ✅ **HTTPS:** Configurado automáticamente
- ✅ **Firewall:** Puerto 8501 reenviado de forma segura

### 🚀 Comandos Útiles

#### Ver estado del servidor
```bash
ps aux | grep streamlit
```

#### Detener el dashboard
```bash
pkill -f "streamlit run"
```

#### Reiniciar el dashboard
```bash
./red_button_control.py
```

#### Obtener URL HTTPS actualizada
```bash
bash get_https_url.sh
```

### 📊 Panel de Puertos (VS Code)

Para verificar el estado del puerto:
1. Presiona `Ctrl+Shift+\`` para abrir terminal
2. Haz clic en la pestaña **PORTS**
3. Busca el puerto `8501`
4. Verifica que el estado sea **Forwarded**

### 🎛️ Módulos Controlables

El dashboard permite controlar individualmente:

- **ML Core** - Sistema de Machine Learning
- **Telegram** - Bot de Telegram y automatización
- **Meta Ads** - Integración con Meta Ads API
- **Device Farm** - Control de dispositivos físicos
- **GoLogin** - Automatización de navegadores
- **Analytics** - Sistema de métricas y reportes

### 💡 Consejos de Uso

1. **Modo Dummy (Desarrollo)**
   - Todas las funcionalidades usan mocks
   - Sin dependencias externas
   - Ideal para testing rápido

2. **Modo Híbrido (Testing)**
   - Activar solo módulos necesarios
   - Combinar mocks con APIs reales
   - Reducir costos de testing

3. **Modo Producción (Live)**
   - Activar módulos progresivamente
   - Monitorear métricas en tiempo real
   - Usar botón rojo ante problemas

### 🔐 Seguridad

**IMPORTANTE:** Este dashboard tiene acceso completo al sistema de producción.

- ⚠️ No compartir la URL HTTPS públicamente
- 🔒 GitHub Codespaces gestiona la autenticación automáticamente
- 🛡️ La URL es única y temporal (asociada a este codespace)

### 📝 Estado Actual

- **Servidor:** Streamlit en background
- **PID:** 201963
- **Puerto:** 8501
- **Modo:** DUMMY (listo para activar producción)
- **Dependencias:** 5/6 críticas, 5/8 opcionales

### 🆘 Soporte

Si el dashboard no responde:

```bash
# 1. Verificar que el proceso está corriendo
ps aux | grep streamlit

# 2. Reiniciar si es necesario
pkill -f "streamlit run"
streamlit run scripts/production_control_dashboard.py --server.port=8501

# 3. Verificar logs
cat ~/.streamlit/logs/streamlit.log
```

---

**Última actualización:** $(date)
**Estado del sistema:** ✅ OPERATIVO
