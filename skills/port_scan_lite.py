#!/usr/bin/env python3
# skills/port_scan_lite.py
import subprocess, shlex

TOP_PORTS = [22, 80, 443, 445, 3389]

def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def _has_nc():
    code, out, err = _run("command -v nc")
    return (out or "").strip() != ""

def _scan_with_nc(target):
    open_ports = []
    for p in TOP_PORTS:
        code, out, err = _run(f"nc -z -w1 {shlex.quote(target)} {p} >/dev/null 2>&1; echo $?")
        if "0" in out.strip():
            open_ports.append(p)
    return open_ports

def _scan_with_bash_tcp(target):
    # Very basic: try connect with timeout 1s
    open_ports = []
    for p in TOP_PORTS:
        code, out, err = _run(f"timeout 1 bash -c '</dev/tcp/{target}/{p}' >/dev/null 2>&1; echo $?")
        if "0" in out.strip():
            open_ports.append(p)
    return open_ports

class Skill:
    name = "port_scan_lite"
    description = "Quick, safe top-port check for a single host"

    def run(self, params):
        target = (params or {}).get("target")
        if not target:
            return {"ok": False, "error": "target required"}
        if _has_nc():
            open_ports = _scan_with_nc(target)
        else:
            open_ports = _scan_with_bash_tcp(target)
        return {"ok": True, "target": target, "open": open_ports}

def run(params):
    return Skill().run(params)

