from flask import Flask
import requests
import os
import schedule
import time
from threading import Thread
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

# استيراد مفاتيح API من البيئة
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# إعداد Flask
app = Flask(__name__)

def generate_post():
    """توليد منشور عن رسول الله ﷺ باستخدام DeepSeek"""
    url = "https://api.deepseek.com/v1/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "اكتب منشورًا يوميًا عن رسول الله ﷺ"}],
        "temperature": 0.7
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return None

def post_to_facebook(content):
    """نشر المحتوى على فيسبوك"""
    url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed"
    params = {"message": content, "access_token": FACEBOOK_ACCESS_TOKEN}
    response = requests.post(url, params=params)
    return response.json()

def send_telegram_notification(message):
    """إرسال إشعار إلى تيليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
    response = requests.get(url)
    return response.json()

def daily_post():
    """تشغيل النشر اليومي"""
    content = generate_post()
    if content:
        # إرسال إشعار بالمحتوى الذي تم توليده
        send_telegram_notification(f"📝 **تم توليد المنشور:**\n\n{content}")

        # نشر المحتوى على فيسبوك
        fb_response = post_to_facebook(content)
        
        # إرسال إشعار بالحالة
        if "id" in fb_response:
            send_telegram_notification(f"✅ **تم نشر المنشور على فيسبوك بنجاح!**\n\n📌 **المحتوى:**\n{content}")
        else:
            send_telegram_notification(f"❌ **فشل النشر على فيسبوك:**\n{fb_response}")

# جدولة تشغيل النشر يوميًا
schedule.every().day.at("23:55").do(daily_post)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

# تشغيل الجدولة في Thread مستقل
thread = Thread(target=run_scheduler)
thread.daemon = True
thread.start()

@app.route('/')
def home():
    return "النشر التلقائي شغال ✅"

@app.route('/run')
def manual_run():
    daily_post()
    return "تم تشغيل النشر اليدوي بنجاح ✅"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)