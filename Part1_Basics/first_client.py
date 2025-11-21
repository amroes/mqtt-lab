#!/usr/bin/env python3
"""First MQTT client - connects, subscribes, publishes messages."""

import paho.mqtt.client as mqtt
import time

BROKER = "localhost"
PORT = 1883
TOPIC = "hello"

def on_connect(client, userdata, flags, rc, properties):
    print(f"[CONNECTED] Result code: {rc}")
    client.subscribe(TOPIC)
    print(f"[SUBSCRIBED] Topic: {TOPIC}")

def on_message(client, userdata, msg):
    print(f"[RECEIVED] {msg.topic}: {msg.payload.decode()}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    
    # Publish messages with delays
    for i in range(5):
        message = f"Hello MQTT #{i+1}"
        client.publish(TOPIC, message)
        print(f"[PUBLISHED] {TOPIC}: {message}")
        time.sleep(2)
    
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()

