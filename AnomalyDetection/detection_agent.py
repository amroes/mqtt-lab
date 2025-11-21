#!/usr/bin/env python3
"""Detection agent - monitors readings and detects anomalies."""

import json
import math
import threading
import time
from collections import defaultdict

import paho.mqtt.client as mqtt

BROKER, PORT = "localhost", 1883
WINDOW = 30.0  # Analysis window in seconds
STD_THRESHOLD = 2.0  # Standard deviations for anomaly

class DetectionAgent:
    def __init__(self):
        self.readings = defaultdict(list)  # {sensor_id: [(ts, value)]}
        self.lock = threading.Lock()
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
    
    def _on_connect(self, client, userdata, flags, rc, props):
        client.subscribe("/+/+/+")  # All sensor readings
        print("[DETECTOR] Monitoring all sensors...")
    
    def _on_message(self, client, userdata, msg):
        parts = msg.topic.split("/")
        if len(parts) < 4:
            return
        
        sensor_id = parts[3]  # /{zone}/{type}/{sensor_id}
        
        try:
            data = json.loads(msg.payload.decode())
            value = data["value"]
            
            with self.lock:
                self.readings[sensor_id].append((time.time(), value))
                self._check_anomaly(sensor_id, value, msg.topic)
        except (json.JSONDecodeError, KeyError):
            pass
    
    def _check_anomaly(self, sensor_id, value, topic):
        now = time.time()
        
        # Gather all readings within window
        all_values = []
        for sid, readings in self.readings.items():
            # Clean old readings
            self.readings[sid] = [(t, v) for t, v in readings if now - t <= WINDOW]
            all_values.extend([v for t, v in self.readings[sid]])
        
        if len(all_values) < 5:
            return  # Not enough data
        
        # Calculate mean and std
        mean = sum(all_values) / len(all_values)
        variance = sum((v - mean) ** 2 for v in all_values) / len(all_values)
        std = math.sqrt(variance) if variance > 0 else 0.001
        
        # Check if current value is anomalous
        z_score = abs(value - mean) / std
        
        if z_score > STD_THRESHOLD:
            alert = {
                "sensor_id": sensor_id,
                "topic": topic,
                "value": value,
                "mean": round(mean, 2),
                "std": round(std, 2),
                "z_score": round(z_score, 2),
                "ts": now
            }
            print(f"[DETECTOR] ⚠️ ANOMALY: {sensor_id} value={value:.2f} (z={z_score:.2f})")
            self.client.publish("/alerts", json.dumps(alert))
    
    def run(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_forever()

if __name__ == "__main__":
    DetectionAgent().run()

