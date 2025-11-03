import os, time
class RealityAnchor:
    def __init__(self, memory, log):
        self.memory = memory
        self.log = log
    async def check(self):
        try:
            now = time.time()
            exists = os.path.exists("brain/identity.json")
            if not exists:
                return "identity.json missing"
            return None
        except Exception as e:
            return f"anchor error: {e}"
