import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "movies"
BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_supabase_data(file_id):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?id=eq.{file_id}",
        headers=headers
    )
    return response.json()[0] if response.status_code == 200 else None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        command = data["message"].get("text", "")
        
        if command.startswith("/start"):
            file_id = command.split()[-1]
            file_data = get_supabase_data(file_id)
            
            if file_data:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                    json={
                        "chat_id": chat_id,
                        "document": file_data['streamhg_url']
                    }
                )
    
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("PORT", 5000))
