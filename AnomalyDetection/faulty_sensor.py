#!/usr/bin/env python3
"""Faulty sensor - sends erroneous readings for testing detection."""

import argparse
import json
import random
import time

import paho.mqtt.client as mqtt

BROKER, PORT = "localhost", 1883

class FaultySensor:
    def __init__(self, zone, measure_type, sensor_id, fault_magnitude=50):
        self.topic = f"/{zone}/{measure_type}/{sensor_id}"
        self.sensor_id = sensor_id
        self.fault_magnitude = fault_magnitude
        self.reset_topic = f"/reset/{sensor_id}"
        self.faulty = True
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
    
    def _on_connect(self, client, userdata, flags, rc, props):
        client.subscribe(self.reset_topic)
        print(f"[FAULTY {self.sensor_id}] Started (will send bad readings)")
    
    def _on_message(self, client, userdata, msg):
        if msg.topic == self.reset_topic:
            print(f"[FAULTY {self.sensor_id}] Reset received - becoming normal")
            self.faulty = False
    
    def generate_reading(self):
        if self.faulty:
            return 20 + self.fault_magnitude + random.uniform(-5, 5)  # Way off!
        return 20 + random.uniform(-2, 2)  # Normal reading
    
    def run(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()
        
        try:
            while True:
                value = self.generate_reading()
                payload = json.dumps({"value": round(value, 2), "ts": time.time()})
                self.client.publish(self.topic, payload)
                status = "FAULTY" if self.faulty else "normal"
                print(f"[FAULTY {self.sensor_id}] ({status}) Published: {value:.2f}")
                time.sleep(2)
        except KeyboardInterrupt:
            self.client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zone", default="living_room")
    parser.add_argument("--type", default="temperature", dest="measure_type")
    parser.add_argument("--id", default="faulty_1", dest="sensor_id")
    args = parser.parse_args()
    
    FaultySensor(args.zone, args.measure_type, args.sensor_id).run()

