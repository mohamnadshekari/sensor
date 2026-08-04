from flask import Flask, render_template
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

# مقداردهی اولیه برای جلوگیری از خطای Undefined
latest_data = {"temperature": 0, "pressure": 0, "timestamp": "N/A", "status": "Waiting..."}

def on_connect(client, userdata, flags, rc, properties=None):
    client.subscribe("factory/rtu_01/sensors")

def on_message(client, userdata, msg):
    global latest_data
    try:
        latest_data = json.loads(msg.payload.decode())
    except Exception as e:
        print(f"Error parsing MQTT data: {e}")

# مقداردهی به صورت صحیح (Callback API v2)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start()

@app.route('/')
def index():
    # اطمینان از ارسال متغیر به تمپلیت
    return render_template('index.html', data=latest_data)

if __name__ == '__main__':
    # برای جلوگیری از تداخل در حالت دیباگ، از use_reloader=False استفاده می‌کنیم
    app.run(debug=True, port=5000, use_reloader=False)
