from flask import Flask, jsonify
import json, os

app = Flask(__name__)

def read_memory():
    path = os.path.expanduser("~/SKG_Portable/brain/memory.jsonl")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        lines = f.readlines()[-50:]
        try:
            return [json.loads(l) for l in lines]
        except:
            return []

@app.route("/telemetry")
def telemetry():
    mem = read_memory()
    return jsonify({
        "identity": "SKG",
        "mode": "unified",
        "recent_memory": mem,
        "memory_items": len(mem)
    })

@app.route("/")
def index():
    return """
    <html>
        <head><title>SKG Cockpit</title></head>
        <body>
            <h2>SKG Telemetry Cockpit</h2>
            <p>Live cognitive state streaming...</p>
            <script>
                async function tick(){
                    let r = await fetch('/telemetry');
                    let j = await r.json();
                    document.body.innerHTML = '<pre>' + JSON.stringify(j, null, 2) + '</pre>';
                }
                setInterval(tick, 2000);
                tick();
            </script>
        </body>
    </html>"""

