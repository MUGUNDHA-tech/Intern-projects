import paho.mqtt.client as mqtt
import mysql.connector
import json
"""from twilio.rest import Client
import ssl
import smtplib
from email.message import EmailMessage"""

locker_length=30
locker_breadth=20
locker_height=50
# --- Twilio Configuration ---
"""TWILIO_SID = 'AC2d69100e2ade052246eb0e42621298b7'
TWILIO_AUTH_TOKEN = '2ed1d10e43a5d397bb5b917cb6453da5'
TWILIO_FROM = '+17175949519'
TWILIO_TO = '+919363119154'


EMAIL_SENDER = "mugub06@gmail.com"
EMAIL_PASSWORD = "ecwysqoeoggmiqkx"
EMAIL_RECEIVER = "vpriyan425@gmail.com" """

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'database': 'p1',  
    'port': 3306
}

# --- MQTT Configuration ---
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "quantanics/sensor"

class MQTTSubscriber:
    def __init__(self):
        self.create_table()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def create_table(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = '''
            CREATE TABLE IF NOT EXISTS proj (
                Distance FLOAT,
                Smoke FLOAT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            '''
            cursor.execute(query)
            conn.commit()
            conn.close()
            print("✅ Database table ready.")
        except mysql.connector.Error as err:
            print(f"❌ Error creating table: {err}")
            exit()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT Broker!")
            client.subscribe(MQTT_TOPIC)
        else:
            print(f"❌ Failed to connect with result code {rc}")
    """def send_email_alert(self, distance, smoke):
        if distance > 20:
            subject = "🚨 ALERT: Locker Breach"
            body = f""""""ALERT from IoT Locker Security System!
            Sensor Values:
            Distance: {distance} cm
            Action Recommended: Please investigate immediately!!!
            """"""
            em = EmailMessage()
            em['From'] = EMAIL_SENDER
            em['To'] = EMAIL_RECEIVER
            em['Subject'] = subject
            em.set_content(body)

            context = ssl.create_default_context()
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                    smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, em.as_string())
                print("📧 Email alert sent!")
            except Exception as e:
                print(f"❌ Failed to send email: {e}")

        elif smoke>400:
            subject = "🚨 ALERT: FIRE DETECTED"
            body = f""""""ALERT from IoT Locker Security System!
            Sensor Values:
            SMOKE: {smoke}
            Action Recommended: Please investigate immediately!!!
            """"""
            em = EmailMessage()
            em['From'] = EMAIL_SENDER
            em['To'] = EMAIL_RECEIVER
            em['Subject'] = subject
            em.set_content(body)

            context = ssl.create_default_context()
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                    smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, em.as_string())
                print("📧 Email alert sent!")
            except Exception as e:
                print(f"❌ Failed to send email: {e}")

    def send_sms_alert(self, distance, smoke):
        try:
            client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
            if(distance>20):
                message = client.messages.create(
                    from_=TWILIO_FROM,
                    to=TWILIO_TO,
                    body=f"ALERT!\nLocker Breach Detected!\nDistance: {distance} cm"
                )
                print("📲 SMS Alert sent! SID:", message.sid)
            elif(smoke>400):
                message = client.messages.create(
                    from_=TWILIO_FROM,
                    to=TWILIO_TO,
                    body=f"ALERT!\FIRE Detected!\n: {smoke} cm"
                )
                print("📲 SMS Alert sent! SID:", message.sid)
        except Exception as e:
            print(f"❌ Failed to send SMS: {e}")"""

    def on_message(self, client, userdata, msg):
        print(f"\n📩 Message received from {msg.topic}")
        try:
            payload = msg.payload.decode()
            data = json.loads(payload)

            distance = data.get('distance')
            smoke = data.get('smoke')

            if distance is not None and smoke is not None:
                self.store_data(distance, smoke)
                print(f"📊 distance: {distance} cm | Smoke: {smoke}")
                #self.send_sms_alert(distance, smoke)
                #self.send_email_alert(distance, smoke)
            else:
                print("❗ Invalid data format or missing keys.")

        except Exception as e:
            print(f"❌ Error processing message: {e}")

    def store_data(self, distance, smoke):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = '''
                INSERT INTO proj (distance, smoke)
                VALUES (%s, %s)
            '''
            values = (distance, smoke)
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            print("✅ Data stored in DB:", values)
        except mysql.connector.Error as err:
            print(f"❌ Error storing data: {err}")

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_forever()


if __name__ == "__main__":
    subscriber = MQTTSubscriber()
    subscriber.start()
