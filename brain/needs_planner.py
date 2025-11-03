import json

RULES = [
    ("interface", "iface_enum", {}),  # keep this
    ("scan", "port_scan_lite", {"target": "127.0.0.1"}),
    ("fingerprint", "fingerprint_host", {}),
]

def plan_from_need(need: str):
    need_l = need.lower()

    # exec_chain special case
    if "improve network enumeration" in need_l or "map network" in need_l:
        return [{"skill": "exec_chain", "params": {
            "commands": [
                "ip -o addr",
                "ip addr",
                "ifconfig",
                "busybox ifconfig"
            ],
            "execute": True
        }}]

    # keyword rules
    for keyword, skill, params in RULES:
        if keyword in need_l:
            return [{"skill": skill, "params": params}]

    # fallback
    return [{"skill": "iface_enum", "params": {}}]

def handler(payload):
    need = payload.get("need","")
    return {"ok": True, "plan": plan_from_need(need)}

# --- Compatibility Layer (adds names expected by API) ---

# old: plan_from_need -> new: make_plan
def make_plan(need):
    if isinstance(need, dict):
        need = need.get("text", "")
    return plan_from_need(need)

