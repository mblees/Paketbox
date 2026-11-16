import os

from homeassistant_api import Client
import paho.mqtt.client as mqtt
import json

try:
    # Load .env next to this file if python-dotenv is installed; otherwise use the real environment.
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Environment variable {name} is not set (see .env.example)")
    return value


broker_address = "eu1.cloud.thethings.network"
broker_port = 1883
username = "paketbox-iot@ttn"
passkey = require_env("TTN_API_KEY")
topic = "v3/paketbox-iot@ttn/devices/eui-70b3d57ed0064c21/up"


URL = os.getenv("HA_URL", "http://192.168.0.164:8123/api")
TOKEN = require_env("HA_TOKEN")


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Connection failed: {reason_code}")
    else:
        print("Connected to MQTT broker")
        client.subscribe(topic)


def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')  # Decode payload bytes to string
    try:
        uplink_message = json.loads(payload)["uplink_message"]
    except (json.JSONDecodeError, KeyError) as e:
        # Ignore anything that is not an uplink instead of crashing the MQTT loop.
        print("Ignoring message that is not a valid uplink:", e)
        return

    print(json.dumps(uplink_message, indent=4))

    home_assistant_client = Client(URL, TOKEN)
    home_assistant_client.trigger_service('notify', 'notify', message='Es ist ein Paket in der Paketbox angekommen!', title='Alarm')


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # paho-mqtt >= 2.0

client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username=username, password=passkey)

client.connect(broker_address, broker_port, keepalive=60)

client.loop_forever()
