# agent/providers/__init__.py — Factory de proveedores
# Generado por AgentKit

import os
from agent.providers.base import ProveedorWhatsApp


def obtener_proveedor() -> ProveedorWhatsApp:
    proveedor = os.getenv("WHATSAPP_PROVIDER", "").lower()

    if proveedor == "twilio":
        from agent.providers.twilio import ProveedorTwilio
        return ProveedorTwilio()
    elif proveedor == "meta":
        from agent.providers.meta import ProveedorMeta
        return ProveedorMeta()
    elif proveedor == "vonage":
        from agent.providers.vonage import ProveedorVonage
        return ProveedorVonage()
    else:
        raise ValueError(f"WHATSAPP_PROVIDER no válido. Usa 'twilio', 'meta' o 'vonage'")
