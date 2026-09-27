"""
Manejo de la base de datos SQLite para no repetir contenido ya notificado.

Guarda cada item visto por fuente (usando su GUID o link como identificador
unico), de modo que en cada corrida se pueda saber que items son nuevos.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

RUTA_DB = Path(__file__).resolve().parent.parent / "data" / "seen_items.db"


@contextmanager
def _conexion():
    """Provee una conexion a la base de datos y la cierra automaticamente."""
    RUTA_DB.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(RUTA_DB)
    try:
        yield conexion
        conexion.commit()
    finally:
        conexion.close()


def inicializar_db():
    """Crea las tablas necesarias si no existen todavia."""
    with _conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS items_vistos (
                id_item TEXT NOT NULL,
                url_fuente TEXT NOT NULL,
                fecha_visto TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (id_item, url_fuente)
            )
            """
        )


def item_ya_visto(id_item: str, url_fuente: str) -> bool:
    """Indica si un item ya fue notificado anteriormente para esa fuente."""
    with _conexion() as conexion:
        cursor = conexion.execute(
            "SELECT 1 FROM items_vistos WHERE id_item = ? AND url_fuente = ?",
            (id_item, url_fuente),
        )
        return cursor.fetchone() is not None


def marcar_item_visto(id_item: str, url_fuente: str):
    """Registra un item como visto para no volver a notificarlo."""
    with _conexion() as conexion:
        conexion.execute(
            "INSERT OR IGNORE INTO items_vistos (id_item, url_fuente) VALUES (?, ?)",
            (id_item, url_fuente),
        )


def marcar_items_vistos(ids_items: list[str], url_fuente: str):
    """Registra varios items como vistos en una sola transaccion."""
    with _conexion() as conexion:
        conexion.executemany(
            "INSERT OR IGNORE INTO items_vistos (id_item, url_fuente) VALUES (?, ?)",
            [(id_item, url_fuente) for id_item in ids_items],
        )
