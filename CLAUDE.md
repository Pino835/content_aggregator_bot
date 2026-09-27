# Content Aggregator

Bot en Python que revisa fuentes RSS (YouTube, subreddits, blogs) y envia
notificaciones a Telegram cuando detecta contenido nuevo. No usa IA
generativa: solo detecta novedades por comparacion contra una base de datos
local de items ya vistos.

## Arquitectura

- `main.py`: punto de entrada y orquestacion (CLI con argparse).
- `modules/rss_reader.py`: lee `config/fuentes.json`, parsea los feeds con
  `feedparser` y filtra los items que ya fueron notificados.
- `modules/db.py`: SQLite (`data/seen_items.db`) con la tabla `items_vistos`
  que guarda `(id_item, url_fuente)` de cada item ya notificado.
- `modules/telegram_notifier.py`: formatea y envia mensajes via
  `python-telegram-bot`. Soporta envio individual y resumen diario agrupado
  por categoria.
- `modules/scheduler.py`: usa la libreria `schedule` para correr la revision
  cada X horas cuando se usa `--loop`.

## Como agregar una nueva fuente RSS

Editar `config/fuentes.json` y agregar un objeto con esta forma:

```json
{
  "nombre": "Nombre visible de la fuente",
  "categoria": "gaming",
  "url": "https://url-del-feed-rss"
}
```

No hace falta tocar codigo. La categoria es libre (se usa tal cual en el
mensaje de Telegram y para agrupar en el resumen diario).

### Como conseguir la URL RSS segun el tipo de fuente

- **YouTube**: `https://www.youtube.com/feeds/videos.xml?channel_id=ID_DEL_CANAL`
  (ver README para como obtener el `channel_id`).
- **Subreddit**: `https://www.reddit.com/r/NOMBRE_SUBREDDIT/.rss`
- **Blog**: buscar el feed propio del sitio, usualmente en `/feed`, `/rss` o
  `/rss.xml`, o el link `<link rel="alternate" type="application/rss+xml">`
  en el HTML de la pagina.

## Comandos

```bash
python main.py                      # ejecuta una revision y termina
python main.py --once               # equivalente al anterior
python main.py --resumen-diario     # agrupa todo en un solo mensaje
python main.py --loop --intervalo 6 # corre en bucle cada 6 horas
```

## Convenciones del proyecto

- Mensajes de terminal y docstrings en espanol.
- Nunca hardcodear tokens: todo credencial va en `.env` (ver `.env.example`).
- Cada feed se procesa con manejo de errores individual: si uno falla, no
  interrumpe la revision de los demas.
- La base de datos y el `.env` no se versionan (ver `.gitignore`).
