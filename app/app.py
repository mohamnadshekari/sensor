from flask import Flask, render_template, jsonify
import random
import time

app = Flask(__name__)

# --- تنظیمات شبیه‌سازی (Simulation Settings) ---
# این بخش شبیه به دیتابیس شما عمل می‌کند
DEVICES = {
    "RTU-01": {"status": "Online", "location": "Sector A - Main Control"},
    "RTU-02": {"status": "Online", "location": "Sector B - Cooling Unit"},
    "RTU-03": {"status": "Online", "location": "Sector C - Power Grid"},
    "RTU-04": {"status": "Offline", "location": "Sector D - Auxiliary"},
}

@app.route('/')
def index():
    """نمایش صفحه اصلی داشبورد"""
    return render_template('index.html')

@app.route('/api/devices')
def get_devices():
    """
    ارسال لیست تمام دستگاه‌ها به فرانت‌اِند
    این همان مسیری است که در لاگ شما کد 200 داشت و درست کار می‌کرد.
    """
    return jsonify(DEVICES)

@app.route('/api/data/<device_id>')
def get_device_data(device_id):
    """
    دریافت داده‌های لحظه‌ای برای یک دستگاه خاص.
    استفاده از <device_id> باعث می‌شود آدرس داینامیک باشد و خطای 404 رفع شود.
    """
    # 1. بررسی وجود دستگاه در سیستم
    if device_id not in DEVICES:
        return jsonify({"error": "Device not found in system"}), 404
    
    # 2. اگر دستگاه آفلاین بود، داده‌های صفر برگردان
    if DEVICES[device_id]["status"] == "Offline":
        return jsonify({
            "device_id": device_id,
            "temperature": 0.0,
            "pressure": 0.0,
            "fan": "OFF",
            "timestamp": time.time()
        })

    # 3. شبیه‌سازی داده‌های واقعی (در پروژه اصلی اینجا داده از سنسور می‌آید)
    # مقادیر را طوری تنظیم کردیم که تغییرات طبیعی داشته باشند
    data = {
        "device_id": device_id,
        "temperature": round(random.uniform(22.0, 28.5), 2),
        "pressure": round(random.uniform(3.5, 4.8), 2),
        "fan": random.choice(["ON", "OFF"]),
        "timestamp": time.time()
    }
    
    return jsonify(data)

if __name__ == '__main__':
    # اجرای سرور در حالت Debug برای مشاهده خطاهای لحظه‌ای
    print("--- Digital Twin Backend Starting ---")
    print(f"Monitoring {len(DEVICES)} nodes...")
    app.run(debug=True, host='0.0.0.0', port=5000)
