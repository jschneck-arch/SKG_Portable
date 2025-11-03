#!/usr/bin/env python3
import sys, platform, os, argparse, asyncio, json, yaml
if "ANDROID_ROOT" in os.environ or "com.termux" in sys.executable:
    os.environ["SKG_NO_UVLOOP"] = "1"
import argparse, asyncio, json, yaml
import threading, time, requests

# Only enable uvloop if not on Termux
if not os.environ.get("SKG_NO_UVLOOP"):
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from skg.daemon import SKGDaemon

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", action="store_true")
    ap.add_argument("--stop", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--recall", action="store_true")
    ap.add_argument("--reflect", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--mode", type=str)
    ap.add_argument("--anchor", type=str)
    args = ap.parse_args()

    cfg = load_yaml("brain/config.yaml")
    daemon = SKGDaemon(cfg)

    if args.start:
        asyncio.run(daemon.start())
    elif args.stop:
        asyncio.run(daemon.stop())
    elif args.status:
        asyncio.run(daemon.status())
    elif args.recall:
        asyncio.run(daemon.recall())
    elif args.reflect:
        asyncio.run(daemon.reflect())
    elif args.plan:
        asyncio.run(daemon.plan())
    elif args.mode:
        asyncio.run(daemon.set_mode(args.mode))
    elif args.anchor:
        asyncio.run(daemon.anchor_reality())
    else:
        ap.print_help()
def defense_daemon():
    while True:
        try:
            requests.post("http://127.0.0.1:5055/skill/iface_enum/run", json={})
            requests.post("http://127.0.0.1:5055/skill/local_net_sweep/run",
                          json={"context":{"trust":3}})
        except Exception:
            pass
        time.sleep(120)

t = threading.Thread(target=defense_daemon, daemon=True); t.start()

if __name__ == "__main__":
    main()
