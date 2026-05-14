# PUNTO DE RETOMA - PolarTech WhatsApp Bot

**Fecha de pausa:** 2026-05-14  
**Estado:** 95% COMPLETADO

---

## ✅ LO QUE FUNCIONA AL 100%

| Componente | Estado |
|-----------|--------|
| Bot Railway Online | ✅ Corriendo |
| Claude AI | ✅ Genera respuestas perfectas |
| Webhook recibe mensajes | ✅ Funciona |
| Base de datos | ✅ Guarda historial |
| Variables Railway | ✅ Configuradas |
| GitHub sincronizado | ✅ Actualizado |

**URL del bot:**
```
https://whatsapp-agentkit-production-1f16.up.railway.app
```

**Test rápido de que está vivo:**
```bash
curl https://whatsapp-agentkit-production-1f16.up.railway.app/
# Debe responder: {"status":"ok","provider":"vonage","vonage_configured":true}
```

---

## 🔴 ÚNICO PASO PENDIENTE

### Credenciales incorrectas de Vonage

**Problema:** El bot usa `VONAGE_API_KEY=36a26e86` pero Vonage responde `401 Unauthorized`.

**Causa:** `36a26e86` es el **Application ID**, no el API Key real.

**Solución:**
1. Abrir: `https://dashboard.vonage.com` (página HOME)
2. Buscar el bloque con **API key** y **API secret**
3. Dar esos valores al asistente
4. El asistente actualiza Railway con los valores correctos (2 minutos)

**Diferencia:**
```
INCORRECTO (lo que tenemos): Application ID = 36a26e86
CORRECTO (lo que necesitamos): API Key = (número de 8 caracteres del HOME del dashboard)
```

---

## CREDENCIALES ACTUALES EN RAILWAY

```
VONAGE_API_KEY=36a26e86       ← ESTA HAY QUE CAMBIAR
VONAGE_API_SECRET=vSUc0q0Xb8Gmm6is  ← Esta puede estar bien o también cambiar
VONAGE_BRAND=polartech
WHATSAPP_PROVIDER=vonage
ENVIRONMENT=production
PORT=8000
ANTHROPIC_API_KEY=(la nueva key generada el 14/05/2026)
DATABASE_URL=sqlite+aiosqlite:///./agentkit.db
```

---

## RAILWAY CLI (para cuando retomes)

Token de acceso guardado (válido):
```
RAILWAY_API_TOKEN=2594c4a7-ba14-4e6f-9897-40af1749b5c0
```

Comandos útiles:
```bash
cd C:\Users\empre\whatsapp-agentkit

# Ver logs
RAILWAY_API_TOKEN=2594c4a7-ba14-4e6f-9897-40af1749b5c0 railway logs --tail 20

# Actualizar variable
RAILWAY_API_TOKEN=2594c4a7-ba14-4e6f-9897-40af1749b5c0 railway variables set VONAGE_API_KEY=NUEVA_KEY

# Ver variables
RAILWAY_API_TOKEN=2594c4a7-ba14-4e6f-9897-40af1749b5c0 railway variables
```

---

## CUANDO REGRESES: 3 PASOS (5 minutos total)

### Paso 1: Obtener API Key correcta de Vonage
```
Ir a: https://dashboard.vonage.com (HOME)
Copiar: API key y API secret del bloque principal
```

### Paso 2: Actualizar Railway (automático)
```bash
RAILWAY_API_TOKEN=2594c4a7-ba14-4e6f-9897-40af1749b5c0 railway variables set VONAGE_API_KEY=TU_KEY_REAL VONAGE_API_SECRET=TU_SECRET_REAL
```

### Paso 3: También registrar número en Sandbox Vonage
```
Ir a: https://dashboard.vonage.com/messages/sandbox
Agregar tu número: +541130003552
Enviar desde tu WhatsApp al número de sandbox: "join [palabra-que-te-dan]"
```

### Paso 4: Test final
```
Enviar WhatsApp al número de Vonage
Verificar que el bot responde
```

---

## ARQUITECTURA TÉCNICA (para contexto)

```
Tu WhatsApp → Vonage → Railway (FastAPI) → Claude AI → Vonage → Tu WhatsApp
```

- **Framework:** FastAPI + SQLAlchemy + SQLite
- **AI:** Claude Sonnet (Anthropic)
- **WhatsApp:** Vonage Messages Sandbox
- **Deploy:** Railway (auto-deploy desde GitHub)
- **Repositorio:** github.com/ecomersnet-ui/whatsapp-agentkit

---

## VERIFICACIÓN RÁPIDA AL RETOMAR

```bash
# 1. Verificar que bot sigue online
curl https://whatsapp-agentkit-production-1f16.up.railway.app/

# 2. Test del webhook
curl -X POST https://whatsapp-agentkit-production-1f16.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"message_uuid":"test","from":"541130003552","to":"14155552671","text":"hola","channel":"whatsapp","message_type":"whatsapp"}'
```

Ambos deben responder con `{"status":"ok"}`
