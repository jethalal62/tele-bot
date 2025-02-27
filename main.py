import os
import asyncio
import sys
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web
from supabase import create_client, Client

# Configure base directory
BASE_DIR = Path(__file__).parent.resolve()
sys.path.append(str(BASE_DIR))

# Initialize Supabase client
supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with movie_id parameter"""
    try:
        args = context.args
        if args:
            movie_id = args[0]
            await send_file(update, movie_id)
        else:
            await update.message.reply_text("🎬 Welcome! Use /file <movie_id> or visit our website.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def send_file(update: Update, movie_id: str):
    """Fetch and send file from Supabase"""
    try:
        # Query Supabase database
        result = supabase.table("movies") \
            .select("file_url") \
            .eq("movie_id", movie_id) \
            .execute()

        if not result.data:
            raise ValueError(f"No file found for ID: {movie_id}")

        file_url = result.data[0]["file_url"]
        
        # Send file directly from URL
        await update.message.reply_document(
            document=file_url,
            caption=f"📁 File for ID: {movie_id}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def handle_redirect(request: web.Request):
    """Handle custom domain redirects"""
    movie_id = request.query.get("id", "")
    bot_username = "SHARING_HuB_Bot"  # ⚠️ Replace with your bot's username
    telegram_url = f"https://t.me/{bot_username}?start={movie_id}"
    return web.HTTPFound(telegram_url)

async def web_server():
    """Configure web server for Render"""
    app = web.Application()
    app.add_routes([
        web.get("/", lambda r: web.Response(text="✅ Bot is running")),
        web.get("/file-redirect/", handle_redirect)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()
    return runner, site

async def main():
    """Main application setup"""
    try:
        # Initialize Telegram bot
        token = os.environ["TELEGRAM_BOT_TOKEN"]
        application = Application.builder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("file", 
            lambda update, context: send_file(update, context.args[0] if context.args else "")
        ))

        # Start web server
        runner, site = await web_server()

        # Start polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("🚀 Bot started successfully")

        # Keep alive
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
