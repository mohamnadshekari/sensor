from flask import Flask, render_template
import paho.mqtt.client as mqtt
import json
import threading
from flask import jsonify
app = Flask(__name__)

# استفاده از یک دیکشنری برای ذخیره داده‌ها (Reference-based)
# این باعث می‌شود در هر جای برنامه که به latest_data دسترسی داشته باشیم، یک شیء واحد را ببینیم
state = {
    "latest_data": {"temperature": 0, "pressure": 0, "timestamp": "N/A", "status": "Connecting..."}
}

@app.route('/api/data')
def get_data():
    # این تابع داده‌های جدید را به صورت JSON برمی‌گرداند
    return jsonify(state["latest_data"])


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected to MQTT Broker with result code: {rc}")
    client.subscribe("factory/rtu_01/sensors")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        state["latest_data"] = payload
        print(f"Data updated: {payload}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")

# تنظیمات کلاینت MQTT با API نسخه ۲
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    try:
        # استفاده از 127.0.0.1 برای اطمینان از اتصال به پورت داکر
        mqtt_client.connect("127.0.0.1", 1883, 60)
        mqtt_client.loop_forever() # در یک ترد جداگانه اجرا می‌شود
    except Exception as e:
        print(f"MQTT Connection Error: {e}")

# اجرای MQTT در یک ترد جداگانه برای اینکه Flask مسدود نشود
mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
mqtt_thread.start()

@app.route('/')
def index():
    # ارسال داده‌های موجود در state به قالب HTML
    return render_template('index.html', data=state["latest_data"])

if __name__ == '__main__':
    # نکته حیاتی: use_reloader=False برای جلوگیری از دو برابر شدن کلاینت MQTT
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
