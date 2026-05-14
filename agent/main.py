# agent/main.py — Servidor FastAPI + Webhook de WhatsApp
# Generado por AgentKit

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, HTMLResponse

from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial
from agent.providers import obtener_proveedor

# load_dotenv() no funciona en Railway - variables vienen del sistema

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
log_level = logging.DEBUG if ENVIRONMENT == "development" else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger("agentkit")

proveedor = obtener_proveedor()
PORT = int(os.getenv("PORT", 8000))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    logger.info("Base de datos inicializada")
    logger.info(f"Servidor AgentKit en puerto {PORT}")
    logger.info(f"Proveedor: {proveedor.__class__.__name__}")
    yield


app = FastAPI(
    title="AgentKit — WhatsApp AI Agent",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def health_check():
    vonage_key = os.getenv("VONAGE_API_KEY", "NOT_SET")
    return {
        "status": "ok",
        "service": "agentkit",
        "provider": os.getenv("WHATSAPP_PROVIDER", "NOT_SET"),
        "vonage_configured": bool(vonage_key and vonage_key != "NOT_SET")
    }


@app.get("/chat")
async def chat_ui():
    """Interfaz web para probar el bot sin WhatsApp"""
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PolarTech Bot - Chat de Prueba</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .chat-container { width: 100%; max-width: 480px; height: 100vh; max-height: 700px; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); display: flex; flex-direction: column; overflow: hidden; }
        .header { background: #25D366; color: white; padding: 16px; display: flex; align-items: center; gap: 12px; }
        .header img { width: 40px; height: 40px; border-radius: 50%; background: white; }
        .header h3 { font-size: 16px; }
        .header p { font-size: 12px; opacity: 0.9; }
        .messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 8px; background: #e5ddd5; }
        .msg { max-width: 80%; padding: 8px 12px; border-radius: 8px; font-size: 14px; line-height: 1.4; word-wrap: break-word; }
        .msg.bot { background: white; align-self: flex-start; border-radius: 0 8px 8px 8px; }
        .msg.user { background: #dcf8c6; align-self: flex-end; border-radius: 8px 0 8px 8px; }
        .msg .time { font-size: 10px; color: #999; text-align: right; margin-top: 4px; }
        .input-area { padding: 12px; background: #f0f2f5; display: flex; gap: 8px; align-items: center; }
        .input-area input { flex: 1; padding: 10px 14px; border: none; border-radius: 20px; font-size: 14px; outline: none; }
        .input-area button { background: #25D366; color: white; border: none; border-radius: 50%; width: 40px; height: 40px; cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center; }
        .typing { font-size: 12px; color: #666; padding: 4px 8px; }
        pre { white-space: pre-wrap; word-wrap: break-word; font-family: Arial, sans-serif; }
    </style>
</head>
<body>
<div class="chat-container">
    <div class="header">
        <div style="width:40px;height:40px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-size:20px;">🔧</div>
        <div>
            <h3>PolarTech Bot</h3>
            <p>En línea</p>
        </div>
    </div>
    <div class="messages" id="messages">
        <div class="msg bot">¡Hola! Soy el bot de PolarTech. ¿En qué puedo ayudarte?<div class="time">Ahora</div></div>
    </div>
    <div class="typing" id="typing" style="display:none">Bot está escribiendo...</div>
    <div class="input-area">
        <input type="text" id="input" placeholder="Escribí tu mensaje..." onkeydown="if(event.key==='Enter')enviar()">
        <button onclick="enviar()">➤</button>
    </div>
</div>
<script>
async function enviar() {
    const input = document.getElementById('input');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    agregarMensaje(msg, 'user');
    document.getElementById('typing').style.display = 'block';
    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({mensaje: msg, telefono: 'web-test'})
        });
        const data = await res.json();
        document.getElementById('typing').style.display = 'none';
        agregarMensaje(data.respuesta, 'bot');
    } catch(e) {
        document.getElementById('typing').style.display = 'none';
        agregarMensaje('Error de conexión. Intentá de nuevo.', 'bot');
    }
}
function agregarMensaje(texto, tipo) {
    const msgs = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = `msg ${tipo}`;
    const hora = new Date().toLocaleTimeString('es', {hour:'2-digit',minute:'2-digit'});
    div.innerHTML = `<pre>${texto}</pre><div class="time">${hora}</div>`;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
}
</script>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.post("/chat")
async def chat_api(request: Request):
    """API de chat para la interfaz web"""
    try:
        data = await request.json()
        mensaje_texto = data.get("mensaje", "")
        telefono = data.get("telefono", "web-user")

        if not mensaje_texto:
            return {"respuesta": "Mensaje vacío"}

        historial = await obtener_historial(telefono)
        respuesta = await generar_respuesta(mensaje_texto, historial)
        await guardar_mensaje(telefono, "user", mensaje_texto)
        await guardar_mensaje(telefono, "assistant", respuesta)

        return {"respuesta": respuesta, "status": "ok"}
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        return {"respuesta": "Error interno. Intentá de nuevo.", "status": "error"}


@app.get("/webhook")
async def webhook_verificacion(request: Request):
    """Verificación de webhook (GET)"""
    return {"status": "ok", "service": "agentkit-webhook"}


@app.post("/webhook")
async def webhook_handler(request: Request):
    """Manejador de mensajes entrantes desde Vonage"""
    try:
        # Parsear JSON del request
        data = await request.json()

        logger.info(f"Webhook recibido: {data}")

        # Validar webhook
        if not proveedor.validar_webhook(data):
            logger.warning(f"Webhook inválido: {data}")
            return {"status": "invalid"}

        # Parsear mensaje
        mensaje = proveedor.parsear_webhook(data)

        # Ignorar mensajes propios o sin texto
        if mensaje.es_propio or not mensaje.texto:
            return {"status": "ignored"}

        logger.info(f"Mensaje de {mensaje.telefono}: {mensaje.texto}")

        # Obtener historial y generar respuesta
        historial = await obtener_historial(mensaje.telefono)
        respuesta = await generar_respuesta(mensaje.texto, historial)

        # Guardar mensajes en BD
        await guardar_mensaje(mensaje.telefono, "user", mensaje.texto)
        await guardar_mensaje(mensaje.telefono, "assistant", respuesta)

        # Enviar respuesta
        await proveedor.enviar_mensaje(mensaje.telefono, respuesta)

        logger.info(f"Respuesta enviada a {mensaje.telefono}: {respuesta}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error en webhook: {type(e).__name__}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
