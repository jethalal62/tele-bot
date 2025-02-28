import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from supabase import create_client, Client

from config import TELEGRAM_TOKEN, SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Telegram Bot
bot = Bot(token=TELEGRAM_TOKEN)

# Set up Flask app
app = Flask(__name__)

# Create a dispatcher to register handlers
dispatcher = Dispatcher(bot, None, workers=0)

def start(update: Update, context: CallbackContext):
    """
    /start command handler. Fetches file using deep-linking.
    """
    args = context.args
    if args:
        file_id = args[0]
        response = supabase.table("movies").select("*").eq("id", file_id).execute()
        data = response.data

        if data and len(data) > 0:
            file_info = data[0]
            file_url = file_info.get("telegram_url")
            title = file_info.get("title", "File")
            chat_id = update.effective_chat.id

            try:
                bot.send_document(chat_id=chat_id, document=file_url, caption=title)
            except Exception as e:
                update.message.reply_text("Error sending file.")
        else:
            update.message.reply_text("File not found.")
    else:
        update.message.reply_text("Welcome! Use the website's Telegram download button.")

# Register handler
dispatcher.add_handler(CommandHandler("start", start))

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handles Telegram updates."""
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
