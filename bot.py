import os
from supabase import create_client, Client
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Initialize Supabase
supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with deep linking"""
    movie_id = context.args[0] if context.args else None
    
    if not movie_id:
        await update.message.reply_text("ℹ️ Please use a valid movie link from our website")
        return

    try:
        # Fetch movie data from Supabase
        data = supabase.table('movies') \
                     .select('*') \
                     .eq('id', movie_id) \
                     .execute()
        
        if not data.data:
            raise ValueError("Movie not found")

        movie = data.data[0]
        response = f"🎬 *{movie['title']}* ({movie['release_year']})\n"
        response += f"📁 Genre: {movie['genre']}\n\n"
        response += f"{movie['description']}\n\n"

        # Create buttons
        keyboard = []
        if movie['telegram_url']:
            keyboard.append([InlineKeyboardButton("📥 Telegram Download", url=movie['telegram_url'])])
        if movie['cloud_download_url']:
            keyboard.append([InlineKeyboardButton("☁️ Cloud Download", url=movie['cloud_download_url'])])
        if movie['streamhg_url']:
            keyboard.append([InlineKeyboardButton("▶️ Watch Now", url=movie['streamhg_url'])])

        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to add new movies"""
    if str(update.effective_user.id) != os.getenv('ADMIN_ID'):
        await update.message.reply_text("⛔ Unauthorized")
        return

    # Implementation for file upload handling
    # (Add your specific upload logic here)

if __name__ == '__main__':
    app = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("upload", upload))
    
    # Webhook setup
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv('PORT', 8443)),
        webhook_url=os.getenv('WEBHOOK_URL')
    )
