# Regeneración de API Key - SEGURIDAD CRÍTICA

## ⚠️ SITUACIÓN ACTUAL
Tu API key de Anthropic fue compartida en el chat y está expuesta.

**ESTA KEY DEBE SER ELIMINADA INMEDIATAMENTE** después de que Railway funcione con la nueva key.

La key actual comienza con: `sk-ant-api03-...` (ver en .env localmente)

---

## PASOS PARA REGENERAR

### 1. Crear Nueva API Key
```
1. Ir a: https://platform.anthropic.com/settings/api-keys
2. Click botón: "Create Key"
3. Dar nombre: "polartech-bot-v2"
4. Click: "Create"
5. COPIAR la nueva key (aparece una sola vez)
```

### 2. Actualizar .env (local)
```
Archivo: C:\Users\empre\whatsapp-agentkit\.env

CAMBIAR:
ANTHROPIC_API_KEY=(la key antigua que comienza con sk-ant-api03-...)

POR:
ANTHROPIC_API_KEY=(la NUEVA key que copiaste de Anthropic)
```

### 3. Actualizar Railway
```
1. Ir a: https://railway.app/dashboard
2. Click: whatsapp-agentkit
3. Click pestaña: Variables
4. Buscar: ANTHROPIC_API_KEY
5. Editar y pegar la NUEVA key
6. Click: Save/Deploy
7. Esperar redeploy (2-3 min)
```

### 4. Eliminar Key Vieja (EN ANTHROPIC)
```
1. Ir a: https://platform.anthropic.com/settings/api-keys
2. Buscar la key que comienza con "sk-ant-api03-A8csE0..."
3. Click botón: Delete (papelera)
4. Confirmar: Delete
```

---

## ✅ VERIFICAR QUE FUNCIONÓ

```bash
cd C:\Users\empre\whatsapp-agentkit
python tests/test_local.py
```

Enviar un mensaje: "Hola, ¿qué servicios ofrecen?"

Debería responder normalmente.

---

## ⏰ TIMELINE RECOMENDADO

1. **Ahora:** Railway con Vonage (2 min)
2. **Después de Railway OK:** Regenerar API key Anthropic (5 min)
3. **Luego:** Test con un mensaje WhatsApp real (1 min)
4. **Finalmente:** Push a GitHub si todo funciona

Total: ~15 minutos para estar 100% listo.
