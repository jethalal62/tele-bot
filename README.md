# Telegram Download Bot

A Telegram bot that delivers exact files stored in Supabase when a user clicks "Download via Telegram" on a website.

## Features
- Uses deep linking (`/start <file_id>`) to send exact files.
- Retrieves files from Supabase database.
- Runs on Flask with a webhook setup.

## Deployment on Render
1. Create a Render Web Service.
2. Set environment variables:
   - `TELEGRAM_TOKEN`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
3. Deploy and set the webhook:
