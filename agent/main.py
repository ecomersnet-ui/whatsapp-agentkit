# agent/main.py — Servidor FastAPI + Webhook de WhatsApp
# Generado por AgentKit

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

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
