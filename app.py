import os
import requests
import schedule
import time
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# تحميل المتغيرات البيئية
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def generate_post():
    """توليد محتوى باستخدام DeepSeek"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "اكتب منشورًا رائعًا عن أخلاق النبي محمد ﷺ"}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"DeepSeek Error: {str(e)}")
        return None

def post_to_facebook(message):
    """النشر على فيسبوك بدون صور"""
    url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed"
    params = {
        "message": message,
        "access_token": FACEBOOK_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, params=params, timeout=2)
        return response.json()
    except Exception as e:
        print(f"Facebook Error: {str(e)}")
        return None

def send_telegram_notification(message):
    """إرسال إشعار للتليجرام بدون صور"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        requests.post(url, json=payload, timeout=2)
    except Exception as e:
        print(f"Telegram Error: {str(e)}")

@app.route('/')
def home():
    return "🤖 بوت النشر التلقائي - يعمل بنجاح ⏱️"

# جدولة النشر كل 10 دقائق
schedule.every(2).minutes.do(
    lambda: post_to_facebook(generate_post())
)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    import threading
    thread = threading.Thread(target=run_scheduler)
    thread.start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))