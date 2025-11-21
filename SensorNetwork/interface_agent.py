#!/usr/bin/env python3
"""Interface agent - displays averages grouped by zone/type."""

import json
import os

import paho.mqtt.client as mqtt
from collections import defaultdict

BROKER, PORT = "localhost", 1883

class InterfaceAgent:
    def __init__(self):
        self.data = defaultdict(dict)  # {zone: {type: value}}
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
    
    def _on_connect(self, client, userdata, flags, rc, props):
        client.subscribe("/average/#")
        print("[INTERFACE] Subscribed to /average/#")
    
    def _on_message(self, client, userdata, msg):
        # Parse topic: /average/{zone}/{type}
        parts = msg.topic.split("/")
        if len(parts) >= 4:
            zone, mtype = parts[2], parts[3]
            try:
                data = json.loads(msg.payload.decode())
                self.data[zone][mtype] = data["average"]
                self._display()
            except (json.JSONDecodeError, KeyError):
                pass
    
    def _display(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print("=" * 50)
        print("       SENSOR NETWORK DASHBOARD")
        print("=" * 50)
        for zone in sorted(self.data.keys()):
            print(f"\n📍 Zone: {zone}")
            print("-" * 30)
            for mtype, value in sorted(self.data[zone].items()):
                print(f"   {mtype}: {value:.2f}")
        print("\n" + "=" * 50)
    
    def run(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_forever()

if __name__ == "__main__":
    InterfaceAgent().run()

