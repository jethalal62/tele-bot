import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Set up logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Load the bot token from environment variables
TOKEN = os.getenv("BOT_TOKEN")

# Initialize the bot application
app = Application.builder().token(TOKEN).build()

# Telegram command: /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I am your Telegram bot.")

# Add command handlers
app.add_handler(CommandHandler("start", start))

# Flask app to keep Render & UptimeRobot happy
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!", 200  # UptimeRobot will now get a 200 OK response

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# Start Flask in a separate thread
threading.Thread(target=run_flask, daemon=True).start()

# Start the bot
if __name__ == "__main__":
    logging.info("Starting bot...")
    app.run_polling()
