# Telegram File Bot
A bot to deliver files from Supabase via Telegram

## Deployment
1. Set environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `BOT_TOKEN`
2. Set webhook:
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<RENDER_URL>/webhook"
