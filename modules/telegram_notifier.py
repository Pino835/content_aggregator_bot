"""
Envio de notificaciones a Telegram.

Formatea y envia los items nuevos detectados, ya sea de forma individual
o agrupados en un resumen diario.
"""

import asyncio
import os

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def _formatear_item(item: dict) -> str:
    """Da formato de mensaje de Telegram a un item nuevo."""
    return (
        f"🆕 Nuevo en {item['categoria']}\n"
        f"📺 {item['titulo']}\n"
        f"🔗 {item['link']}\n"
        f"Fuente: {item['fuente']}"
    )


async def _enviar_mensaje(bot: Bot, texto: str, miniatura: str | None = None):
    """Envia un mensaje a Telegram, con foto si hay miniatura disponible."""
    try:
        if miniatura:
            await bot.send_photo(chat_id=CHAT_ID, photo=miniatura, caption=texto)
        else:
            await bot.send_message(chat_id=CHAT_ID, text=texto, disable_web_page_preview=False)
    except TelegramError as error:
        print(f"Error al enviar mensaje a Telegram: {error}")


async def _enviar_items_async(items: list[dict]):
    """Envia cada item nuevo como un mensaje individual."""
    if not TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configurados en .env")
        return

    bot = Bot(token=TOKEN)
    for item in items:
        texto = _formatear_item(item)
        await _enviar_mensaje(bot, texto, item.get("miniatura"))


async def _enviar_resumen_async(items: list[dict]):
    """Agrupa todos los items nuevos por categoria y los envia en un solo mensaje."""
    if not TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configurados en .env")
        return

    if not items:
        return

    items_por_categoria: dict[str, list[dict]] = {}
    for item in items:
        items_por_categoria.setdefault(item["categoria"], []).append(item)

    bloques = ["📋 Resumen diario de contenido nuevo\n"]
    for categoria, items_categoria in items_por_categoria.items():
        bloques.append(f"\n📂 {categoria.upper()}")
        for item in items_categoria:
            bloques.append(f"📺 {item['titulo']}\n🔗 {item['link']} ({item['fuente']})")

    texto = "\n".join(bloques)

    bot = Bot(token=TOKEN)
    await _enviar_mensaje(bot, texto)


def enviar_items_nuevos(items: list[dict]):
    """Punto de entrada sincrono para enviar items nuevos individualmente."""
    if not items:
        return
    asyncio.run(_enviar_items_async(items))


def enviar_resumen_diario(items: list[dict]):
    """Punto de entrada sincrono para enviar el resumen diario agrupado."""
    asyncio.run(_enviar_resumen_async(items))
