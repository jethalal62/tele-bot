import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "movies"  # Your table name in Supabase

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    # Get Telegram update
    data = request.get_json()
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        command = data["message"].get("text", "")
        
        # Extract file ID from command like /start FILE123
        if command.startswith("/start"):
            file_id = command.split()[-1]
            
            # Fetch data from Supabase
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?id=eq.{file_id}",
                headers=headers
            )
            
            if response.status_code == 200 and response.json():
                file_data = response.json()[0]
                # Send file via Telegram
                requests.post(
                    f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendDocument",
                    json={
                        "chat_id": chat_id,
                        "document": file_data['streamhg_url']
                    }
                )
    
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("PORT", 5000))
