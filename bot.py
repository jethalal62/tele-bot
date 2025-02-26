import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print(f"SUPABASE_URL: {SUPABASE_URL}") #added print statement
print(f"SUPABASE_KEY: {SUPABASE_KEY}") #added print statement
print(f"TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}") #added print statement

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: CallbackContext) -> None:
    try:
        token = context.args[0]
        print(f"Received token: {token}") #added print statement
        file_data = supabase.table("files").select("streamhg_url").eq("id", token).execute()

        if file_data.data:
            streamhg_url = file_data.data[0]["streamhg_url"]
            print(f"StreamHG URL: {streamhg_url}") #added print statement
            response = requests.get(streamhg_url)

            if response.status_code == 200:
                file_content = response.content
                await context.bot.send_document(chat_id=update.effective_chat.id, document=file_content, filename="movie.mp4")
            else:
                print(f"StreamHG download failed with status code: {response.status_code}") #added print statement
                await update.message.reply_text("Failed to download file from StreamHG.")
        else:
            print("Invalid token.") #added print statement
            await update.message.reply_text("Invalid token.")
    except Exception as e:
        print(f"Error in start command: {e}") #added print statement
        await update.message.reply_text("An error occurred. Please try again later.")

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    main()
