import sys, os, time, json
sys.path.append(os.path.expanduser("~/SKG_Portable"))

from needs_manager import get_active_needs, get_need, resolve_need
from needs_planner import plan_from_need
from skills.manager import SkillManager

mgr = SkillManager()

# inside daemon.py after imports and init
print("[SKG:BRAIN] Boot OK")
print("[SKG:BRAIN] Autonomous loop started...")

while True:
    try:
        needs = get_active_needs()
        if needs:
            need = needs[0]
            print(f"[SKG:BRAIN] Need detected: {need}")
            plan = plan_from_need(need)
            print(f"[SKG:BRAIN] Generated plan: {plan}")

            if plan:
                step = plan[0]
                skill = step.get("skill")
                params = step.get("params", {})
                print(f"[SKG:BRAIN] Executing skill '{skill}' with params {params}")
                result = mgr.run(skill, params)
                print(f"[SKG:BRAIN] Skill result: {result}")
                # only call resolve if skill succeeded or per your logic
                if getattr(result, "get", None):
                    ok = result.get("ok", False)
                else:
                    ok = False
                if ok:
                    resolve_need(str(need))
                else:
                    print("[SKG:BRAIN] Skill failed, need not resolved")
                    # optional: write a new need/fallback
                    # write_need("improve network enumeration capabilities")
            else:
                print("[SKG:BRAIN] Generated empty plan, resolving need")
                resolve_need(str(need))
        else:
            print("[SKG:BRAIN] No needs. Idling...")
        time.sleep(4)
    except Exception as e:
        print(f"[SKG:BRAIN] Error: {e}")
        time.sleep(5)

