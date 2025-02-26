import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler

async def start(update: Update, _):
    await update.message.reply_text("✅ Bot is working!")

async def main():
    token = os.getenv("7511109980:AAEj0hHXZXC9Dh9dEI70ElZC3K3g9EW0xfU")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    await app.initialize()
    await app.start()
    print("Bot activated! Send /start in Telegram")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
