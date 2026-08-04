import paho.mqtt.client as mqtt
import time
import random
import json

# تنظیمات MQTT
MQTT_BROKER = "localhost"  # در مرحله بعد این را به Mosquitto تغییر می‌دهیم
MQTT_TOPIC = "factory/rtu_01/sensors"

def simulate_industrial_data():
    """تولید داده‌های تصادفی شبیه به دنیای واقعی"""
    # شبیه‌سازی دما (بین 20 تا 30 درجه)
    temperature = round(random.uniform(20.0, 30.0), 2)
    # شبیه‌سازی فشار (بین 90 تا 110 بار)
    pressure = round(random.uniform(90.0, 110.0), 2)
    
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": temperature,
        "pressure": pressure,
        "status": "OK" if temperature < 28 else "WARNING"
    }

def run_rtu():
    # ایجاد کلاینت MQTT
    client = mqtt.Client()

    print(f"--- Starting Virtual RTU ---")
    try:
        # اتصال به Broker (فعلاً فرض می‌کنیم روی سیستم خودت است)
        # نکته: اگر Broker نصب نیست، اینجا خطا می‌گیری که طبیعی است
        client.connect(MQTT_BROKER, 1883, 60)
        print(f"Connected to Broker: {MQTT_BROKER}")
    except Exception as e:
        print(f"Error: Could not connect to MQTT Broker. {e}")
        print("Tip: Make sure Mosquitto is running or we will setup Docker next.")
        return

    client.loop_start()

    try:
        while True:
            # ۱. تولید داده
            data = simulate_industrial_data()
            
            # ۲. تبدیل به فرمت JSON برای ارسال
            payload = json.dumps(data)
            
            # ۳. ارسال داده به Topic مشخص شده
            client.publish(MQTT_TOPIC, payload)
            
            print(f"[SENT] {payload}")
            
            # ۴. وقفه بین ارسال‌ها (هر ۲ ثانیه یکبار)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nStopping RTU...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    run_rtu()
