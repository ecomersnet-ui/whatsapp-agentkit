# agent/providers/base.py — Clase base para proveedores de WhatsApp
# Generado por AgentKit

from abc import ABC, abstractmethod
from dataclasses import dataclass
from fastapi import Request


@dataclass
class MensajeEntrante:
    telefono: str
    texto: str
    mensaje_id: str
    es_propio: bool


class ProveedorWhatsApp(ABC):
    @abstractmethod
    async def parsear_webhook(self, request: Request) -> list[MensajeEntrante]:
        pass

    @abstractmethod
    async def enviar_mensaje(self, telefono: str, mensaje: str) -> bool:
        pass

    async def validar_webhook(self, request: Request):
        return None
