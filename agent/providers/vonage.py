# agent/providers/vonage.py — Proveedor Vonage (Nexmo) para WhatsApp
# Implementación para Argentina

import os
import json
import logging
from dataclasses import dataclass
import httpx
from .base import ProveedorWhatsApp, MensajeEntrante

logger = logging.getLogger("agentkit")


@dataclass
class MensajeVonage:
    """Estructura de mensaje de Vonage"""
    from_number: str
    to_number: str
    text: str
    message_uuid: str


class ProveedorVonage(ProveedorWhatsApp):
    """Proveedor Vonage para WhatsApp Business API en Argentina"""

    def __init__(self):
        self.api_key = os.getenv("VONAGE_API_KEY")
        self.api_secret = os.getenv("VONAGE_API_SECRET")
        self.vonage_brand = os.getenv("VONAGE_BRAND", "polartech")
        self.base_url = "https://messages-sandbox.nexmo.com"

        if not self.api_key or not self.api_secret:
            logger.error("VONAGE_API_KEY o VONAGE_API_SECRET no configuradas")

    def parsear_webhook(self, data: dict) -> MensajeEntrante:
        """
        Parsear webhook de Vonage

        Formato esperado:
        {
            "message_uuid": "xxx",
            "to": "14155552671",
            "from": "447700900123",
            "timestamp": "2020-01-01T12:00:00Z",
            "message_type": "whatsapp",
            "text": "Hello World",
            "channel": "whatsapp",
            "message_status": "submitted"
        }
        """
        try:
            return MensajeEntrante(
                telefono=data.get("from", ""),
                texto=data.get("text", ""),
                mensaje_id=data.get("message_uuid", ""),
                es_propio=False
            )
        except Exception as e:
            logger.error(f"Error parseando webhook de Vonage: {e}")
            raise

    async def enviar_mensaje(self, telefono: str, texto: str) -> bool:
        """
        Enviar mensaje por Vonage

        Args:
            telefono: Número de teléfono en formato internacional (+54...)
            texto: Contenido del mensaje

        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        try:
            # Releer variables en cada envío (por si se cargaron después del init)
            api_key = os.getenv("VONAGE_API_KEY") or self.api_key
            api_secret = os.getenv("VONAGE_API_SECRET") or self.api_secret
            brand = os.getenv("VONAGE_BRAND") or self.vonage_brand

            if not api_key or not api_secret:
                logger.error(f"Vonage no configurado. KEY={api_key}, SECRET={'***' if api_secret else None}")
                return False

            payload = {
                "to": telefono,
                "from": brand,
                "message_type": "text",
                "text": texto,
                "channel": "whatsapp"
            }

            logger.info(f"Enviando a Vonage: to={telefono}, from={brand}")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/messages",
                    json=payload,
                    auth=(api_key, api_secret),
                    timeout=15.0
                )

                logger.info(f"Vonage response: {response.status_code} - {response.text[:200]}")

                if response.status_code in (200, 202):
                    logger.info(f"Mensaje enviado exitosamente a {telefono}")
                    return True
                else:
                    logger.error(f"Error Vonage {response.status_code}: {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Error en enviar_mensaje (Vonage): {e}", exc_info=True)
            return False

    def validar_webhook(self, request_data: dict) -> bool:
        """
        Validar que el webhook es de Vonage

        Vonage incluye un campo 'api_key' en el webhook para validación
        """
        try:
            # Validar que el request contiene los campos esperados
            required_fields = ["from", "to", "text", "message_uuid"]
            return all(field in request_data for field in required_fields)
        except Exception as e:
            logger.error(f"Error validando webhook: {e}")
            return False
