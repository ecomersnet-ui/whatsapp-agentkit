# PUNTO DE RETOMA - PolarTech WhatsApp Bot

**Fecha de pausa:** 2026-05-14  
**Estado:** ✅ BOT 100% FUNCIONAL Y COMPLETO

---

## ✅ TODO FUNCIONA AL 100%

| Componente | Estado |
|-----------|--------|
| Bot Railway Online | ✅ Corriendo |
| Claude AI (respuestas) | ✅ Perfecto |
| WhatsApp via Vonage | ✅ Enviando y recibiendo |
| Panel Admin | ✅ Funcionando |
| Chat Web | ✅ Funcionando |
| Sitio web en respuestas | ✅ www.polartechsrl.com |
| Instagram en respuestas | ✅ instagram.com/polartechsrl |
| Base de datos | ✅ Guarda historial |

---

## 🔗 URLs IMPORTANTES

| Recurso | URL |
|---------|-----|
| Bot (salud) | https://whatsapp-agentkit-production-1f16.up.railway.app/ |
| Chat Web | https://whatsapp-agentkit-production-1f16.up.railway.app/chat |
| Panel Admin | https://whatsapp-agentkit-production-1f16.up.railway.app/admin |
| Número WhatsApp Sandbox | +14157386102 |

---

## 📱 CÓMO USAR EL BOT (Sandbox Vonage)

1. Desde WhatsApp enviar al **+14157386102**:
   ```
   Join pork coach
   ```
2. Recibir "Thank you! Your number is now set up..."
3. Escribir cualquier mensaje → el bot responde

**⚠️ La whitelist expira periódicamente.** Si el bot no responde, repetir paso 1.

**Si el bot deja de responder completamente**, verificar que los webhooks sigan apuntando a:
- Inbound: `https://whatsapp-agentkit-production-1f16.up.railway.app/webhook`
- Status: `https://whatsapp-agentkit-production-1f16.up.railway.app/webhook/status`
- En: https://dashboard.vonage.com/messages/sandbox → sección Webhooks → "Save webhooks"

---

## 🎛️ PANEL DE ADMIN

Abrí en el navegador:
```
https://whatsapp-agentkit-production-1f16.up.railway.app/admin
```
- Ver todos los clientes que escribieron
- Estadísticas: mensajes hoy, semana, total
- Click en cualquier fila → conversación completa

---

## 📋 PRÓXIMOS PASOS SUGERIDOS

### Opción A: Agregar bot al sitio web (30 min)
Poner un botón/widget en www.polartechsrl.com que abra:
```
https://whatsapp-agentkit-production-1f16.up.railway.app/chat
```

### Opción B: Usar número propio de WhatsApp (3-7 días)
Para que el bot responda desde el número de PolarTech:
- Registrar en Meta WhatsApp Business API
- Ver: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

### Opción C: Mejorar el bot
- Agregar precios de servicios
- Agregar formulario de presupuesto
- Notificaciones por email cuando llega un cliente nuevo

---

## 🔐 SEGURIDAD PENDIENTE

- [ ] Regenerar ANTHROPIC_API_KEY (fue expuesta en conversaciones)
  - Ir a: https://platform.anthropic.com/settings/api-keys
  - Crear nueva y actualizar en Railway dashboard

---

## RAILWAY CLI (para revisar logs)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
$env:RAILWAY_API_TOKEN="(tu token de Railway)"
Set-Location "C:\Users\empre\whatsapp-agentkit"
railway logs --tail 30
```

---

## ARQUITECTURA

```
WhatsApp → Vonage Sandbox (+14157386102) → Railway FastAPI → Claude AI → Vonage → WhatsApp
Web → /chat → Railway FastAPI → Claude AI → respuesta JSON
```

- **Framework:** FastAPI + SQLAlchemy + SQLite
- **AI:** Claude Sonnet (Anthropic)
- **WhatsApp:** Vonage Messages Sandbox
- **Deploy:** Railway (auto-deploy desde GitHub)
- **Repo:** github.com/ecomersnet-ui/whatsapp-agentkit
