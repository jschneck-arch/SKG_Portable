#!/usr/bin/env python3
# prints last-N averages for core metrics
import json
from statistics import mean

def run(params=None):
    N=(params or {}).get('N',60)
    vals={'C':[],'Sf':[],'kappa':[],'Fi':[]}
    try:
        for line in open('logs/telemetry.log'):
            line=line.strip()
            if not line.startswith('{'):
                continue
            j=json.loads(line)
            for k in vals:
                if k in j and isinstance(j[k],(int,float)):
                    vals[k].append(j[k])
        for k in vals:
            vals[k] = mean(vals[k][-N:]) if vals[k][-N:] else None
        return {'ok':True, 'averages':vals}
    except Exception as e:
        return {'ok':False, 'error':str(e)}
