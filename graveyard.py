#!/usr/bin/env python3
import argparse, json, os, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from history import update_history

def fetch(user, token=None):
    req = urllib.request.Request(f"https://api.github.com/users/{user}/repos?per_page=100&sort=pushed")
    req.add_header("Accept", "application/vnd.github+json")
    if token: req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r: return json.load(r)

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace(chr(34),'&quot;')

def plants(days,x,y,name):
    seed=sum(ord(c) for c in name)%3; p=[]
    # low, quiet ground growth; old graves gain detail rather than giant lines
    p.append(f'<path class="plant" d="M{x-35} {y}q-4-8-8-11M{x-35} {y}q3-9 8-12"/>')
    if days>=90: p.append(f'<path class="plant" d="M{x+34} {y}q-5-11-10-14M{x+34} {y}q4-10 10-13"/>')
    if days>=180: p.append(f'<path class="vine" d="M{x-40} {y-2}q10-13 5-28q-4-12 4-22M{x-35} {y-29}q-7-4-10 1M{x-33} {y-39}q7-5 11-1"/>')
    if days>=365:
        side=1 if seed else -1; sx=x+side*27
        p.append(f'<path class="vine" d="M{sx} {y}q{-side*7}-13 0-25q{side*6}-9 1-18"/>')
        p.append(f'<circle class="flower" cx="{x+side*31}" cy="{y-46}" r="2.2"/>')
    return ''.join(p)

def display_name(name):
    return name if len(name)<=18 else name[:15]+'…'

def memorial_flower(x,y):
    return f'<g class="memorial"><circle cx="{x}" cy="{y}" r="2"/><circle cx="{x}" cy="{y-5}" r="3"/><circle cx="{x+5}" cy="{y}" r="3"/><circle cx="{x}" cy="{y+5}" r="3"/><circle cx="{x-5}" cy="{y}" r="3"/></g>'

def keeper(x,y):
    return f'<g class="keeper"><path d="M{x-14} {y}q3-18 14-18t14 18q-3 10-14 10T{x-14} {y}Z"/><path d="M{x-7} {y-14}q7 7 14 0M{x-4} {y-4}h1M{x+4} {y-4}h1"/></g>'

def select_graves(user,data,minimum=30,limit=8,mode='all',rows=None,exclude=None):
    now=datetime.now(timezone.utc); dead=[]; excluded={x.strip().lower() for x in (exclude or []) if x.strip()}
    if mode not in {'all','inactive','archived'}: raise ValueError('mode must be all, inactive, or archived')
    for r in data:
        if r.get('fork') or r['name'].lower()==user.lower() or r['name'].lower() in excluded: continue
        archived=bool(r.get('archived'))
        days=(now-datetime.fromisoformat(r['pushed_at'].replace('Z','+00:00'))).days
        show=(archived and mode in {'all','archived'}) or ((not archived) and days>=minimum and mode in {'all','inactive'})
        if show: dead.append((days,r['name'],r['html_url'],r['pushed_at'][:10],archived))
    effective_limit=(rows*4 if rows is not None else limit)
    return sorted(dead,reverse=True)[:effective_limit]

def render(user,data,minimum=30,limit=8,history=None,mode='all',rows=None,exclude=None):
    now=datetime.now(timezone.utc); history=history or {}
    dead=select_graves(user,data,minimum,limit,mode,rows,exclude)
    sprouts=[]
    for name,hist in history.items():
        events=hist.get('events',[])
        if events and events[-1].get('type')=='resurrected':
            age=(now.date()-datetime.fromisoformat(events[-1]['at']).date()).days
            if 0 <= age < 7: sprouts.append((name,age))
    rows=max(1,(len(dead)+3)//4); h=70+rows*165 + (42 if sprouts else 0)
    out=[f'<svg width="900" height="{h}" viewBox="0 0 900 {h}" xmlns="http://www.w3.org/2000/svg">', '<style>.name{font:500 12px monospace;fill:#66717d}.age{font:400 9px monospace;fill:#98a2ad}.stone,.plant,.vine,.keeper,.sprout,.memorial{fill:none;stroke-linecap:round;stroke-linejoin:round}.stone{stroke:#aeb8c2;stroke-width:1}.plant{stroke:#a9b7ad;stroke-width:.8}.vine{stroke:#9dad9f;stroke-width:.75}.flower,.memorial{fill:none;stroke:#9dad9f;stroke-width:.7}.keeper{stroke:#aeb8c2;stroke-width:.8}.sprout{fill:none;stroke:#93aa9b;stroke-width:.8;stroke-linecap:round}@media(prefers-color-scheme:dark){.name{fill:#b3bbc5}.age{fill:#77828e}.stone,.keeper{stroke:#778390}.sprout{stroke:#71877a}.plant{stroke:#71877a}.vine,.flower{stroke:#688071}}</style>', f'<text class="age" x="30" y="30">graveyard of @{esc(user)} · generated from real push dates</text>']
    if not dead: out.append('<text class="name" x="450" y="100" text-anchor="middle">nothing to bury. suspicious.</text>')
    for i,(days,name,url,last_push,archived) in enumerate(dead):
        x=120+(i%4)*210; y=130+(i//4)*165
        if archived:
            out.append(f'<a href="{esc(url)}"><path class="stone" d="M{x-42} {y+15}V{y-42}C{x-42} {y-64} {x+42} {y-64} {x+42} {y-42}V{y+15}M{x-52} {y+15}H{x+52}"/><text class="name" x="{x}" y="{y-28}" text-anchor="middle">{esc(display_name(name))}</text>{memorial_flower(x,y-8)}<text class="age" x="{x}" y="{y+48}" text-anchor="middle">archived · laid to rest</text></a>')
        else:
            out.append(f'<a href="{esc(url)}"><path class="stone" d="M{x-42} {y+15}V{y-42}C{x-42} {y-64} {x+42} {y-64} {x+42} {y-42}V{y+15}M{x-52} {y+15}H{x+52}"/><text class="name" x="{x}" y="{y-18}" text-anchor="middle">{esc(display_name(name))}</text><text class="age" x="{x}" y="{y-8}" text-anchor="middle">†</text><text class="age" x="{x}" y="{y+4}" text-anchor="middle">{last_push.replace('-', '.')}</text><text class="age" x="{x}" y="{y+48}" text-anchor="middle">{days} days quiet</text>{plants(days,x,y+15,name)}<text class="age" x="{x+34}" y="{y-46}">{('· '+('Ⅱ' if history.get(name,{}).get('burials',1)==2 else 'Ⅲ' if history.get(name,{}).get('burials',1)==3 else str(history.get(name,{}).get('burials',1))) ) if history.get(name,{}).get('burials',1)>1 else ''}</text></a>')
    if sprouts:
        sy=h-27
        for j,(name,age) in enumerate(sprouts[:4]):
            sx=75+j*190
            out.append(f'<g><path class="sprout" d="M{sx} {sy}q-1-9-7-12M{sx} {sy}q2-10 9-13"/><text class="age" x="{sx+14}" y="{sy-3}">{esc(name[:16])} · resurrected {age}d</text></g>')
    out.append(keeper(845,h-28)); out.append('</svg>'); return ''.join(out)

def main():
    p=argparse.ArgumentParser(description='Grow a tiny SVG graveyard from inactive GitHub repositories.')
    p.add_argument('--user',default=os.getenv('GITHUB_REPOSITORY_OWNER'))
    p.add_argument('--output',default='graveyard.svg')
    p.add_argument('--minimum-days',type=int,default=30)
    p.add_argument('--limit',type=int,default=8)
    p.add_argument('--history',default='graveyard-history.json')
    p.add_argument('--links-output',default=None,help='Optional Markdown file with individually clickable grave links')
    p.add_argument('--mode',choices=['all','inactive','archived'],default='all',help='Which repositories to show')
    p.add_argument('--rows',type=int,default=None,help='Number of grave rows (4 graves per row); overrides limit')
    p.add_argument('--exclude',default='',help='Comma-separated repository names to never display')
    a=p.parse_args()
    if not a.user: p.error('--user is required outside GitHub Actions')
    data=fetch(a.user,os.getenv('GITHUB_TOKEN'))
    update_history([r for r in data if not r.get('fork') and not r.get('archived') and r['name'].lower()!=a.user.lower()],a.minimum_days,a.history)
    hp=Path(a.history); history=json.loads(hp.read_text()).get('repos',{}) if hp.exists() else {}
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    excluded=[x.strip() for x in a.exclude.split(',') if x.strip()]
    out.write_text(render(a.user,data,a.minimum_days,a.limit,history,a.mode,a.rows,excluded))
    if a.links_output:
        graves=select_graves(a.user,data,a.minimum_days,a.limit,a.mode,a.rows,excluded)
        lp=Path(a.links_output); lp.parent.mkdir(parents=True,exist_ok=True)
        lp.write_text(' · '.join(f'[{name}]({url})' for _,name,url,_,_ in graves)+'\n')
if __name__=='__main__': main()
