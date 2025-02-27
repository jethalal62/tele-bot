import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

# Initialize Supabase
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
            await update.message.reply_text("🤖 Send a Movie ID like /file movie123")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def send_file(update: Update, movie_id: str):
    """Fetch and send file from Supabase"""
    try:
        # Query database
        result = supabase.table("movies") \
                  .select("file_url") \
                  .eq("movie_id", movie_id) \
                  .execute()

        if not result.data:
            raise ValueError(f"No file found for ID: {movie_id}")

        file_url = result.data[0]["file_url"]
        
        # Send file
        await update.message.reply_document(
            document=file_url,
            caption=f"📁 File for ID: {movie_id}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def main():
    """Start the bot"""
    try:
        token = os.environ["TELEGRAM_BOT_TOKEN"]
        application = Application.builder().token(token).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("file", 
            lambda update, context: send_file(update, context.args[0] if context.args else "")
        ))

        # Start polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("🚀 Bot is running!")

        # Keep alive
        while True:
            await asyncio.sleep(3600)

    except Exception as e:
        print(f"🔥 Critical error: {str(e)}")
    finally:
        await application.stop()

if __name__ == "__main__":
    asyncio.run(main())
