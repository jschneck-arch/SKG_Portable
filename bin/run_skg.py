#!/data/data/com.termux/files/usr/bin/python3
import time, subprocess, os

HOME = os.getenv("HOME")
SKG = f"{HOME}/SKG_Portable/bin/skg"

while True:
    subprocess.run([SKG, "tick"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)  # heartbeat frequency

