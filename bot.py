import os
from supabase import create_client, Client
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Initialize Supabase with legacy settings
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY'),
    options={
        'auto_refresh_token': False,
        'persist_session': False
    }
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start command with movie ID"""
    try:
        movie_id = context.args[0] if context.args else None
        if not movie_id:
            await update.message.reply_text("Please use a valid movie link from our website")
            return

        # Fetch movie data
        data = supabase.table('movies') \
                     .select('*') \
                     .eq('id', movie_id) \
                     .execute()

        if not data.data:
            raise ValueError("Movie not found")

        movie = data.data[0]
        
        # Create response message
        response = (
            f"🎬 *{movie['title']}* ({movie['release_year']})\n"
            f"📁 Genre: {movie['genre']}\n\n"
            f"{movie['description']}\n\n"
        )

        # Create buttons
        buttons = []
        if movie.get('telegram_url'):
            buttons.append([InlineKeyboardButton("📥 Telegram Download", url=movie['telegram_url'])])
        if movie.get('cloud_download_url'):
            buttons.append([InlineKeyboardButton("☁️ Cloud Download", url=movie['cloud_download_url'])])
        if movie.get('streamhg_url'):
            buttons.append([InlineKeyboardButton("▶️ Watch Now", url=movie['streamhg_url'])])

        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin file upload handler"""
    if str(update.effective_user.id) != os.getenv('ADMIN_ID'):
        await update.message.reply_text("⛔ Unauthorized")
        return

    # Add your file upload logic here

if __name__ == '__main__':
    app = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("upload", upload))
    
    # Webhook configuration for Render
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv('PORT', 8443)),
        webhook_url=os.getenv('WEBHOOK_URL'),
        secret_token='YOUR_WEBHOOK_SECRET'
    )
