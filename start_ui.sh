#!/data/data/com.termux/files/usr/bin/bash
pkill -f run_skg.py
pkill -f flask
nohup python ~/SKG_Portable/api.py > ~/SKG_Portable/logs/ui.log 2>&1 &
nohup ~/SKG_Portable/bin/run_skg.py > ~/SKG_Portable/logs/daemon.log 2>&1 &
sleep 2
termux-open-url http://127.0.0.1:5055/ui

