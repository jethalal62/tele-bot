import os
import asyncio
import sys
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

# Explicit path configuration for Render
BASE_DIR = Path(__file__).parent.resolve()
sys.path.append(str(BASE_DIR))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command"""
    await update.message.reply_text("🚀 Bot successfully deployed on Render!")

async def web_server():
    """Configure web server for Render health checks"""
    app = web.Application()
    port = int(os.environ.get('PORT', 8080))  # Required for Render
    app.add_routes([web.get('/', lambda r: web.Response(text="Render Bot Active"))])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    return runner, site

async def main():
    """Main application setup"""
    try:
        # Initialize Telegram bot
        token = os.environ['TELEGRAM_BOT_TOKEN']
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler("start", start))

        # Start web server
        runner, site = await web_server()

        # Start polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("✅ Successfully connected to Telegram API!")

        # Keep alive
        while True:
            await asyncio.sleep(3600)
            
    except Exception as e:
        print(f"🔥 Critical error: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup resources
        await application.stop()
        await site.stop()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
