import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Environment variable থেকে Bot Token ও Webhook URL নেওয়া
TOKEN = os.getenv("BOT_TOKEN")  # Render dashboard এ BOT_TOKEN সেট আছে
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Render dashboard এ WEBHOOK_URL সেট আছে; উদাহরণ: "https://your-app.onrender.com/webhook"

if not TOKEN:
    raise RuntimeError("BOT_TOKEN সেট করা নেই!")
if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL সেট করা নেই!")

# Telegram bot এর জন্য Application তৈরি করা
telegram_app = Application.builder().token(TOKEN).build()

# /start কমান্ডের জন্য handler
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I am your bot. Send /file movie123 to get files.")

# (যদি /file কমান্ডও থাকে, তবে নিচের মত করে যোগ করতে পারেন)
async def send_file(update: Update, context: CallbackContext) -> None:
    if context.args:
        movie_id = context.args[0]
        await update.message.reply_text(f"Fetching file for {movie_id}...")
    else:
        await update.message.reply_text("Please provide a Movie ID! Example: /file movie123")

# Handler গুলো যোগ করা
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("file", send_file))

# Flask app তৈরি করা, যা WSGI callable হিসেবে কাজ করবে
app = Flask(__name__)

# Webhook endpoint; Telegram যখন message পাঠাবে, তখন এই রুট এ আসবে
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), telegram_app.bot)
    telegram_app.process_update(update)
    return "OK", 200

# যদি local testing করতে চান, তাহলে home endpoint (health check) ও রাখতে পারেন
@app.route("/")
def home():
    return "Bot is running!", 200

# যদি __main__ এ চালান, তাহলে webhook মোডে রান হবে
if __name__ == "__main__":
    # Render Free version এ port সাধারণত 10000 ব্যবহার করা হয়
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=WEBHOOK_URL
    )
