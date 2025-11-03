#!/usr/bin/env python3
import subprocess, json

class Skill:
    name = "exec_chain"
    description = "Execute shell commands in controlled chain"

    def run(self, params):
        commands = params.get("commands", [])
        if not isinstance(commands, list):
            return {"ok": False, "error": "commands must be list"}

        results = []
        full_output = ""

        for cmd in commands:
            try:
                r = subprocess.run(
                    cmd, shell=True,
                    capture_output=True, text=True
                )
                out = r.stdout.strip()
                full_output += f"$ {cmd}\n{out}\n\n"
                results.append({cmd: out})

            except Exception as e:
                results.append({cmd: str(e)})

        return {"ok": True, "output": full_output, "results": results}

def run(params):
    return Skill().run(params)

