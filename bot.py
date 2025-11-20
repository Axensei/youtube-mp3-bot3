import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# Token dal sistema
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("You must set the TOKEN environment variable with your BotFather token!")

# Percorso ffmpeg statico
FFMPEG_PATH = "./bin/ffmpeg"
FFPROBE_PATH = "./bin/ffprobe"

# Se vuoi usare cookies esportati da YouTube
COOKIES_FILE = "./cookies.txt"  # Inserisci qui il tuo file cookies

# Comando /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Send me a YouTube link and I will convert it to MP3 for you."
    )

# Funzione principale per gestire messaggi con link YouTube
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "youtube.com" in text or "youtu.be" in text:
        url = text
        await update.message.reply_text("🔗 Link received! Starting download...")

        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "audio.%(ext)s",
                "ffmpeg_location": FFMPEG_PATH,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }],
                "quiet": True,
            }

            # Usa i cookies se presenti
            if os.path.exists(COOKIES_FILE):
                ydl_opts["cookiefile"] = COOKIES_FILE

            await update.message.reply_text("⬇️ Downloading and converting audio, please wait...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "audio")
                file_name = "audio.mp3"

            # Controllo dimensione file per Telegram (max 50MB)
            if os.path.getsize(file_name) > 49 * 1024 * 1024:
                await update.message.reply_text("❌ The file is too big for Telegram (>50MB).")
                os.remove(file_name)
                return

            await update.message.reply_text("🎵 Uploading your MP3 now...")

            await update.message.reply_document(
                open(file_name, "rb"),
                filename=f"{title}.mp3",
                caption=f"✅ Here is your MP3: {title}"
            )
            os.remove(file_name)

        except Exception as e:
            await update.message.reply_text(f"❌ An error occurred: {str(e)}")
            if os.path.exists("audio.mp3"):
                os.remove("audio.mp3")

    else:
        await update.message.reply_text(
            "⚠️ Please send a valid YouTube link and I will convert it to MP3!"
        )

# Crea l'applicazione
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Avvia il bot
if __name__ == "__main__":
    print("🤖 Bot started successfully!")
    app.run_polling()