import platform, socket, json

class fingerprint_host:
    name = "fingerprint_host"

    def run(self, params):
        try:
            info = {
                "hostname": socket.gethostname(),
                "os": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
            }
            return {"ok": True, "fingerprint": info}
        except Exception as e:
            return {"ok": False, "error": str(e)}
