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

def plants(days,x,y):
    p=[]
    if days>=30: p.append(f'<path class="plant" d="M{x-28} {y}q-7-13-13-17M{x-28} {y}q6-14 13-19"/>')
    if days>=90: p.append(f'<path class="plant" d="M{x+30} {y}q10-20 1-36M{x+31} {y-22}q12-8 18-2M{x+31} {y-29}q-11-8-16-1"/>')
    if days>=180: p.append(f'<path class="vine" d="M{x-43} {y-7}q25-17 17-48q-5-18 10-31M{x-27} {y-51}q-13-8-18 2"/>')
    if days>=365: p.append(f'<path class="vine" d="M{x+42} {y-5}q-23-24-9-49q10-18-2-36M{x+34} {y-55}q13-8 18 1"/>')
    return ''.join(p)

def render(user,data,minimum=30,limit=8):
    now=datetime.now(timezone.utc); dead=[]
    for r in data:
        if r.get('fork') or r.get('archived') or r['name'].lower()==user.lower(): continue
        days=(now-datetime.fromisoformat(r['pushed_at'].replace('Z','+00:00'))).days
        if days>=minimum: dead.append((days,r['name'],r['html_url'],r['pushed_at'][:10]))
    dead=sorted(dead,reverse=True)[:limit]
    rows=max(1,(len(dead)+3)//4); h=70+rows*165
    out=[f'<svg width="900" height="{h}" viewBox="0 0 900 {h}" xmlns="http://www.w3.org/2000/svg">', '<style>.name{font:500 12px monospace;fill:#66717d}.age{font:400 9px monospace;fill:#98a2ad}.stone,.plant,.vine{fill:none;stroke:#aeb8c2;stroke-width:1.1;stroke-linecap:round;stroke-linejoin:round}.plant{stroke:#94a69a}.vine{stroke:#84998a}@media(prefers-color-scheme:dark){.name{fill:#b3bbc5}.age{fill:#77828e}.stone{stroke:#778390}.plant{stroke:#71877a}.vine{stroke:#688071}}</style>', f'<text class="age" x="30" y="30">graveyard of @{esc(user)} · generated from real push dates</text>']
    if not dead: out.append('<text class="name" x="450" y="100" text-anchor="middle">nothing to bury. suspicious.</text>')
    for i,(days,name,url,last_push) in enumerate(dead):
        x=120+(i%4)*210; y=130+(i//4)*165
        out.append(f'<a href="{esc(url)}"><path class="stone" d="M{x-42} {y+15}V{y-42}C{x-42} {y-64} {x+42} {y-64} {x+42} {y-42}V{y+15}M{x-52} {y+15}H{x+52}"/><text class="name" x="{x}" y="{y-18}" text-anchor="middle">{esc(name[:20])}</text><text class="age" x="{x}" y="{y+34}" text-anchor="middle">died {last_push}</text><text class="age" x="{x}" y="{y+48}" text-anchor="middle">{days} days quiet</text>{plants(days,x,y+15)}</a>')
    out.append('</svg>'); return ''.join(out)

def main():
    p=argparse.ArgumentParser(description='Grow a tiny SVG graveyard from inactive GitHub repositories.')
    p.add_argument('--user',default=os.getenv('GITHUB_REPOSITORY_OWNER'))
    p.add_argument('--output',default='graveyard.svg')
    p.add_argument('--minimum-days',type=int,default=30)
    p.add_argument('--limit',type=int,default=8)
    a=p.parse_args()
    if not a.user: p.error('--user is required outside GitHub Actions')
    data=fetch(a.user,os.getenv('GITHUB_TOKEN'))
    update_history([r for r in data if not r.get('fork') and not r.get('archived') and r['name'].lower()!=a.user.lower()],a.minimum_days)
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(render(a.user,data,a.minimum_days,a.limit))
if __name__=='__main__': main()
