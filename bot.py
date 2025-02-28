import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

# Environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize bot and Flask app
bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# Build the Application (new API)
application = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                await context.bot.send_document(chat_id=chat_id, document=file_url, caption=title)
            except Exception as e:
                await update.message.reply_text("Error sending file.")
        else:
            await update.message.reply_text("File not found.")
    else:
        await update.message.reply_text("Welcome! Use the website's Telegram download button.")

application.add_handler(CommandHandler("start", start))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    # Process the update using the new Application method
    application.run_update(update)
    return "ok"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
