import os
import asyncio
import logging
import signal
from telegram import Update
from telegram.error import Conflict, RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
        logger.error(f"Start error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            raise ValueError("Missing movie_id parameter")
        await send_file(update, context.args[0])
    except Exception as e:
        logger.error(f"File handler error: {e}")
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
        logger.error(f"Send file error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def main():
    application = Application.builder() \
        .token(os.environ["TELEGRAM_BOT_TOKEN"]) \
        .post_init(lambda _: logger.info("Bot initialized")) \
        .post_shutdown(lambda _: logger.info("Bot shutdown")) \
        .build()

    # Register commands
    await application.bot.set_my_commands([
        ("start", "Start the bot"),
        ("file", "Get movie file by ID")
    ])

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("file", file_handler))

    # Signal handling
    loop = asyncio.get_event_loop()
    for s in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(s, lambda: asyncio.create_task(shutdown(application)))

    # Start polling with enhanced conflict handling
    try:
        await application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            stop_signals=None,
            close_loop=False
        )
    except Conflict as e:
        logger.critical(f"Conflict detected: {e}. Ensure only one instance is running.")
    except RetryAfter as e:
        logger.warning(f"Rate limited. Retrying in {e.retry_after} seconds...")
        await asyncio.sleep(e.retry_after)
        await main()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if application.running:
            await application.stop()
            await application.shutdown()

async def shutdown(application: Application):
    logger.info("Initiating graceful shutdown...")
    await application.stop()
    await application.shutdown()
    logger.info("Bot successfully shutdown")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
