#!/usr/bin/env python3
"""Identification agent - requests faulty sensors to reset."""

import json
import time
from collections import defaultdict

import paho.mqtt.client as mqtt

BROKER, PORT = "localhost", 1883
ALERT_THRESHOLD = 3  # Alerts before requesting reset
RESET_COOLDOWN = 30.0  # Seconds between resets

class IdentificationAgent:
    def __init__(self):
        self.alert_counts = defaultdict(int)
        self.last_reset = defaultdict(float)
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
    
    def _on_connect(self, client, userdata, flags, rc, props):
        client.subscribe("/alerts")
        print("[IDENTIFIER] Listening for anomaly alerts...")
    
    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            sensor_id = data["sensor_id"]
            
            self.alert_counts[sensor_id] += 1
            count = self.alert_counts[sensor_id]
            
            print(f"[IDENTIFIER] Alert #{count} for {sensor_id}")
            
            # Check if reset needed
            if count >= ALERT_THRESHOLD:
                now = time.time()
                if now - self.last_reset[sensor_id] > RESET_COOLDOWN:
                    print(f"[IDENTIFIER] 🔄 Requesting reset for {sensor_id}")
                    self.client.publish(f"/reset/{sensor_id}", json.dumps({"action": "reset"}))
                    self.last_reset[sensor_id] = now
                    self.alert_counts[sensor_id] = 0
        except (json.JSONDecodeError, KeyError):
            pass
    
    def run(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_forever()

if __name__ == "__main__":
    IdentificationAgent().run()

