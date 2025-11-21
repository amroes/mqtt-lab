#!/usr/bin/env python3
"""Averaging agent - computes averages over time window."""

import argparse
import json
import threading
import time

import paho.mqtt.client as mqtt

BROKER, PORT = "localhost", 1883

class AveragingAgent:
    def __init__(self, zone, measure_type, window=10.0, pub_interval=5.0):
        self.zone = zone
        self.measure_type = measure_type
        self.window = window
        self.pub_interval = pub_interval
        
        self.subscribe_topic = f"/{zone}/{measure_type}/+"
        self.publish_topic = f"/average/{zone}/{measure_type}"
        
        self.readings = []  # List of (timestamp, value)
        self.lock = threading.Lock()
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
    
    def _on_connect(self, client, userdata, flags, rc, props):
        print(f"[AVG {self.zone}/{self.measure_type}] Subscribed to {self.subscribe_topic}")
        client.subscribe(self.subscribe_topic)
    
    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            with self.lock:
                self.readings.append((time.time(), data["value"]))
        except (json.JSONDecodeError, KeyError):
            pass
    
    def compute_average(self):
        now = time.time()
        with self.lock:
            # Keep only readings within window
            self.readings = [(t, v) for t, v in self.readings if now - t <= self.window]
            if not self.readings:
                return None
            return sum(v for _, v in self.readings) / len(self.readings)
    
    def run(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()
        
        try:
            while True:
                time.sleep(self.pub_interval)
                avg = self.compute_average()
                if avg is not None:
                    payload = json.dumps({"average": round(avg, 2), "ts": time.time()})
                    self.client.publish(self.publish_topic, payload)
                    print(f"[AVG {self.zone}/{self.measure_type}] Published average: {avg:.2f}")
        except KeyboardInterrupt:
            self.client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zone", required=True)
    parser.add_argument("--type", required=True, dest="measure_type")
    parser.add_argument("--window", type=float, default=10.0)
    parser.add_argument("--interval", type=float, default=5.0)
    args = parser.parse_args()
    
    agent = AveragingAgent(args.zone, args.measure_type, args.window, args.interval)
    agent.run()

