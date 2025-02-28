import os
import logging
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Load the bot token from the BOT_TOKEN environment variable.
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("No BOT_TOKEN provided! Set it in your Render environment variables.")

# Create the Telegram bot application (using python-telegram-bot v20+)
tg_app = Application.builder().token(TOKEN).build()

# Define a simple /start command for Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I am your Telegram bot.")

# Add the /start handler to the Telegram app
tg_app.add_handler(CommandHandler("start", start))

# Create a Flask app to serve as the WSGI callable for Gunicorn
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!", 200

# Function to run the Telegram bot in a separate thread.
def run_telegram_bot():
    # Create and set a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Run polling without resetting signals (to avoid errors in non-main threads)
    tg_app.run_polling(reset_signals=False)

# Start the Telegram bot in a daemon thread (so it doesn't block the Flask app)
threading.Thread(target=run_telegram_bot, daemon=True).start()

# When running locally, run the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)
