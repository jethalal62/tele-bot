import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from supabase import create_client

# -------------------------------
# 1) Load Environment Variables
# -------------------------------
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

# -------------------------------
# 2) Create Supabase Client
# -------------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# 3) Create Telegram Application
# -------------------------------
telegram_app = Application.builder().token(BOT_TOKEN).build()

# -------------------------------
# 4) Define Command Handlers
# -------------------------------
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I am your bot. Send /file movie123 to get files.")

async def send_file(update: Update, context: CallbackContext):
    if context.args:
        movie_id = context.args[0]
        response = supabase.table(DATABASE_TABLE_NAME).select("file_link").eq("movie_id", movie_id).execute()
        if response.data:
            file_link = response.data[0]["file_link"]
            await update.message.reply_text(f"Here is your file: {file_link}")
        else:
            await update.message.reply_text("No file found for this Movie ID.")
    else:
        await update.message.reply_text("Please provide a Movie ID! Example: /file movie123")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("file", send_file))

# -------------------------------
# 5) Global Asyncio Event Loop
# -------------------------------
# We create ONE event loop for everything:
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Initialize the bot ONCE in this global loop:
loop.run_until_complete(telegram_app.initialize())

# -------------------------------
# 6) Create Flask App
# -------------------------------
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Parse incoming update
    update_dict = request.get_json(force=True)
    update = Update.de_json(update_dict, telegram_app.bot)

    # Process update in the same global loop
    loop.run_until_complete(telegram_app.process_update(update))

    return jsonify({"status": "ok"}), 200

@app.route("/")
def home():
    return "Bot is running!", 200

# -------------------------------
# 7) Run Flask if Called Directly
# -------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
