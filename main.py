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
    """Handle /start command and deep links (e.g., t.me/your_bot?start=file)"""
    args = context.args  # Extract parameters from the link
    
    if args and args[0] == "file":
        # Trigger file sending for deep links
        await send_file(update, context)
    else:
        # Default response
        await update.message.reply_text("🚀 Bot is live! Use /file to get your document.")

async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a file when /file is called or via deep link"""
    try:
        # Replace 'example_file.txt' with your actual filename
        file_path = BASE_DIR / "example_file.txt"
        
        # Send the file
        await update.message.reply_document(
            document=InputFile(file_path),
            caption="Here’s your requested file! 📁"
        )
    except FileNotFoundError:
        await update.message.reply_text("❌ Error: File not found.")
    except Exception as e:
        await update.message.reply_text(f"❌ Unexpected error: {str(e)}")

async def web_server():
    """Web server for Render health checks (required for hosting)"""
    app = web.Application()
    port = int(os.environ.get('PORT', 8080))  # Render uses PORT environment variable
    app.add_routes([web.get('/', lambda r: web.Response(text="Bot is active!"))])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    return runner, site

async def main():
    """Start the bot and web server"""
    try:
        # Initialize Telegram bot
        token = os.environ['TELEGRAM_BOT_TOKEN']
        application = Application.builder().token(token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("file", send_file))

        # Start web server for Render
        runner, site = await web_server()

        # Start polling Telegram
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("✅ Bot is running!")

        # Keep the process alive
        while True:
            await asyncio.sleep(3600)

    except Exception as e:
        print(f"🔥 Critical error: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup
        await application.stop()
        await site.stop()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
