#!/bin/bash
python3 ping_pong.py ping --start &
python3 ping_pong.py pong &
wait

