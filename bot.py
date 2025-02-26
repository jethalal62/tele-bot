import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

TELEGRAM_BOT_TOKEN = os.getenv("7511109980:AAE6WnvBWr7NbWl_vYDpNDlJsrpqrGMOyA0")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with movie ID parameter"""
    try:
        # Get movie ID from deep link
        movie_id = context.args[0] if context.args else None
        response = f"🚀 Download link for movie {movie_id}:\nhttps://yourdomain.com/{movie_id}"
        await update.message.reply_text(response)
    except Exception as e:
        print(f"Error handling /start: {e}")
        await update.message.reply_text("⚠️ Error processing your request")

async def web_handler(request):
    """Basic web server handler for health checks"""
    return web.Response(text="Bot is operational")

async def main():
    """Main async function to start both services"""
    # Initialize Telegram Bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Setup web server for Render health checks
    runner = web.AppRunner(web.Application(router=web.RouteTableDef()))
    runner.app.add_routes([web.get('/', web_handler)])
    
    try:
        # Start web server first
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
        await site.start()

        # Start polling for Telegram updates
        print("🤖 Bot is starting...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        # Keep running
        while True:
            await asyncio.sleep(3600)

    except Exception as e:
        print(f"🔴 Critical error: {e}")
    finally:
        print("🛑 Shutting down...")
        await application.stop()
        await site.stop()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
