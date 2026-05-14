# agent/memory.py — Memoria de conversaciones con SQLite
# Generado por AgentKit

import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, select, Integer
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./agentkit.db")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Mensaje(Base):
    __tablename__ = "mensajes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telefono: Mapped[str] = mapped_column(String(50), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def inicializar_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def guardar_mensaje(telefono: str, role: str, content: str):
    async with async_session() as session:
        mensaje = Mensaje(
            telefono=telefono,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        session.add(mensaje)
        await session.commit()


async def obtener_historial(telefono: str, limite: int = 20) -> list[dict]:
    async with async_session() as session:
        query = (
            select(Mensaje)
            .where(Mensaje.telefono == telefono)
            .order_by(Mensaje.timestamp.desc())
            .limit(limite)
        )
        result = await session.execute(query)
        mensajes = result.scalars().all()

        mensajes.reverse()

        return [
            {"role": msg.role, "content": msg.content}
            for msg in mensajes
        ]


async def limpiar_historial(telefono: str):
    async with async_session() as session:
        query = select(Mensaje).where(Mensaje.telefono == telefono)
        result = await session.execute(query)
        mensajes = result.scalars().all()
        for msg in mensajes:
            session.delete(msg)
        await session.commit()


# ── Funciones Admin ────────────────────────────────────────

async def obtener_clientes() -> list[dict]:
    """Retorna lista de clientes con su último mensaje y total de mensajes."""
    from sqlalchemy import func, desc
    async with async_session() as session:
        # Subconsulta: último timestamp por teléfono
        subq = (
            select(
                Mensaje.telefono,
                func.max(Mensaje.timestamp).label("ultimo"),
                func.count(Mensaje.id).label("total")
            )
            .group_by(Mensaje.telefono)
            .subquery()
        )
        result = await session.execute(
            select(subq).order_by(desc(subq.c.ultimo))
        )
        rows = result.fetchall()

        clientes = []
        for row in rows:
            # Obtener el último mensaje de ese cliente
            last_msg_q = (
                select(Mensaje)
                .where(Mensaje.telefono == row.telefono)
                .order_by(desc(Mensaje.timestamp))
                .limit(1)
            )
            lm_result = await session.execute(last_msg_q)
            last_msg = lm_result.scalar_one_or_none()
            clientes.append({
                "telefono": row.telefono,
                "ultimo": row.ultimo,
                "total": row.total,
                "ultimo_mensaje": last_msg.content[:80] if last_msg else "",
                "ultimo_role": last_msg.role if last_msg else ""
            })
        return clientes


async def obtener_conversacion_completa(telefono: str) -> list[dict]:
    """Retorna todos los mensajes de un cliente con timestamps."""
    from sqlalchemy import asc
    async with async_session() as session:
        query = (
            select(Mensaje)
            .where(Mensaje.telefono == telefono)
            .order_by(asc(Mensaje.timestamp))
        )
        result = await session.execute(query)
        mensajes = result.scalars().all()
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.strftime("%d/%m/%Y %H:%M")
            }
            for msg in mensajes
        ]


async def obtener_estadisticas() -> dict:
    """Retorna estadísticas generales del bot."""
    from sqlalchemy import func, distinct
    from datetime import timedelta
    async with async_session() as session:
        hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        semana = hoy - timedelta(days=7)

        total_clientes = await session.execute(
            select(func.count(distinct(Mensaje.telefono)))
        )
        total_mensajes = await session.execute(select(func.count(Mensaje.id)))
        mensajes_hoy = await session.execute(
            select(func.count(Mensaje.id)).where(Mensaje.timestamp >= hoy)
        )
        mensajes_semana = await session.execute(
            select(func.count(Mensaje.id)).where(Mensaje.timestamp >= semana)
        )
        mensajes_user = await session.execute(
            select(func.count(Mensaje.id)).where(Mensaje.role == "user")
        )

        return {
            "total_clientes": total_clientes.scalar() or 0,
            "total_mensajes": total_mensajes.scalar() or 0,
            "mensajes_hoy": mensajes_hoy.scalar() or 0,
            "mensajes_semana": mensajes_semana.scalar() or 0,
            "mensajes_user": mensajes_user.scalar() or 0,
        }
