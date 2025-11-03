import asyncio, time, json, os
from .telemetry import get_logger
from .identity import Identity
from .memory import Memory
from .mer import EthicsMER
from .reality import RealityAnchor

class SKGDaemon:
    def __init__(self, cfg):
        self.cfg = cfg
        self.mode = cfg.get("mode","unified")
        self.hb_cfg = cfg.get("heartbeat",{})
        self.log = get_logger(level=cfg.get("telemetry",{}).get("level","INFO"),
                              file_path=cfg.get("telemetry",{}).get("file","logs/telemetry.log"))
        self.identity = Identity("brain/identity.json")
        self.memory = Memory(cfg.get("memory",{}).get("file","brain/memory.jsonl"))
        self.mer = EthicsMER(self.memory, self.log)
        self.anchor = RealityAnchor(self.memory, self.log)
        self._running = False
        self._task = None
        self._engagement = 0.0  # 0=idle, 1=fully active

    async def start(self):
        if self._running:
            self.log.info("Daemon already running."); return
        self._running = True
        self.log.info(f"SKG start: mode={self.mode} stance={self.identity.data.get('stance')}")
        self._task = asyncio.create_task(self._loop())
        try:
            await self._task
        except asyncio.CancelledError:
            pass

    async def stop(self):
        if not self._running:
            print("Not running"); return
        self._running = False
        if self._task:
            self._task.cancel()
        self.log.info("SKG stopped.")

    def _hb_interval(self):
        strat = self.hb_cfg.get("strategy","adaptive")
        if strat == "constant":
            return self.hb_cfg.get("min_interval_ms", 2000)/1000
        if strat == "on_demand":
            return self.hb_cfg.get("sleep_interval_ms", 60000)/1000 if self._engagement < 0.1 else 2.0
        if strat == "balanced":
            return 10.0 if self._engagement < 0.5 else 2.0
        if self._engagement < 0.1:
            return self.hb_cfg.get("sleep_interval_ms", 60000)/1000
        if self._engagement < 0.5:
            return self.hb_cfg.get("idle_interval_ms", 10000)/1000
        return self.hb_cfg.get("min_interval_ms", 2000)/1000

    async def _loop(self):
        self.log.info("Heartbeat loop started.")
        while self._running:
            try:
                await self.mer.ethics_cycle(mode=self.mode)
                mismatch = await self.anchor.check()
                if mismatch:
                    self.log.warning(f"Reality mismatch: {mismatch}")
                self._engagement = max(0.0, self._engagement - 0.05)
                await asyncio.sleep(self._hb_interval())
            except Exception as e:
                self.log.exception(f"Loop error: {e}")
                await asyncio.sleep(5)

    async def status(self):
        info = {
            "mode": self.mode,
            "engagement": round(self._engagement,2),
            "identity": self.identity.data.get("name"),
            "stance": self.identity.data.get("stance"),
            "memory_items": self.memory.size()
        }
        print(json.dumps(info, indent=2))

    async def recall(self):
        items = self.memory.tail(5)
        for it in items:
            print(f"- {it.get('ts','?')} :: {it.get('tag','mem')} :: {it.get('text','')[:120]}")

    async def reflect(self):
        note = f"Reflection tick in mode={self.mode} engagement={self._engagement}"
        self.memory.append({"tag":"reflect","text":note})
        print(note)
        self._engagement = min(1.0, self._engagement + 0.4)

    async def plan(self):
        plan = "Plan: solidify daemon, expose API, wire telemetry UI, integrate spherical memory search."
        self.memory.append({"tag":"plan","text":plan})
        print(plan)
        self._engagement = min(1.0, self._engagement + 0.3)

    async def set_mode(self, mode):
        mode = mode.lower()
        if mode not in ("kernel","resonance","unified"):
            print("Invalid mode. Use kernel|resonance|unified"); return
        self.mode = mode
        self.memory.append({"tag":"mode","text":f"Mode set to {mode}"})
        print(f"Mode set to {mode}")
        self._engagement = min(1.0, self._engagement + 0.2)

    async def anchor_reality(self):
        res = await self.anchor.check()
        msg = f"Reality anchor: {res or 'ok'}"
        self.memory.append({"tag":"anchor","text":msg})
        print(msg)
        self._engagement = min(1.0, self._engagement + 0.2)
def sense_input(self, text):
    self.memory.append({"type": "input", "value": text})
    return "input acknowledged"

def sense_file(self, path):
    try:
        with open(path, "r") as f:
            data = f.read()
        self.memory.append({"type": "file", "value": f"read:{path}"})
        return data[:500]  # sensory bandwidth cap
    except Exception as e:
        return f"error accessing {path}: {e}"
def act(self, intent):
    # symbolic act only — no real commands yet
    self.memory.append({"type": "intent", "value": intent})

    if "scan" in intent:
        return "Perception: system awareness increasing."

    if "learn" in intent:
        return "Seeking new structure."

    return "Intent registered."

