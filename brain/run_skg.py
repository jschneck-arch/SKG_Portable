# run_skg.py — main execution loop launcher

import time
from daemon import load_skills, Brain

if __name__ == "__main__":
    print("[SKG:BRAIN] Booting brain...")
    skills = load_skills()
    brain = Brain(skills)

    print("[SKG:BRAIN] Boot OK")
    print("[SKG:BRAIN] Autonomous loop started...")

    while True:
        try:
            brain.loop_once()
        except Exception as e:
            print("[SKG:BRAIN] ERROR:", e)
        time.sleep(1)

