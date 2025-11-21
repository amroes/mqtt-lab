#!/usr/bin/env python3
"""Sensor agent - publishes readings on configured topic."""

import argparse
import json
import math
import time

import paho.mqtt.client as mqtt

BROKER, PORT = "localhost", 1883

class SensorAgent:
    def __init__(self, zone, measure_type, sensor_id, interval=2.0):
        self.topic = f"/{zone}/{measure_type}/{sensor_id}"
        self.interval = interval
        self.sensor_id = sensor_id
        self.start_time = time.time()
        self.running = True
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        # Subscribe to reset commands
        self.reset_topic = f"/reset/{sensor_id}"
    
    def _on_connect(self, client, userdata, flags, rc, props):
        print(f"[SENSOR {self.sensor_id}] Connected, publishing on {self.topic}")
        client.subscribe(self.reset_topic)
    
    def _on_message(self, client, userdata, msg):
        if msg.topic == self.reset_topic:
            print(f"[SENSOR {self.sensor_id}] Received RESET command")
            self.start_time = time.time()  # Reset phase
    
    def generate_reading(self):
        elapsed = time.time() - self.start_time
        # Sinusoidal value: base 20, amplitude 5, period 30s
        return 20 + 5 * math.sin(2 * math.pi * elapsed / 30)
    
    def run(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()
        
        try:
            while self.running:
                value = self.generate_reading()
                payload = json.dumps({"value": round(value, 2), "ts": time.time()})
                self.client.publish(self.topic, payload)
                print(f"[SENSOR {self.sensor_id}] Published: {value:.2f}")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zone", required=True)
    parser.add_argument("--type", required=True, dest="measure_type")
    parser.add_argument("--id", required=True, dest="sensor_id")
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    
    sensor = SensorAgent(args.zone, args.measure_type, args.sensor_id, args.interval)
    sensor.run()

