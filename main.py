import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if args:
            await send_file(update, args[0])
        else:
            await update.message.reply_text("🚀 Bot is online! Use /file <movie_id>")
    except Exception as e:
        await update.message.reply_text(f"❌ Startup Error: {str(e)}")

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
        await update.message.reply_text(f"❌ File Error: {str(e)}")

async def main():
    try:
        # ====== CRITICAL INITIALIZATION ======
        print("🔄 Initializing environment variables...")
        token = os.environ["TELEGRAM_BOT_TOKEN"]
        supabase_url = os.environ["SUPABASE_URL"]
        supabase_key = os.environ["SUPABASE_KEY"]
        
        print("🔗 Connecting to Supabase...")
        global supabase
        supabase = create_client(supabase_url, supabase_key)
        
        print("🤖 Starting Telegram bot...")
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("file", 
            lambda update, context: send_file(update, context.args[0])
        ))
        
        print("🚀 Starting polling...")
        await application.run_polling()
        
    except KeyError as e:
        print(f"🔑 Missing environment variable: {str(e)}")
    except Exception as e:
        print(f"🔥 Critical failure: {str(e)}")
    finally:
        if 'application' in locals():
            await application.stop()

if __name__ == "__main__":
    asyncio.run(main())
