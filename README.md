# Content Aggregator

Bot que revisa fuentes RSS (canales de YouTube, subreddits, blogs) y avisa
por Telegram cuando hay contenido nuevo. Sin IA generativa: solo deteccion
y reenvio con formato limpio.

## Instalacion

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env
```

Completar `.env` con `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`.

## Uso

```bash
python main.py                      # revisa una vez
python main.py --resumen-diario     # revisa una vez, envia resumen agrupado
python main.py --loop --intervalo 6 # corre indefinidamente cada 6 horas
```

## Configurar fuentes

Editar `config/fuentes.json`. Ver `CLAUDE.md` para el detalle de como
agregar YouTube, subreddits o blogs.

## 1. Crear un bot de Telegram con BotFather

1. Abrir Telegram y buscar el usuario `@BotFather`.
2. Enviar el comando `/newbot`.
3. Elegir un nombre para el bot (visible) y un username (debe terminar en
   `bot`, ej: `mi_aggregator_bot`).
4. BotFather responde con un token con este formato:
   `123456789:ABCdefGhIJKlmNoPQRstuVwxyZ`. Ese es el `TELEGRAM_BOT_TOKEN`.
5. Para obtener el `TELEGRAM_CHAT_ID`:
   - Enviar cualquier mensaje al bot recien creado (buscarlo por su username
     y darle "Start").
   - Visitar en el navegador:
     `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Buscar el campo `"chat":{"id": ... }` en la respuesta JSON. Ese numero
     es el `TELEGRAM_CHAT_ID`.
   - Si se va a usar un canal en vez de un chat privado, agregar el bot como
     administrador del canal y el `chat_id` sera negativo (ej: `-100123...`).

## 2. Obtener el channel_id de un canal de YouTube

1. Entrar al canal de YouTube desde el navegador.
2. Abrir el codigo fuente de la pagina (Ctrl+U) y buscar `"channelId"`, o
   usar una herramienta como https://commentpicker.com/youtube-channel-id.html
3. Alternativamente, si la URL del canal ya tiene formato
   `youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxx`, ese `UC...` es el
   `channel_id` directamente.
4. Si la URL es un "handle" (`youtube.com/@nombre`), hay que entrar al canal,
   ir a "Acerca de" > "Compartir canal" > "Copiar ID del canal".
5. Armar la URL del feed:
   `https://www.youtube.com/feeds/videos.xml?channel_id=UC_x5XG1OV2P6uZZ5FSM9Ttw`
6. Agregar esa URL a `config/fuentes.json`.

## 3. Probar que todo funciona

1. Dejar en `config/fuentes.json` al menos una fuente real (por ejemplo un
   subreddit activo como `https://www.reddit.com/r/gaming/.rss`, que no
   requiere configuracion adicional).
2. Completar el `.env` con el token y chat_id reales.
3. Ejecutar:
   ```bash
   python main.py
   ```
4. La primera corrida va a notificar TODOS los items del feed (porque nunca
   se vieron antes). Es normal. A partir de la segunda corrida, solo se
   notificara lo nuevo.
5. Verificar en Telegram que llegaron los mensajes con el formato esperado.
6. Si algo falla, revisar la salida en consola: cada error de feed o de
   envio se imprime sin detener el resto del proceso.
