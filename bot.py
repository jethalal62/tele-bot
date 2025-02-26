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
    # Setup Telegram Bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Setup Web Server
    web_app = web.Application()
    web_app.add_routes([web.get('/', handle_request)])
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 10000)))
    await site.start()

    # Start the bot
    await application.initialize()
    await application.start()

    # Keep the application running
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        # Cleanup
        await application.stop()
        await site.stop()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
