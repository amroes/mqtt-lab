# Anomaly Detection

This portion extends the Sensor Network with anomaly handling logic.

## Agents
- `detection_agent.py` listens to every sensor topic, computes z-scores, and publishes anomaly alerts.
- `identification_agent.py` tracks alerts and issues reset commands once a sensor exceeds the alert threshold.
- `faulty_sensor.py` generates outlier readings to test the detection pipeline.

## Running

1. Start a broker and bring up the baseline sensor network (see `SensorNetwork/README.md`).
2. Launch the detection and identification agents:
   ```bash
   python detection_agent.py
   python identification_agent.py
   ```
3. Run one or more instances of `faulty_sensor.py` to trigger alerts and observe reset flows.

