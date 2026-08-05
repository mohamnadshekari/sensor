from flask import Flask, render_template, jsonify
import math
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# --- تنظیمات ایمیل (بعداً اینجا را پر کن) ---
EMAIL_SETTINGS = {
    "sender_email": "mohammadshekari395@gmail.com",
    "sender_password": "fzkcninwvlymaqhh", 
    "receiver_email": "mohammad.shekari1215@gmail.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}

# --- تنظیمات شبیه‌سازی و هشدار ---
DEVICE_CONFIGS = {
    "RTU-01": {"offset": 35.0, "amp": 2.0, "freq": 0.1, "status": "Online", "loc": "Sector A"},
    "RTU-02": {"offset": 32.0, "amp": 1.5, "freq": 0.05, "status": "Online", "loc": "Sector B"},
    "RTU-03": {"offset": 28.0, "amp": 4.0, "freq": 0.15, "status": "Online", "loc": "Sector C"},
}

# برای جلوگیری از ارسال ایمیل‌های پشت سر هم (Spam prevention)
# ذخیره می‌کنیم که برای هر دستگاه، آخرین بار چه زمانی هشدار فرستاده شده است.
last_alert_sent = {dev_id: 0 for dev_id in DEVICE_CONFIGS}

# آستانه دما برای هشدار
TEMP_THRESHOLD_CRITICAL = 30.0

start_time = time.time()

def send_email_alert(device_id, current_temp):
    """تابع ارسال ایمیل واقعی"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SETTINGS["sender_email"]
    msg['To'] = EMAIL_SETTINGS["receiver_email"]
    msg['Subject'] = f"🚨 CRITICAL ALERT: {device_id}"

    body = f"Critical temperature detected on {device_id}!\n\nCurrent Temperature: {current_temp}°C\nLocation: {DEVICE_CONFIGS[device_id]['loc']}\n\nPlease check the dashboard immediately."
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_SETTINGS["smtp_server"], EMAIL_SETTINGS["smtp_port"])
        server.starttls()
        server.login(EMAIL_SETTINGS["sender_email"], EMAIL_SETTINGS["sender_password"])
        server.send_message(msg)
        server.quit()
        print(f"✅ Email alert sent for {device_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/devices')
def get_devices():
    devices_list = {k: {"status": v["status"], "location": v["loc"]} for k, v in DEVICE_CONFIGS.items()}
    return jsonify(devices_list)

@app.route('/api/data/<device_id>')
def get_device_data(device_id):
    if device_id not in DEVICE_CONFIGS:
        return jsonify({"error": "Not found"}), 404
    
    config = DEVICE_CONFIGS[device_id]
    elapsed = time.time() - start_time
    noise = random.uniform(-0.05, 0.05)
    
    temp = round(config["offset"] + (config["amp"] * math.sin(config["freq"] * elapsed)) + noise, 2)
    pressure = round(4.0 + (0.5 * math.sin(config["freq"] * 0.5 * elapsed)) + noise, 2)
    fan_status = "ON" if temp > 26.0 else "OFF"

    # --- منطق بررسی هشدار (Alarm Logic) ---
    current_time = time.time()
    if temp > TEMP_THRESHOLD_CRITICAL:
        # بررسی اینکه آیا بیش از 10 دقیقه از آخرین ایمیل گذشته است؟ (برای جلوگیری از اسپم)
        if current_time - last_alert_sent[device_id] > 600: 
            print(f"⚠️ ALERT! {device_id} is overheating: {temp}°C")
            # در اینجا تابع ایمیل را صدا می‌زنیم
            success = send_email_alert(device_id, temp) 
            # اگر می‌خواهی واقعاً تست کنی، خط بالا را از حالت کامنت خارج کن
            last_alert_sent[device_id] = current_time
    
    return jsonify({
        "device_id": device_id,
        "temperature": temp,
        "pressure": pressure,
        "fan": fan_status,
        "timestamp": current_time,
        "is_critical": temp > TEMP_THRESHOLD_CRITICAL # اضافه کردن این فیلد برای فرانت‌اِند
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
