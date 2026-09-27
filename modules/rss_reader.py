"""
Lectura y parseo de feeds RSS.

Se encarga de leer las fuentes configuradas, extraer los items y detectar
cuales son nuevos comparando contra la base de datos de items vistos.
"""

import json
from pathlib import Path

import feedparser

from modules import db

RUTA_FUENTES = Path(__file__).resolve().parent.parent / "config" / "fuentes.json"


def cargar_fuentes() -> list[dict]:
    """Carga la lista de fuentes configuradas desde config/fuentes.json."""
    with open(RUTA_FUENTES, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def _obtener_id_item(entrada) -> str:
    """Obtiene un identificador unico para una entrada del feed."""
    return getattr(entrada, "id", None) or getattr(entrada, "link", None) or entrada.get("title", "")


def _obtener_miniatura(entrada) -> str | None:
    """Extrae la URL de la miniatura de una entrada, si el feed la trae."""
    if hasattr(entrada, "media_thumbnail") and entrada.media_thumbnail:
        return entrada.media_thumbnail[0].get("url")
    if hasattr(entrada, "media_content") and entrada.media_content:
        return entrada.media_content[0].get("url")
    return None


def obtener_items_nuevos(fuente: dict) -> list[dict]:
    """
    Lee una fuente RSS y devuelve solo los items que no fueron vistos antes.

    Si el feed falla al parsearse, devuelve una lista vacia y no interrumpe
    la ejecucion del resto del script.
    """
    url_fuente = fuente["url"]
    items_nuevos = []

    try:
        feed = feedparser.parse(url_fuente)

        if feed.bozo and not feed.entries:
            print(f"Aviso: no se pudo leer el feed de '{fuente['nombre']}' ({url_fuente})")
            return []

        for entrada in feed.entries:
            id_item = _obtener_id_item(entrada)
            if not id_item:
                continue

            if db.item_ya_visto(id_item, url_fuente):
                continue

            items_nuevos.append(
                {
                    "id_item": id_item,
                    "titulo": entrada.get("title", "Sin titulo"),
                    "link": entrada.get("link", ""),
                    "miniatura": _obtener_miniatura(entrada),
                    "fuente": fuente["nombre"],
                    "categoria": fuente["categoria"],
                    "url_fuente": url_fuente,
                }
            )

        return items_nuevos

    except Exception as error:
        print(f"Error al procesar el feed de '{fuente['nombre']}': {error}")
        return []
