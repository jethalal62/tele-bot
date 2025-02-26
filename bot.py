import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY}")
print(f"TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: CallbackContext) -> None:
    print("Start command received.") # added print statement
    try:
        token = context.args[0]
        print(f"Received token: {token}")

        print("Querying Supabase...") # added print statement
        file_data = supabase.table("files").select("streamhg_url").eq("id", token).execute()
        print("Supabase query complete.") # added print statement

        if file_data.data:
            streamhg_url = file_data.data[0]["streamhg_url"]
            print(f"StreamHG URL: {streamhg_url}")

            print("Downloading file from StreamHG...") # added print statement
            response = requests.get(streamhg_url)

            if response.status_code == 200:
                print("StreamHG download successful.") # added print statement
                file_content = response.content
                await context.bot.send_document(chat_id=update.effective_chat.id, document=file_content, filename="movie.mp4")
            else:
                print(f"StreamHG download failed with status code: {response.status_code}")
                await update.message.reply_text("Failed to download file from StreamHG.")
        else:
            print("Invalid token.")
            await update.message.reply_text("Invalid token.")
    except Exception as e:
        print(f"Error in start command: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")
    print("End of start command.") # added print statement


def main() -> None:
    print("Starting bot...") # added print statement
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()
    print("Bot started.") # added print statement

if __name__ == "__main__":
    main()
