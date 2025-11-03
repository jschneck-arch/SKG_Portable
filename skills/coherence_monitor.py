# simple reader for telemetry
import json
from statistics import mean

def run(params=None):
    path = 'logs/telemetry.log'
    values = {'C': [], 'Sf': [], 'kappa': [], 'Fi': []}
    try:
        for line in open(path):
            j = json.loads(line)
            for k in values:
                if k in j:
                    values[k].append(j[k])
        avg = {k: mean(v) if v else None for k, v in values.items()}
        return {'ok': True, 'averages': avg}
    except Exception as e:
        return {'ok': False, 'error': str(e)}
