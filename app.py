import os
import requests
import schedule
import time
from flask import Flask
from dotenv import load_dotenv

# تحميل المفاتيح من ملف .env
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

def generate_post():
    """ توليد منشور جديد باستخدام DeepSeek """
    url = "https://api.deepseek.com/generate"
    payload = {"prompt": "اكتب منشورًا رائعًا عن أخلاق النبي محمد ﷺ", "max_length": 300}
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("text", "لم يتم توليد المنشور بنجاح.")
    else:
        return "خطأ في API DeepSeek"

def post_to_facebook(message):
    """ نشر المنشور على صفحة فيسبوك """
    url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed"
    payload = {"message": message, "access_token": FACEBOOK_ACCESS_TOKEN}
    
    response = requests.post(url, data=payload)
    return response.json()

def send_telegram_notification(message):
    """ إرسال إشعار إلى تيليجرام بعد نشر المنشور """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    
    requests.post(url, data=payload)

def daily_post():
    """ توليد منشور يومي ونشره على فيسبوك ثم إرسال إشعار تيليجرام """
    post = generate_post()
    fb_response = post_to_facebook(post)
    
    if "id" in fb_response:
        send_telegram_notification(f"✅ تم نشر منشور جديد على فيسبوك!\n\n{post}")
    else:
        send_telegram_notification(f"❌ فشل نشر المنشور: {fb_response}")

@app.route('/')
def home():
    return "🔹 بوت النشر التلقائي يعمل! 🔹"

@app.route('/run')
def run_manual():
    daily_post()
    return "✅ تم تشغيل النشر اليدوي!"

# جدولة النشر يوميًا الساعة 9 صباحًا
schedule.every().day.at("09:00").do(daily_post)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import threading
    thread = threading.Thread(target=run_scheduler)
    thread.start()
    app.run(host="0.0.0.0", port=5000)