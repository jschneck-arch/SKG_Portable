#!/usr/bin/env python3
# skills/mindstream_sink.py
"""
Thin wrapper so any skill can log a pearl via a uniform interface.
"""

from skills import memory_pearl as mp

class Skill:
    name = "mindstream_sink"
    description = "Record a mindstream pearl via memory_pearl."

    def run(self, params):
        params = params or {}
        return mp.write_pearl(
            kind=params.get("kind","trace"),
            msg=params.get("msg",""),
            context=params.get("context",""),
            truth_anchor=bool(params.get("truth_anchor", True)),
            extras=params.get("extras", {})
        )

def run(params):
    return Skill().run(params)

