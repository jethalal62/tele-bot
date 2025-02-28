import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import TimedOut
from supabase import create_client

# ------------------------------
# Environment Variables
# ------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_TABLE_NAME = os.getenv("DATABASE_TABLE_NAME")

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
# /start Command Handler (Deep Link)
# ------------------------------
async def start(update: Update, context: CallbackContext) -> None:
    try:
        print("Received /start command with args:", context.args)
        if context.args:
            movie_id = context.args[0]
            print("Movie ID received:", movie_id)
            # Query Supabase for the movie using the 'id' column
            response = supabase.table(DATABASE_TABLE_NAME) \
                               .select("telegram_url") \
                               .eq("id", movie_id) \
                               .execute()
            print("Supabase response data:", response.data)
            if response.data:
                tg_link = response.data[0]["telegram_url"]
                await update.message.reply_text(f"Here is your file: {tg_link}")
            else:
                await update.message.reply_text("No file found for this Movie ID.")
        else:
            await update.message.reply_text("Hello! I am your bot. Send /file <movie_id> to get files.")
    except TimedOut as e:
        print("TimedOut error in /start:", e)
        await update.message.reply_text("Sorry, the request timed out. Please try again later.")
    except Exception as e:
        print("Error in /start:", e)
        await update.message.reply_text("An error occurred. Please try again later.")

# ------------------------------
# /file Command Handler (Manual)
# ------------------------------
async def send_file(update: Update, context: CallbackContext) -> None:
    try:
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
            await update.message.reply_text("Please provide a Movie ID! Example: /file movie123")
    except TimedOut as e:
        print("TimedOut error in /file:", e)
        await update.message.reply_text("Sorry, the request timed out. Please try again later.")
    except Exception as e:
        print("Error in /file:", e)
        await update.message.reply_text("An error occurred. Please try again later.")

# Add command handlers to the Telegram application
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
    try:
        update_dict = request.get_json(force=True)
        update = Update.de_json(update_dict, telegram_app.bot)
        loop.run_until_complete(telegram_app.process_update(update))
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print("Error processing webhook:", e)
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/")
def home():
    return "Bot is running!", 200

# ------------------------------
# Run Flask for Local Testing
# ------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
