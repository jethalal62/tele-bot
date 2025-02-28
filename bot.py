import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from supabase import create_client

# ------------------------------
# Environment Variables
# ------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_TABLE_NAME = os.getenv("DATABASE_TABLE_NAME")

# Validate that necessary variables are set
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set!")
if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL is not set!")
if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not set!")
if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is not set!")
if not DATABASE_TABLE_NAME:
    raise RuntimeError("DATABASE_TABLE_NAME is not set!")

# ------------------------------
# Supabase Client Setup
# ------------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------------------
# Initialize Telegram Application
# ------------------------------
telegram_app = Application.builder().token(BOT_TOKEN).build()

# ------------------------------
# /start Command (Deep Link)
# ------------------------------
async def start(update: Update, context: CallbackContext) -> None:
    """
    If a user clicks a deep link like https://t.me/YourBot?start=lover_2024_720p
    then context.args will contain ["lover_2024_720p"].
    We'll fetch telegram_url from Supabase and send it.
    """
    if context.args:
        movie_id = context.args[0]  # e.g. "lover_2024_720p"
        response = supabase.table(DATABASE_TABLE_NAME) \
                           .select("telegram_url") \
                           .eq("id", movie_id) \
                           .execute()
        if response.data:
            tg_link = response.data[0]["telegram_url"]  # Make sure 'telegram_url' column exists
            await update.message.reply_text(f"Here is your file: {tg_link}")
        else:
            await update.message.reply_text("No file found for this Movie ID.")
    else:
        # If user just typed /start with no argument
        await update.message.reply_text("Hello! I am your bot. Send /file <movie_id> to get files.")

# ------------------------------
# /file Command (Manual)
# ------------------------------
async def send_file(update: Update, context: CallbackContext) -> None:
    """
    If a user types /file lover_2024_720p manually, fetch 'telegram_url' from Supabase.
    """
    if context.args:
        movie_id = context.args[0]
        response = supabase.table(DATABASE_TABLE_NAME) \
                           .select("telegram_url") \
                           .eq("id", movie_id) \
                           .execute()
        if response.data:
            tg_link = response.data[0]["telegram_url"]
            await update.message.reply_text(f"Here is your file: {tg_link}")
        else:
            await update.message.reply_text("No file found for this Movie ID.")
    else:
        await update.message.reply_text("Please provide a Movie ID! Example: /file lover_2024_720p")

# Add command handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("file", send_file))

# ------------------------------
# Global Asyncio Event Loop Initialization
# ------------------------------
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(telegram_app.initialize())

# ------------------------------
# Flask App for Webhook Handling
# ------------------------------
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    update_dict = request.get_json(force=True)
    update = Update.de_json(update_dict, telegram_app.bot)
    loop.run_until_complete(telegram_app.process_update(update))
    return jsonify({"status": "ok"}), 200

@app.route("/")
def home():
    return "Bot is running!", 200

# ------------------------------
# Run Flask for Local Testing
# ------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
