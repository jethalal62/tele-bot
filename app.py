import os
import logging
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from supabase import create_client
from flask import Flask, request

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize clients
supabase = create_client(
    os.environ['SUPABASE_URL'],
    os.environ['SUPABASE_KEY']
)
bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
dispatcher = Dispatcher(bot, None, use_context=True)

def handle_request(update: Update, context: CallbackContext):
    """Process deep links and send files"""
    try:
        # Extract parameters
        args = context.args
        if not args or len(args[0].split('_')) < 2:
            update.message.reply_text("❌ Invalid request format")
            return

        action, movie_id = args[0].split('_', 1)
        
        # Fetch file data
        data = supabase.table('movies') \
            .select('*') \
            .eq('id', movie_id) \
            .execute()
        
        if not data.data:
            update.message.reply_text("⚠️ Content not found")
            return

        file_url = data.data[0].get(f"{action}_url")
        if not file_url:
            update.message.reply_text("⛔ File unavailable")
            return

        # Send file through Telegram
        context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=file_url,
            caption=f"📁 {data.data[0].get('title', 'Your File')}"
        )

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        update.message.reply_text("🚨 Failed to process request")

# Register handlers
dispatcher.add_handler(CommandHandler("start", handle_request))

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook"""
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
