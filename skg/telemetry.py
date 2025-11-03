import logging, os
def get_logger(level="INFO", file_path="logs/telemetry.log"):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    log = logging.getLogger("skg")
    log.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not log.handlers:
        fh = logging.FileHandler(file_path)
        sh = logging.StreamHandler()
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        fh.setFormatter(fmt); sh.setFormatter(fmt)
        log.addHandler(fh); log.addHandler(sh)
    return log
