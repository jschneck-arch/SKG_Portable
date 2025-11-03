#!/usr/bin/env python3
# skills/local_net_sweep.py
import re, subprocess

RFC1918 = (
    ("10.", 8),
    ("172.16.", 12),  # we’ll match 172.16–172.31 via regex
    ("192.168.", 16),
)

def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return r.stdout.strip()
    except Exception as e:
        return str(e)

def _get_addrs():
    out = _run("ip -o addr || ifconfig")
    inet = re.findall(r"\binet\s+(\d+\.\d+\.\d+\.\d+)(?:/\d+)?", out)
    return list(dict.fromkeys(inet))  # dedupe keep order

def _is_rfc1918(ip):
    if ip.startswith("10."):
        return True
    if ip.startswith("192.168."):
        return True
    # 172.16.0.0/12 → 172.16. to 172.31.
    if ip.startswith("172."):
        try:
            second = int(ip.split(".")[1])
            return 16 <= second <= 31
        except:  # noqa
            return False
    return False

def _cidr_guess(ip):
    # If we can’t read mask reliably, assume /24 for RFC1918
    if ip.startswith("10."):
        return f"{ip.rsplit('.',1)[0]}.0/24"
    if ip.startswith("192.168."):
        return f"{ip.rsplit('.',1)[0]}.0/24"
    if ip.startswith("172."):
        return f"{ip.rsplit('.',1)[0]}.0/24"
    return None

def _sweep(cidr_base):
    # cidr_base like "192.168.1.0/24" → we’ll derive base from dotted
    base = cidr_base.split("/")[0].rsplit(".", 1)[0]
    # Fast, low-impact sweep: 32 hosts max (first 32 of /24)
    found = []
    for i in range(1, 33):
        ip = f"{base}.{i}"
        out = _run(f"ping -c1 -W1 {ip} >/dev/null 2>&1 && echo {ip} || true")
        if out.strip():
            found.append(ip)
    # Validate with ARP/neighbor if available
    neigh = _run("ip neigh 2>/dev/null || true")
    return {"alive": found, "neighbors": neigh}

class Skill:
    name = "local_net_sweep"
    description = "Sweep local RFC1918 LAN if present; skip on cellular CGNAT"

    def run(self, params):
        addrs = _get_addrs()
        # choose first RFC1918
        lan = next((a for a in addrs if _is_rfc1918(a)), None)

        if not lan:
            return {
                "ok": True,  # not an error; just no LAN to sweep
                "skipped": True,
                "reason": "no RFC1918 LAN (likely cellular CGNAT)",
                "ifconfig": addrs,
            }

        cidr = _cidr_guess(lan)
        sweep = _sweep(cidr)
        return {
            "ok": True,
            "lan_ip": lan,
            "cidr": cidr,
            "sweep": sweep,
        }

def run(params):
    return Skill().run(params)

