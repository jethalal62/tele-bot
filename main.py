import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

# Initialize Supabase with validated versions
supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if args:
            movie_id = args[0]
            await send_file(update, movie_id)
        else:
            await update.message.reply_text("🤖 Send /file <movie_id>")
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

async def main():
    try:
        # Initialize bot
        token = os.environ["TELEGRAM_BOT_TOKEN"]
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("file", 
            lambda update, context: send_file(update, context.args[0])
        ))

        # Start polling
        await application.run_polling()
        
    except Exception as e:
        print(f"🔥 Critical failure: {str(e)}")
    finally:
        if 'application' in locals():
            await application.stop()

if __name__ == "__main__":
    asyncio.run(main())
