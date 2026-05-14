# agent/main.py — Servidor FastAPI + Webhook de WhatsApp
# Generado por AgentKit

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, HTMLResponse

from agent.brain import generar_respuesta
from agent.memory import (
    inicializar_db, guardar_mensaje, obtener_historial,
    obtener_clientes, obtener_conversacion_completa, obtener_estadisticas
)
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


# ── Panel de Administración ───────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Panel de administración — lista de clientes y estadísticas"""
    stats = await obtener_estadisticas()
    clientes = await obtener_clientes()

    clientes_html = ""
    for c in clientes:
        numero = c["telefono"]
        ultimo = c["ultimo"].strftime("%d/%m %H:%M") if c["ultimo"] else "-"
        preview = c["ultimo_mensaje"].replace("<", "&lt;").replace(">", "&gt;")
        badge = "🟢" if c["ultimo_role"] == "assistant" else "🔵"
        clientes_html += f"""
        <tr onclick="verChat('{numero}')" style="cursor:pointer">
            <td><span style="font-family:monospace;font-size:13px">+{numero}</span></td>
            <td style="text-align:center">{c['total']}</td>
            <td>{ultimo}</td>
            <td style="color:#888;font-size:13px">{badge} {preview}...</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PolarTech Admin — Conversaciones</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: Arial, sans-serif; background:#1a1a2e; color:#eee; min-height:100vh; }}
  .header {{ background:linear-gradient(135deg,#16213e,#0f3460); padding:20px 30px; display:flex; align-items:center; gap:15px; box-shadow:0 2px 10px rgba(0,0,0,.5); }}
  .header h1 {{ font-size:22px; color:#e94560; }}
  .header p {{ font-size:13px; color:#aaa; margin-top:3px; }}
  .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:15px; padding:25px 30px 10px; }}
  .stat {{ background:#16213e; border-radius:10px; padding:18px; text-align:center; border:1px solid #0f3460; }}
  .stat .num {{ font-size:36px; font-weight:bold; color:#e94560; }}
  .stat .lbl {{ font-size:12px; color:#aaa; margin-top:5px; }}
  .section {{ padding:20px 30px; }}
  .section h2 {{ color:#e94560; margin-bottom:15px; font-size:16px; text-transform:uppercase; letter-spacing:1px; }}
  table {{ width:100%; border-collapse:collapse; background:#16213e; border-radius:10px; overflow:hidden; }}
  th {{ background:#0f3460; padding:12px 15px; text-align:left; font-size:12px; text-transform:uppercase; color:#aaa; letter-spacing:1px; }}
  td {{ padding:12px 15px; border-bottom:1px solid #0f3460; font-size:14px; }}
  tr:hover td {{ background:#1a2744; }}
  tr:last-child td {{ border-bottom:none; }}

  /* Modal chat */
  .modal {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,.7); z-index:100; align-items:center; justify-content:center; }}
  .modal.open {{ display:flex; }}
  .modal-box {{ background:#16213e; border-radius:12px; width:90%; max-width:650px; max-height:85vh; display:flex; flex-direction:column; border:1px solid #0f3460; }}
  .modal-header {{ padding:18px 20px; border-bottom:1px solid #0f3460; display:flex; justify-content:space-between; align-items:center; }}
  .modal-header h3 {{ color:#e94560; font-size:16px; }}
  .modal-close {{ background:none; border:none; color:#aaa; font-size:22px; cursor:pointer; }}
  .modal-body {{ flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column; gap:10px; }}
  .msg {{ max-width:78%; padding:10px 14px; border-radius:10px; font-size:13px; line-height:1.5; }}
  .msg.user {{ background:#0f3460; align-self:flex-end; border-radius:10px 0 10px 10px; }}
  .msg.assistant {{ background:#1e3a5f; align-self:flex-start; border-radius:0 10px 10px 10px; }}
  .msg .meta {{ font-size:10px; color:#888; margin-top:5px; text-align:right; }}
  .empty {{ color:#555; text-align:center; padding:40px; }}
</style>
</head>
<body>

<div class="header">
  <div style="font-size:32px">🤖</div>
  <div>
    <h1>PolarTech Admin</h1>
    <p>Panel de conversaciones del ChatBot</p>
  </div>
  <div style="margin-left:auto; font-size:12px; color:#888">
    Actualizado: <span id="ts"></span>
  </div>
</div>

<div class="stats">
  <div class="stat"><div class="num">{stats["total_clientes"]}</div><div class="lbl">👥 Clientes únicos</div></div>
  <div class="stat"><div class="num">{stats["mensajes_hoy"]}</div><div class="lbl">💬 Mensajes hoy</div></div>
  <div class="stat"><div class="num">{stats["mensajes_semana"]}</div><div class="lbl">📅 Esta semana</div></div>
  <div class="stat"><div class="num">{stats["total_mensajes"]}</div><div class="lbl">📊 Total mensajes</div></div>
</div>

<div class="section">
  <h2>💬 Conversaciones ({len(clientes)} clientes)</h2>
  {'<p class="empty">No hay conversaciones todavía.</p>' if not clientes else f"""
  <table>
    <thead><tr>
      <th>Número</th><th style="text-align:center">Msgs</th><th>Último contacto</th><th>Último mensaje</th>
    </tr></thead>
    <tbody>{clientes_html}</tbody>
  </table>"""}
</div>

<!-- Modal conversación -->
<div class="modal" id="modal">
  <div class="modal-box">
    <div class="modal-header">
      <h3 id="modal-title">Conversación</h3>
      <button class="modal-close" onclick="cerrarModal()">✕</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>

<script>
document.getElementById('ts').textContent = new Date().toLocaleString('es');

async function verChat(tel) {{
  document.getElementById('modal-title').textContent = '+' + tel;
  document.getElementById('modal-body').innerHTML = '<p class="empty">Cargando...</p>';
  document.getElementById('modal').classList.add('open');
  const res = await fetch('/admin/conversacion/' + tel);
  const msgs = await res.json();
  if (!msgs.length) {{
    document.getElementById('modal-body').innerHTML = '<p class="empty">Sin mensajes</p>';
    return;
  }}
  document.getElementById('modal-body').innerHTML = msgs.map(m => `
    <div class="msg ${{m.role}}">
      ${{m.content.replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>')}}
      <div class="meta">${{m.timestamp}}</div>
    </div>`).join('');
  document.getElementById('modal-body').scrollTop = 99999;
}}

function cerrarModal() {{
  document.getElementById('modal').classList.remove('open');
}}
document.getElementById('modal').addEventListener('click', e => {{
  if (e.target === document.getElementById('modal')) cerrarModal();
}});
</script>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.get("/admin/conversacion/{telefono}")
async def admin_conversacion(telefono: str):
    """API: devuelve los mensajes de un cliente para el modal"""
    mensajes = await obtener_conversacion_completa(telefono)
    return mensajes
