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
    try:
        if context.args:
            return await send_file(update, context.args[0])
        await update.message.reply_text("🤖 Send /file <movie_id>")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            raise ValueError("Missing movie_id parameter")
        await send_file(update, context.args[0])
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def send_file(update: Update, movie_id: str):
    try:
        result = supabase.table("movies") \
                  .select("file_url") \
                  .eq("movie_id", movie_id) \
                  .execute()

        if not result.data:
            raise ValueError(f"No file for ID: {movie_id}")

        await update.message.reply_document(
            document=result.data[0]["file_url"],
            caption=f"🎥 File: {movie_id}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    # Create application instance
    application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("file", file_handler))

    # Run application with explicit event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(application.run_polling())
    finally:
        loop.close()

if __name__ == "__main__":
    main()
