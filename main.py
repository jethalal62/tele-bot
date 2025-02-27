import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot is now running on Render!")

async def web_server():
    app = web.Application()
    port = int(os.environ.get('PORT', 8080))  # Render requires dynamic port
    app.add_routes([web.get('/', lambda r: web.Response(text="Render Bot Active"))])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    return runner, site

async def main():
    token = os.environ['TELEGRAM_BOT_TOKEN']
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))

    runner, site = await web_server()

    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("✅ Successfully deployed on Render!")
        while True:
            await asyncio.sleep(3600)
    finally:
        await application.stop()
        await site.stop()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
