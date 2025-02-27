import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TABLE_NAME = "movies"  # Replace with your table name

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if "message" not in data:
            return '', 200
        
        message = data["message"]
        chat_id = message["chat"]["id"]
        command = message.get("text", "")
        
        if not command.startswith("/start"):
            return '', 200
        
        parts = command.split()
        if len(parts) < 2:
            return 'Missing file ID', 400
        
        file_id = parts[1]
        
        # Fetch from Supabase
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        supabase_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?id=eq.{file_id}",
            headers=headers
        )
        
        if supabase_response.status_code != 200:
            return '', 500
        
        result = supabase_response.json()
        if not result:
            return '', 404
        
        file_url = result[0].get("streamhg_url")
        if not file_url:
            return '', 404
        
        # Send to Telegram
        telegram_response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
            json={"chat_id": chat_id, "document": file_url}
        )
        
        return '', 200 if telegram_response.status_code == 200 else 500
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return '', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
