import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_BOT_TOKEN = os.getenv("7511109980:AAEj0hHXZXC9Dh9dEI70ElZC3K3g9EW0xfU")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mandatory command handler"""
    await update.message.reply_text("🚀 Bot is working!")

async def main():
    """Simplified startup sequence"""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    print("✅ Bot successfully initialized")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
