import os
import asyncio
import sys
from pathlib import Path
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

# Configure paths
BASE_DIR = Path(__file__).parent.resolve()
sys.path.append(str(BASE_DIR))
FILES_DIR = BASE_DIR / "files"  # Path to your files directory

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with movie_id from deep links"""
    args = context.args  # Extract movie_id (e.g., ?start=movie123)
    
    if args:
        movie_id = args[0]
        await send_file(update, movie_id)
    else:
        await update.message.reply_text("🔍 Send a Movie ID like /file movie123")

async def send_file(update: Update, movie_id: str):
    """Send file based on movie_id"""
    try:
        # Find the file (supports .txt, .mp4, etc.)
        file_path = next(FILES_DIR.glob(f"{movie_id}.*"))  # Searches for ANY extension
        
        await update.message.reply_document(
            document=InputFile(file_path),
            caption=f"🎥 Here’s your file for ID: {movie_id}"
        )
    except StopIteration:
        await update.message.reply_text("❌ No file found for this ID.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def handle_redirect(request: web.Request):
    """Redirect users from your domain to Telegram bot with movie_id"""
    movie_id = request.query.get("id", "")
    bot_username = "SHARING_HuB_Bot"  # Replace with your bot's username
    telegram_link = f"https://t.me/{bot_username}?start={movie_id}"
    return web.HTTPFound(telegram_link)  # Redirect to Telegram

async def web_server():
    """Web server for redirects and health checks"""
    app = web.Application()
    app.add_routes([
        web.get("/", lambda r: web.Response(text="Bot Active!")),
        web.get("/file-redirect/", handle_redirect)  # Your custom endpoint
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()
    return runner, site

async def main():
    try:
        # Initialize bot
        token = os.environ["TELEGRAM_BOT_TOKEN"]
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("file", lambda u, c: send_file(u, c.args[0])))  # /file movie123

        # Start web server
        runner, site = await web_server()

        # Start polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("✅ Bot is running!")

        # Keep alive
        while True:
            await asyncio.sleep(3600)

    except Exception as e:
        print(f"🔥 Error: {str(e)}")
        sys.exit(1)
    finally:
        await application.stop()
        await site.stop()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
