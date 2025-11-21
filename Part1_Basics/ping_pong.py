#!/usr/bin/env python3
"""Ping-Pong MQTT client - configurable via command line."""

import paho.mqtt.client as mqtt
import argparse
import time

BROKER, PORT, TOPIC = "localhost", 1883, "pingpong"

def create_client(mode):
    respond_to = "pong" if mode == "ping" else "ping"
    send_msg = "ping" if mode == "ping" else "pong"
    
    def on_connect(client, userdata, flags, rc, props):
        print(f"[{mode.upper()}] Connected")
        client.subscribe(TOPIC)
    
    def on_message(client, userdata, msg):
        received = msg.payload.decode()
        if received == respond_to:
            print(f"[{mode.upper()}] Received '{received}', sending '{send_msg}'")
            time.sleep(0.5)
            client.publish(TOPIC, send_msg)
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    return client, send_msg

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["ping", "pong"])
    parser.add_argument("--start", action="store_true")
    args = parser.parse_args()
    
    client, send_msg = create_client(args.mode)
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    
    if args.start:  # Initiator sends first message
        time.sleep(1)
        client.publish(TOPIC, send_msg)
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        client.disconnect()

if __name__ == "__main__":
    main()

