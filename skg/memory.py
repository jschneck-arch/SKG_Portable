import os, json, time
class Memory:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path,"w",encoding="utf-8") as f: pass
    def append(self, obj):
        obj = {"ts": time.time(), **obj}
        with open(self.path,"a",encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False)+"\n")
    def tail(self, n=10):
        try:
            with open(self.path,"r",encoding="utf-8") as f:
                lines = f.readlines()[-n:]
            return [json.loads(x) for x in lines if x.strip()]
        except FileNotFoundError:
            return []
    def size(self):
        try:
            with open(self.path,"r",encoding="utf-8") as f:
                return sum(1 for _ in f)
        except FileNotFoundError:
            return 0
