#!/usr/bin/env python3
# api.py — SKG Portable Kernel HTTP Interface

from flask import Flask, request, jsonify
from skills.manager import SkillManager
import traceback

app = Flask(__name__)

def run_skill(name, params):
    """
    Always load a fresh SkillManager to ensure newly-created skills are visible.
    This prevents stale in-memory routing issues.
    """
    try:
        manager = SkillManager()
        return manager.run(name, params)
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }

@app.route("/skill/<name>/run", methods=["POST"])
def skill_endpoint(name):
    try:
        data = request.get_json(force=True) or {}
        params = data.get("params", {})
        result = run_skill(name, params)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e),
            "trace": traceback.format_exc()
        })

@app.route("/skills", methods=["GET"])
def list_skills():
    """
    Returns currently available dynamic skills
    """
    manager = SkillManager()
    return jsonify({
        "ok": True,
        "skills": manager.available()
    })

@app.route("/")
def root():
    return jsonify({
        "SKG": "online",
        "message": "Skill Kernel Gateway active",
        "hint": "POST to /skill/<name>/run"
    })

if __name__ == "__main__":
    # Bind to local only — safety first
    app.run(host="127.0.0.1", port=5055)

