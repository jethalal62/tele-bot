import os
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, CallbackContext
from supabase import create_client

# Initialize Supabase client
url = "YOUR_SUPABASE_URL"  # Replace with your Supabase URL
key = "YOUR_SUPABASE_API_KEY"  # Replace with your Supabase API key
supabase = create_client(url, key)

# Define the command handler for /start
def start(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        rf"Hello {user.mention_html()}! Use /getfile <movie_id> to download your file.",
        reply_markup=ForceReply(selective=True),
    )

# Define the command handler for /getfile
def get_file(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text("Please provide a movie ID. Usage: /getfile <movie_id>")
        return
    
    movie_id = context.args[0]
    
    # Fetch movie details from Supabase
    response = supabase.table('movies').select('*').eq('id', movie_id).execute()
    
    if response.data:
        movie = response.data[0]
        file_url = movie.get('telegram_url')
        
        if file_url:
            update.message.reply_text(f"Here is your file: {file_url}")
        else:
            update.message.reply_text("File not available.")
    else:
        update.message.reply_text("Movie not found.")

def main() -> None:
    # Create the Updater and pass your bot's token
    updater = Updater("YOUR_BOT_TOKEN")  # Replace with your Telegram bot token

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("getfile", get_file))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()
    
