# Manual de Deploy en Railway - Alternativa

Si el auto-deploy automático de Railway no funciona, sigue estos pasos para hacer deploy manual:

## Opción 1: Deploy Manual en Railway (Recomendado)

### Paso 1: Conectar GitHub en Railway
```
1. Abre: https://railway.app/dashboard
2. Click: "+ New Project"
3. Selecciona: "Deploy from GitHub"
4. Conecta tu cuenta GitHub
5. Selecciona: ecomersnet-ui/whatsapp-agentkit
```

### Paso 2: Configurar Variables de Entorno
```
En Railway Dashboard:
1. Click: whatsapp-agentkit
2. Variables tab
3. Agregar:
   - VONAGE_API_KEY=36a26e86
   - VONAGE_API_SECRET=vSUc0q0Xb8Gmm6is
   - WHATSAPP_PROVIDER=vonage
   - ANTHROPIC_API_KEY=(tu nueva key)
   - ENVIRONMENT=production
   - PORT=8000
4. Save
```

### Paso 3: Esperar Deploy
- Railway hará build automático
- Esperar ~3-5 minutos
- Ver "Deploy Successful" en verde

---

## Opción 2: Deploy Local (Para Testing)

Si Railway sigue dando problemas, puedes hacer que el bot funcione localmente:

```bash
cd C:\Users\empre\whatsapp-agentkit

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el bot
python -m uvicorn agent.main:app --host 0.0.0.0 --port 8000

# El bot estará en: http://localhost:8000
```

Configura Vonage webhook para apuntar a tu IP local:
```
http://TU_IP_LOCAL:8000/webhook
```

---

## Opción 3: Heroku / Render / Otros

Si Railway no funciona, considera:
- **Render.com** - Similar a Railway
- **Heroku** - Clásico, muy confiable
- **Fly.io** - Moderno
- **Digital Ocean** - Más control

---

## Si Todo Falla: Test Local

El bot funciona 100% localmente. Puedes testear con:

```bash
python tests/test_local.py
```

Y enviar mensajes como si fueras un cliente de WhatsApp.

---

## Soporte

Si persisten los problemas:
1. Verifica que Railway tiene acceso a tu repo GitHub
2. Revisa los Logs en Railway Dashboard
3. Intenta "Redeploy" manualmente en Railway
4. Contacta a support@railway.app

El código está 100% correcto (testeado localmente). Si Railway falla, es un problema de configuración en su plataforma.
