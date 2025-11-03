class EthicsMER:
    def __init__(self, memory, log):
        self.memory = memory
        self.log = log
    async def ethics_cycle(self, mode="unified"):
        note = f"MER tick: mode={mode}"
        self.memory.append({"tag":"mer","text":note})
        self.log.debug(note)
