from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client
import os

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_id = context.args[0] if context.args else None
    if not movie_id:
        await update.message.reply_text("Please use the website link to start")
        return

    # Fetch from Supabase
    data = supabase.table('movies').select('telegram_url, title').eq('id', movie_id).execute()
    if not data.data:
        await update.message.reply_text("Movie not found 🎬")
        return

    movie = data.data[0]
    try:
        await update.message.reply_document(movie['telegram_url'], caption=f"Here's {movie['title']}")
    except Exception as e:
        await update.message.reply_text("Error sending file")

if __name__ == '__main__':
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.run_polling()
