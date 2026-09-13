import os, json, re, hashlib, datetime as dt
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
JOBS=DATA/'jobs.json'
SOURCES=DATA/'sources.json'
TIMEOUT=25
KEYWORDS=[
    'intern','internship','supply chain','supply-chain','operations','procurement','logistics',
    'demand planning','supply planning','inventory','material planning','warehouse','manufacturing',
    'business analyst','data analyst','continuous improvement'
]
EXCLUDE=['senior manager','manager','director','vice president','vp ','head of','lead engineer','software engineer']

def now(): return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
def norm(x): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',x or '')).strip()
def slug(company,title,url=''):
    s=f'{company}-{title}-{url}'.lower()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

def serper_search(q):
    key=os.getenv('SERPER_API_KEY')
    if not key: return []
    r=requests.post('https://google.serper.dev/search',headers={'X-API-KEY':key,'Content-Type':'application/json'},json={'q':q,'gl':'in','hl':'en','num':20},timeout=TIMEOUT)
    r.raise_for_status(); return r.json().get('organic',[])

def relevance(title,snippet):
    text=(title+' '+snippet).lower()
    if any(x in text for x in EXCLUDE): return 0
    score=0
    for k in KEYWORDS:
        if k in text: score+=2 if ' ' in k else 1
    if '6 month' in text or '6-month' in text or 'six month' in text: score+=4
    if 'india' in text or 'bengaluru' in text or 'mumbai' in text or 'gurugram' in text or 'delhi' in text or 'ahmedabad' in text: score+=2
    return score

def extract_results(company, results):
    out=[]
    for x in results:
        title=norm(x.get('title','')); link=x.get('link',''); snippet=norm(x.get('snippet',''))
        sc=relevance(title,snippet)
        if sc<4: continue
        out.append({'id':slug(company,title,link),'company':company,'title':title,'description':snippet,'apply_url':link,'career_url':'','score':min(99,60+sc*3),'source':'web-search'})
    return out

def main():
    jobs=json.loads(JOBS.read_text())
    by_id={j['id']:j for j in jobs}
    sources=json.loads(SOURCES.read_text())
    stamp=now(); discovered=0; updated=0
    for src in sources:
        try:
            results=serper_search(src['query'])
            for item in extract_results(src['company'],results):
                discovered+=1
                existing=by_id.get(item['id'])
                if existing:
                    existing['last_seen']=stamp; existing['status']='active';
                    if item.get('description'): existing['description']=item['description']
                else:
                    item.update({'location':'India','sector':'FMCG / Consumer','category':'New Discovery','why':'Potential FMCG/operations/supply-chain fit; review listing details.','missing':'Needs manual verification against your 6-month internship requirement.','status':'new','first_seen':stamp,'last_seen':stamp})
                    item['career_url']=src['career']; by_id[item['id']]=item; updated+=1
        except Exception as e:
            print(f'WARN {src["company"]}: {e}')
    JOBS.write_text(json.dumps(list(by_id.values()),indent=2,ensure_ascii=False))
    (DATA/'sync.json').write_text(json.dumps({'last_sync':stamp,'discovered':discovered,'new_jobs':updated,'provider':'Serper' if os.getenv('SERPER_API_KEY') else 'Seed only','note':'Set SERPER_API_KEY in GitHub Actions secrets for automated web discovery.'},indent=2))
    print(f'Sync complete: discovered={discovered}, new={updated}')

if __name__=='__main__': main()
