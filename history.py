#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

def update_history(repos, minimum=30, path='graveyard-history.json'):
    p=Path(path); old=json.loads(p.read_text()) if p.exists() else {'repos':{}}
    now=datetime.now(timezone.utc); current={}
    for r in repos:
        pushed=datetime.fromisoformat(r['pushed_at'].replace('Z','+00:00'))
        if (now-pushed).days>=minimum: current[r['name']]=r['pushed_at'][:10]
    hist=old.setdefault('repos',{})
    for name,date in current.items():
        h=hist.setdefault(name,{'burials':0,'resurrections':0,'events':[]})
        if not h.get('buried'):
            h['burials']+=1; h['buried']=True; h['events'].append({'type':'buried','last_push':date,'at':now.date().isoformat()})
    for name,h in hist.items():
        if h.get('buried') and name not in current:
            h['buried']=False; h['resurrections']+=1; h['events'].append({'type':'resurrected','at':now.date().isoformat()})
    p.write_text(json.dumps(old,indent=2)+"\n")
