#!/usr/bin/env python3
"""GBOGEB Level-1 dependency-free MIP runtime."""
from __future__ import annotations
import argparse, hashlib, json, math, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTROL=ROOT/'LEVEL1.md'; MANIFEST=ROOT/'level1/manifest.json'; SSOT=ROOT/'level1/ssot.json'; SKILL=ROOT/'skill/SKILL.md'; AGENT=ROOT/'skill/agents/openai.yaml'
BLOCKS={'census':'inventory Level-1 surfaces','modernize':'repair smallest stale/missing gap','innovate':'add useful authority-safe edges','perpetuate':'rerun exact-SHA self-test'}
AGENTS={'census_agent':['census'],'mip_agent':['modernize','innovate','perpetuate'],'evidence_agent':['pca','bt']}

def text(p): return p.read_text(encoding='utf-8') if p.exists() else ''
def obj(p): return json.loads(text(p) or '{}')
def gitsha():
    try: return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return 'UNBOUND'
def digest(p):
    if not p.is_file(): return None
    return hashlib.sha256(p.read_bytes()).hexdigest()

def census():
    marks={'index':'## Index','aod':'## AOD','dmaic':'## DMAIC','pca':'## PCA','bt':'## BT'}
    g={k:(v in text(CONTROL)) for k,v in marks.items()}
    g.update(manifest=MANIFEST.is_file(),ssot=SSOT.is_file(),skill=SKILL.is_file(),runtime=Path(__file__).is_file(),blocks_functions=bool(BLOCKS),agents=AGENT.is_file() and bool(AGENTS),orchestration=callable(orchestrate))
    s=obj(SSOT); n=sum(g.values()); total=len(g)
    return {'schema':'gbogeb-level1-census/v1','repo':s.get('repo',ROOT.name),'head_sha':gitsha(),'gates':g,'passed':n,'total':total,'level':round(n/total,4),'level_1_0':n==total,'existing_runtime_refs':{r:(ROOT/r).exists() for r in s.get('existing_runtime_refs',[])}}

def mip():
    c=census(); s=obj(SSOT); missing=[k for k,v in c['gates'].items() if not v]
    return {'repo':s.get('repo',ROOT.name),'role':s.get('role'),'authority':s.get('authority',{}),'modernize':{'missing_or_stale':missing},'innovate':{'edges':['SSOT->runtime','runtime->agent','agent->orchestrator','metrics->PCA','comparisons->BT'],'authority_transfer':False},'perpetuate':{'command':'python level1/runtime.py self-test','exact_sha_required':True,'promotion':'12/12 + green CI'}}

def pca(rows):
    if len(rows)<3 or not rows or len(rows[0])<2: return {'status':'DEFER_INSUFFICIENT_OBSERVATIONS'}
    p=len(rows[0]); means=[sum(r[j] for r in rows)/len(rows) for j in range(p)]; x=[[r[j]-means[j] for j in range(p)] for r in rows]; d=max(len(rows)-1,1); cov=[[sum(r[i]*r[j] for r in x)/d for j in range(p)] for i in range(p)]; v=[1/math.sqrt(p)]*p
    for _ in range(64):
        w=[sum(cov[i][j]*v[j] for j in range(p)) for i in range(p)]; z=math.sqrt(sum(a*a for a in w))
        if z<1e-15: return {'status':'DEFER_ZERO_VARIANCE'}
        v=[a/z for a in w]
    eig=sum(v[i]*sum(cov[i][j]*v[j] for j in range(p)) for i in range(p)); tv=sum(cov[i][i] for i in range(p))
    return {'status':'PASS_TESTABLE_ENGINE','component':v,'explained_variance_ratio':eig/tv if tv else 0.0}

def bt(pairs):
    if not pairs: return {'status':'DEFER_NO_COMPARISONS','scores':{}}
    names=sorted({x for a,b in pairs for x in (a,b)}); wins={x:0.0 for x in names}; n={(a,b):0 for a in names for b in names if a!=b}
    for a,b in pairs:
        if a==b: continue
        wins[a]+=1; n[(a,b)]+=1; n[(b,a)]+=1
    s={x:1.0 for x in names}
    for _ in range(64):
        q={}
        for a in names:
            den=sum(n[(a,b)]/(s[a]+s[b]) for b in names if b!=a and n[(a,b)])
            q[a]=wins[a]/den if den and wins[a] else 1e-9
        scale=sum(q.values())/len(q); s={k:v/scale for k,v in q.items()}
    return {'status':'PASS_TESTABLE_ENGINE','scores':dict(sorted(s.items(),key=lambda kv:kv[1],reverse=True))}

def orchestrate():
    s=obj(SSOT); return {'status':'READY','repo':s.get('repo',ROOT.name),'role':s.get('role'),'sequence':['census','modernize','innovate','evidence_analysis','perpetuate'],'blocks':BLOCKS,'agents':AGENTS,'federation_targets':s.get('federation_targets',[]),'mip':mip()}

def selftest():
    c=census(); a=pca([[1,1],[2,2.2],[3,2.9],[4,4.1]]); b=bt([['repair','docs'],['repair','style'],['runtime','docs'],['repair','runtime']]); ok=c['level_1_0'] and a['status'].startswith('PASS') and b['status'].startswith('PASS')
    return {'schema':'gbogeb-level1-receipt/v1','status':'PASS' if ok else 'FAIL','head_sha':gitsha(),'census':c,'pca_fixture':a,'bt_fixture':b,'fixture_is_project_evidence':False,'manifest_sha256':digest(MANIFEST),'ssot_sha256':digest(SSOT)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['census','mip','pca','bt','orchestrate','self-test']); ap.add_argument('--input'); a=ap.parse_args()
    if a.command=='census': out=census()
    elif a.command=='mip': out=mip()
    elif a.command=='orchestrate': out=orchestrate()
    elif a.command=='self-test': out=selftest()
    elif not a.input: out={'status':'DEFER_NO_MEASURED_INPUT'}
    else:
        data=json.loads(Path(a.input).read_text(encoding='utf-8')); out=pca(data) if a.command=='pca' else bt(data)
    print(json.dumps(out,indent=2,sort_keys=True)); return 1 if out.get('status')=='FAIL' else 0
if __name__=='__main__': raise SystemExit(main())
