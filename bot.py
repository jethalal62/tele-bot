```python
import supabase
from telegram.ext import Updater, CommandHandler

# Initialize supabase
supabase_client = supabase.create_client("supabase_url", "supabase_key")

# Function to handle telegram download
def start(update, context):
    user_id = update.effective_user.id    # Check if user has interacted with bot before    if supabase_client.query("SELECT * FROM movies WHERE id = $1", [user_id]).count == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No file found")
    else:
        file_data = supabase_client.query("SELECT * FROM movies WHERE id = $1", [user_id]).get("data")[0]
        if file_data["telegram_url"]:
            context.bot.send_document(chat_id=update.effective_chat.id, document=file_data["telegram_url"])
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="No file found")

# Initialize telegram bot
updater = Updater("telegram_token", use_context=True)
dispatcher = updater.dispatcher

# Add start handler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# Start the bot
updater.start_polling()
```
