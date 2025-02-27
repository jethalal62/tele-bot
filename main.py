import os
import asyncio
import sys
from pathlib import Path
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

# Configure absolute paths for Render
BASE_DIR = Path(__file__).parent.resolve()
sys.path.append(str(BASE_DIR))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command and process movie_id from custom domain links"""
    args = context.args  # Extract parameters like "movie123"
    
    if args:
        movie_id = args[0]
        await send_file(update, context, movie_id)
    else:
        await update.message.reply_text("🚀 Welcome! Use /file <movie_id> to get a file.")

async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE, movie_id: str):
    """Send a file based on movie_id"""
    try:
        # Map movie_id to a file (customize this logic)
        file_path = BASE_DIR / "files" / f"{movie_id}.txt"
        
        # Send the file
        await update.message.reply_document(
            document=InputFile(file_path),
            caption=f"Here’s your file for Movie ID: {movie_id}! 🎬"
        )
    except FileNotFoundError:
        await update.message.reply_text("❌ Error: File not found for this ID.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def handle_redirect(request: web.Request):
    """Redirect users from https://mydomain.io/file-redirect/?id=movie_id to Telegram"""
    movie_id = request.query.get("id", "")
    bot_username = "YOUR_BOT_USERNAME"  # Replace with your bot's username
    telegram_deep_link = f"https://t.me/{bot_username}?start={movie_id}"
    
    # Redirect to Telegram
    return web.HTTPFound(telegram_deep_link)

async def web_server():
    """Web server with redirect logic for your custom domain"""
    app = web.Application()
    port = int(os.environ.get('PORT', 8080))
    
    # Add routes
    app.add_routes([
        web.get('/', lambda r: web.Response(text="Bot is active!")),
        web.get('/file-redirect/', handle_redirect)  # Your custom endpoint
    ])
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    return runner, site

async def main():
    try:
        # Initialize Telegram bot
        token = os.environ['TELEGRAM_BOT_TOKEN']
        application = Application.builder().token(token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("file", send_file))

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
