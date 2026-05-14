# PUNTO DE RETOMA - PolarTech WhatsApp Bot

**Fecha de pausa:** 2026-05-14  
**Estado:** ✅ BOT 100% FUNCIONAL EN WHATSAPP

---

## ✅ TODO FUNCIONA AL 100%

| Componente | Estado |
|-----------|--------|
| Bot Railway Online | ✅ Corriendo |
| Claude AI | ✅ Genera respuestas perfectas |
| Webhook recibe mensajes | ✅ Funciona |
| Vonage envía a WhatsApp | ✅ 202 Accepted |
| Números Argentina (AR) | ✅ Normalización automática |
| Base de datos | ✅ Guarda historial |
| Chat Web | ✅ Funcionando |

**URL del bot:**
```
https://whatsapp-agentkit-production-1f16.up.railway.app
```

**Chat Web (para sitio web):**
```
https://whatsapp-agentkit-production-1f16.up.railway.app/chat
```

---

## 📱 CÓMO USAR EL BOT AHORA (Sandbox)

1. Desde WhatsApp enviar al **+14157386102**:
   ```
   Join pork coach
   ```
2. Recibir confirmación "Thank you! Your number is now set up..."
3. Escribir cualquier mensaje → el bot responde automáticamente

**⚠️ IMPORTANTE:** La whitelist del sandbox expira cada cierto tiempo.  
Si el bot no responde, volver a enviar `Join pork coach` al +14157386102.

---

## 🔧 FIXES APLICADOS EN ESTA SESIÓN

### 1. Normalización números Argentina
- Problema: Vonage enviaba `541130003552` pero WhatsApp requiere `5491130003552` (con el 9)
- Fix: `normalizar_telefono_argentina()` en `agent/providers/vonage.py`
- Deployed: ✅ Commit `570b993`

### 2. Número FROM del sandbox
- Problema: Usaba `polartech` como remitente → 403 Forbidden
- Fix: Ahora usa `14157386102` (número sandbox de Vonage)
- Variable Railway: `VONAGE_FROM_NUMBER=14157386102` ✅

### 3. URL Webhook del Sandbox
- Problema: Estaba apuntando a `https://www.vonage.com` (!)
- Fix: Usuario actualizó en dashboard.vonage.com/messages/sandbox → Webhooks
- URLs correctas:
  - Inbound: `https://whatsapp-agentkit-production-1f16.up.railway.app/webhook`
  - Status: `https://whatsapp-agentkit-production-1f16.up.railway.app/webhook/status`

---

## 📋 PRÓXIMOS PASOS (cuando regreses)

### Opción A: Poner chat en sitio web (30 min)
Agregar un botón/widget en la web que abra:
```
https://whatsapp-agentkit-production-1f16.up.railway.app/chat
```

### Opción B: Usar número propio de WhatsApp (3-7 días)
Para que el bot responda desde el número de PolarTech (+541130003552):
1. Registrar el número en Meta WhatsApp Business API
2. Requiere verificación de negocio en Facebook Business
3. URL: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

---

## VARIABLES EN RAILWAY (completas)

```
ANTHROPIC_API_KEY=(ver en Railway dashboard - no guardar aquí)
WHATSAPP_PROVIDER=vonage
VONAGE_API_KEY=36a26e86
VONAGE_API_SECRET=(ver en Railway dashboard)
VONAGE_BRAND=polartech
VONAGE_FROM_NUMBER=14157386102
PORT=8000
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:///./agentkit.db
```

---

## RAILWAY CLI (si necesitás revisar logs)

```bash
# En PowerShell (como Administrador o con bypass):
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
$env:RAILWAY_API_TOKEN="(tu token de Railway)"
Set-Location "C:\Users\empre\whatsapp-agentkit"
railway logs --tail 30
```

---

## VERIFICACIÓN RÁPIDA AL RETOMAR

```powershell
# 1. Verificar que bot sigue online
Invoke-WebRequest -Uri "https://whatsapp-agentkit-production-1f16.up.railway.app/" -UseBasicParsing

# 2. Probar chat web
# Abrir en navegador: https://whatsapp-agentkit-production-1f16.up.railway.app/chat
```

---

## ARQUITECTURA TÉCNICA

```
Tu WhatsApp → Vonage Sandbox (+14157386102) → Railway (FastAPI) → Claude AI → Vonage → Tu WhatsApp
```

- **Framework:** FastAPI + SQLAlchemy + SQLite
- **AI:** Claude Sonnet (Anthropic)
- **WhatsApp:** Vonage Messages Sandbox
- **Deploy:** Railway (auto-deploy desde GitHub)
- **Repositorio:** github.com/ecomersnet-ui/whatsapp-agentkit

---

## 🔐 SEGURIDAD PENDIENTE

- [ ] Regenerar ANTHROPIC_API_KEY (fue compartida en conversaciones anteriores)
  - Ir a: https://platform.anthropic.com/settings/api-keys
  - Crear nueva key y actualizar en Railway
- [ ] Rotar RAILWAY_API_TOKEN si ya no se necesita
