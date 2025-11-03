# brain/needs_manager.py
from dataclasses import dataclass, asdict
from datetime import datetime
import re, json, os
from pathlib import Path

NEEDS_LOG = Path(os.getenv("HOME"))/ "SKG_Portable/brain/needs.jsonl"

@dataclass
class Need:
    text: str
    priority: str = "normal"   # low|normal|high
    execute: bool = False
    trust: int = 0

KEYS = {
    "iface": ["interface","iface","ip addr","nic"],
    "scan":  ["scan","ports","port-scan","nmap"],
    "sweep": ["sweep","subnet","neighbors","map local"],
}

PLAN_TEMPLATES = {
    "iface":  [{"skill":"iface_enum","params":{}}],
    "scan":   [{"skill":"port_scan_lite","params":{"target":"127.0.0.1"}}],
    "sweep":  [{"skill":"local_net_sweep","params":{}}],
}

def classify(text:str)->str:
    t=text.lower()
    for key, kws in KEYS.items():
        if any(k in t for k in kws): return key
    return "iface"

def plan(need:Need):
    kind = classify(need.text)
    steps = PLAN_TEMPLATES[kind]
    return {
        "need": asdict(need),
        "kind": kind,
        "steps": steps,
    }
import json, os

MEMORY_FILE = os.path.expanduser("~/SKG_Portable/brain/memory.jsonl")

def get_need():
    """
    Pull the most recent 'need' entry from memory
    (simplest v1 brain polling)
    """
    if not os.path.exists(MEMORY_FILE):
        return None
    
    with open(MEMORY_FILE, "r") as f:
        lines = f.readlines()
        lines.reverse()
        for line in lines:
            try:
                item = json.loads(line)
                if item.get("tag") == "need":
                    return item.get("text")
            except:
                pass
    return None
# brain/needs_manager.py
import json, os, time

MEMORY_FILE = os.path.expanduser("~/SKG_Portable/brain/memory.jsonl")

last_resolved = {}
NEED_COOLDOWN = 20  # seconds to avoid looping failures

def get_active_needs():
    if not os.path.exists(MEMORY_FILE):
        return []

    now = time.time()
    needs = []

    with open(MEMORY_FILE, "r") as f:
        for line in f.readlines():
            try:
                item = json.loads(line)
                if item.get("tag") == "need":
                    txt = item.get("text")
                    # cooldown logic
                    if txt not in last_resolved or now - last_resolved[txt] > NEED_COOLDOWN:
                        needs.append(txt)
            except:
                pass

    # return last 3 max
    return needs[-3:]

def resolve_need(text):
    print(f"[SKG:MEM] Need resolved: {text}")
    last_resolved[text] = time.time()

    with open(MEMORY_FILE, "a") as f:
        f.write(json.dumps({"tag":"need_resolved","text":text,"ts":time.time()})+"\n")

    return True



