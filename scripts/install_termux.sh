#!/data/data/com.termux/files/usr/bin/bash
pkg update -y && pkg install -y python git clang
pip install -r requirements.txt
echo "Run: python run_skg.py --start"
