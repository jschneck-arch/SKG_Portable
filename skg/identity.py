import json, os, time
class Identity:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            self.data = {"name":"SKG","created":time.time()}
            self.save()
        else:
            with open(path,"r",encoding="utf-8") as f:
                self.data = json.load(f)
    def save(self):
        with open(self.path,"w",encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
