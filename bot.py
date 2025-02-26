import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from aiohttp import web

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello!")

async def handle_request(request):
    return web.Response(text="Bot is running")

async def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Add a minimal web server
    app = web.Application()
    app.add_routes([web.get('/', handle_request)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 10000)))  # Use port from environment or 10000
    await site.start()

    asyncio.create_task(application.run_polling())

    # Keep the web server running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
