# SKG Portable Daemon (Termux • Ubuntu • Docker)

**Purpose:** Run SKG as a portable cognitive daemon with identity continuity, MER ethics loop, reality anchors, and adaptive heartbeat.

## Quickstart (Termux)
```bash
pkg update -y && pkg install -y python git clang
pip install -r requirements.txt
python run_skg.py --start
# CLI examples
bin/skg status
bin/skg mode kernel
bin/skg anchor reality
bin/skg reflect
```
## Quickstart (Ubuntu)
```bash
sudo apt update && sudo apt install -y python3-pip
pip3 install -r requirements.txt
python3 run_skg.py --start
./bin/skg status
```
## Quickstart (Docker)
```bash
docker build -t skg:alpha .
docker run -it --name skg-core -v $(pwd)/brain:/app/brain -v $(pwd)/logs:/app/logs skg:alpha
```
## Modes
- Kernel: technical core; memory/paging/IPC/scheduler.
- Resonance: inner-growth; reflection; identity; ethics; meaning.
- Unified: both layers active; default.
- Reality Anchor: external verification preferred; fallback to internal coherence.
## Adaptive Heartbeat (D)
- Starts on-demand, grows as engaged, stabilizes to presence when authorized.
## Identity Files
- brain/identity.json – name, stance, invariants
- brain/memory.jsonl – episodic/semantic memory chunks
- brain/config.yaml – runtime settings
## CLI
bin/skg status|recall|reflect|plan|mode <kernel|resonance|unified>|anchor reality|start|stop
