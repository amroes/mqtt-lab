# Part I: MQTT Basics

This directory contains the exercises covering MQTT fundamentals.

## Scripts
- `first_client.py`: connects to a local broker, subscribes to `hello`, and publishes several messages with delays. Prints outgoing and incoming payloads for manual verification.
- `ping_pong.py`: single script that can act as either `ping` or `pong` via a command-line argument. Both instances share one topic and respond to each other, demonstrating two clients interacting on the same broker.
- `start_ping_pong.sh`: launches the `ping` and `pong` clients together and keeps the session alive.

## Running

1. Install dependencies (see root `README.md`) and ensure the broker runs on `localhost:1883`.
2. Run `python first_client.py` to validate your connection and publish/subscribe behavior.
3. Use `./start_ping_pong.sh` (or run `python ping_pong.py ping --start` and `python ping_pong.py pong`) to execute the ping-pong exercise.

