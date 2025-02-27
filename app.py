import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from supabase import create_client

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Validate environment variables
REQUIRED_ENV = ['SUPABASE_URL', 'SUPABASE_KEY', 'TELEGRAM_BOT_TOKEN']
for var in REQUIRED_ENV:
    if not os.environ.get(var):
        logger.error(f"Missing required environment variable: {var}")
        exit(1)

try:
    # Initialize clients
    supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])
    bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
    dispatcher = Dispatcher(bot, None, use_context=True)
except Exception as e:
    logger.error(f"Initialization failed: {str(e)}")
    exit(1)

def start(update: Update, context: CallbackContext):
    """Simple start handler for testing"""
    update.message.reply_text("Bot is working! 🚀")

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint"""
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return '', 200
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return '', 500

@app.route('/')
def health_check():
    """Health check endpoint"""
    return "Bot is running", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
