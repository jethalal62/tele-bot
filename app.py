import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            
            if text.startswith("/start"):
                file_id = text.split()[-1]
                
                # Supabase থেকে ডেটা আনুন
                headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
                response = requests.get(f"{SUPABASE_URL}/rest/v1/movies?id=eq.{file_id}", headers=headers)
                
                if response.ok and response.json():
                    file_url = response.json()[0]['streamhg_url']
                    
                    # Telegram এ ফাইল পাঠান
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                        json={"chat_id": chat_id, "document": file_url}
                    )
        
        return '', 200
    
    except Exception as e:
        print(f"ERROR: {str(e)}")  # লগে এরর দেখাবে
        return '', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
