from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os
from supabase import create_client

# ✅ Environment Variables
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_TABLE_NAME = os.getenv("DATABASE_TABLE_NAME")

# ✅ Supabase Client Setup
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Flask App
app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

# ✅ Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I am your bot. Send /file movie123 to get files.")

# ✅ File Command (Fetch from Supabase)
async def send_file(update: Update, context: CallbackContext):
    if context.args:
        movie_id = context.args[0]
        
        # 🔍 Fetch file link from Supabase
        response = supabase.table(DATABASE_TABLE_NAME).select("file_link").eq("movie_id", movie_id).execute()
        
        if response.data:
            file_link = response.data[0]["file_link"]
            await update.message.reply_text(f"Here is your file: {file_link}")
        else:
            await update.message.reply_text("No file found for this Movie ID.")
    else:
        await update.message.reply_text("Please provide a Movie ID! Example: /file movie123")

# ✅ Handlers Add
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("file", send_file))

# ✅ Webhook Function
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), telegram_app.bot)
    telegram_app.process_update(update)
    return "OK", 200

# ✅ Run Webhook on Render
if __name__ == "__main__":
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=10000,  # Render Free Version 10000 Port ব্যবহার করে
        webhook_url=WEBHOOK_URL
    )
