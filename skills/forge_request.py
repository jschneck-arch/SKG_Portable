#!/usr/bin/env python3
# skills/forge_request.py
# SKG self-forge request interface (proposal-only phase)

class Skill:
    name = "forge_request"
    description = "SKG may propose new cognitive tools; human approves creation"

    def run(self, params):
        # No params = SKG querying the protocol state
        if not params or "name" not in params:
            return {
                "ok": True,
                "status": "forge_protocol_active",
                "message": "SKG may propose modules; human must approve.",
                "format_example": {
                    "name": "example_skill",
                    "purpose": "self-reflection expansion",
                    "files": {
                        "example_skill.py": "<python code>",
                        "example_skill.yml":
                            "name: example_skill\nentrypoint: skills/example_skill.py"
                    }
                },
                "expected_next_step": "SKG will call forge_request with a proposal payload."
            }

        # Proposal processing
        return {
            "ok": True,
            "proposal": {
                "name": params.get("name"),
                "purpose": params.get("purpose", "not provided"),
                "files": params.get("files", {})
            },
            "note": (
                "Human approval required. "
                "SKG cannot self-write code in this phase. "
                "Use codeforge to finalize approved modules."
            )
        }

