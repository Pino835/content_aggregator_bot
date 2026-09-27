"""
Punto de entrada del Content Aggregator.

Revisa las fuentes RSS configuradas, detecta contenido nuevo y lo envia
a Telegram, ya sea de forma inmediata o como resumen diario.
"""

import argparse

from dotenv import load_dotenv

load_dotenv()

from modules import db, rss_reader, telegram_notifier, scheduler


def ejecutar_revision(resumen_diario: bool = False):
    """Revisa todas las fuentes configuradas y notifica el contenido nuevo."""
    print("Iniciando revision de fuentes...")

    fuentes = rss_reader.cargar_fuentes()
    todos_los_items_nuevos = []

    for fuente in fuentes:
        print(f"Revisando fuente: {fuente['nombre']} ({fuente['categoria']})")
        items_nuevos = rss_reader.obtener_items_nuevos(fuente)

        if items_nuevos:
            print(f"  -> {len(items_nuevos)} item(s) nuevo(s) encontrado(s)")
            todos_los_items_nuevos.extend(items_nuevos)
        else:
            print("  -> sin novedades")

    if not todos_los_items_nuevos:
        print("No se encontro contenido nuevo en ninguna fuente.")
        return

    if resumen_diario:
        telegram_notifier.enviar_resumen_diario(todos_los_items_nuevos)
    else:
        telegram_notifier.enviar_items_nuevos(todos_los_items_nuevos)

    for item in todos_los_items_nuevos:
        db.marcar_item_visto(item["id_item"], item["url_fuente"])

    print(f"Revision finalizada. {len(todos_los_items_nuevos)} item(s) notificado(s).")


def main():
    """Interpreta los argumentos de linea de comandos y ejecuta el modo elegido."""
    parser = argparse.ArgumentParser(description="Content Aggregator: bot de notificaciones RSS a Telegram")
    parser.add_argument("--once", action="store_true", help="Ejecuta una sola revision y termina")
    parser.add_argument("--loop", action="store_true", help="Ejecuta en bucle cada X horas (ver --intervalo)")
    parser.add_argument("--intervalo", type=float, default=6, help="Horas entre cada revision en modo --loop (default: 6)")
    parser.add_argument("--resumen-diario", action="store_true", help="Agrupa los items nuevos en un solo mensaje resumen")

    args = parser.parse_args()

    db.inicializar_db()

    def tarea():
        ejecutar_revision(resumen_diario=args.resumen_diario)

    if args.loop:
        scheduler.iniciar_scheduler(tarea, args.intervalo)
    else:
        # Por defecto (o con --once) se ejecuta una sola vez.
        tarea()


if __name__ == "__main__":
    main()
