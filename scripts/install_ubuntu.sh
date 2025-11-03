#!/usr/bin/env bash
sudo apt update && sudo apt install -y python3-pip
pip3 install -r requirements.txt
echo "Run: python3 run_skg.py --start"
