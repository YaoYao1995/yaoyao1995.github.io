"""Weekly citation refresh and conservative formal-publication verification."""
import json, os, re, time, unicodedata, urllib.request, urllib.parse
from datetime import datetime, timezone
from difflib import SequenceMatcher

# Publisher DOI records checked on 2026-10-30; never infer a venue from a title.
DOIS = {'g5m5HwL7SMYC':'10.1016/j.jhydrol.2026.135686','hMod-77fHWUC':'10.1109/tkde.2023.3332671','bEWYMUwI8FkC':'10.1609/aaai.v36i11.21440','TFP_iSt0sucC':'10.1609/icaps.v31i1.15989','e5wmG9Sq2KIC':'10.1109/icra48506.2021.9561842','O3NaXMp0MMsC':'10.1016/j.jhydrol.2025.133117','R3hNpaxXUhUC':'10.1109/cai59869.2024.00146','isC4tDSrTZIC':'10.1109/icme.2019.00050','GnPB-g6toBAC':'10.1609/aaai.v39i15.33728','BqipwSGYUEgC':'10.1609/aaai.v39i13.33584','k_IJM867U9cC':'10.1007/978-3-319-94289-6_19','ns9cj8rnVeAC':'10.1109/tip.2025.3526066','_Qo2XoVZTnwC':'10.1007/978-3-031-30108-7_28','J_g5lzvAfSwC':'10.1109/tgrs.2025.3601628','j3f4tGmQtD8C':'10.1109/icassp.2019.8682832','r0BpntZqJG4C':'10.1016/j.physa.2019.122236'}
VENUES = [('transactions on image processing','IEEE TIP'),('transactions on knowledge and data engineering','IEEE TKDE'),('transactions on geoscience and remote sensing','IEEE TGRS'),('transactions on pattern analysis and machine intelligence','IEEE TPAMI'),('journal of hydrology','Journal of Hydrology'),('journal of computational physics','J. Comput. Phys.'),('journal of cleaner production','Journal of Cleaner Production'),('water research','Water Research'),('physica a','Physica A'),('aaai conference','AAAI'),('automated planning and scheduling','ICAPS'),('robotics and automation','ICRA'),('acoustics, speech and signal processing','ICASSP'),('multimedia and expo','ICME'),('conference on artificial intelligence (cai)','IEEE CAI'),('asian conference on machine learning','ACML'),('web services','ICWS'),('neural information processing','ICONIP'),('neural information processing systems','NeurIPS'),('international conference on machine learning','ICML'),('computer vision and pattern recognition','CVPR'),('international conference on computer vision','ICCV'),('european conference on computer vision','ECCV'),('international joint conference on artificial intelligence','IJCAI'),('knowledge discovery and data mining','KDD'),('international conference on learning representations','ICLR')]
CONFERENCES={'AAAI','ICAPS','ICRA','ICASSP','ICME','IEEE CAI','ACML','ICWS','ICONIP','NeurIPS','ICML','CVPR','ICCV','ECCV','IJCAI','KDD','ICLR'}
PATENTS={'vV6vV6tmYwMC','NaGl4SEjCO4C','M05iB0D1s5AC'}

def normalize(s):
 return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',re.sub('<[^>]+>','',s)).lower())
def short_venue(venue):
 for text,short in sorted(VENUES,key=lambda x:-len(x[0])):
  if text in venue.lower():return short
 return venue

def get_json(url):
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'YaoAcademicHomepage/1.0 (https://yaoyao1995.github.io/)'})
   with urllib.request.urlopen(req,timeout=15) as response:return json.load(response)
  except Exception:
   if attempt==2:raise
   time.sleep(3*(attempt+1))

def candidate(title,record):
 titles=record.get('title') or [];venues=record.get('container-title') or []
 if not titles or not venues:return None
 clean_title=re.sub('<[^>]+>','',titles[0])
 if SequenceMatcher(None,normalize(title),normalize(clean_title)).ratio()<.98:return None
 authors=record.get('author',[])
 if not any(a.get('ORCID','').endswith('0000-0001-9887-4301') or (normalize(a.get('given',''))=='yao' and normalize(a.get('family',''))=='yao') for a in authors):return None
 venue=venues[-1];short=short_venue(venue);kind=record.get('type');conference=short in CONFERENCES
 if re.search(r'arxiv|biorxiv|medrxiv|ssrn|preprint|patent|research square|techrxiv|egusphere',venue,re.I):return None
 if kind=='journal-article':
  if re.search(r'proceedings|conference|symposium',venue,re.I) and not conference:return None
 elif kind in ('proceedings-article','book-chapter'):
  if not conference:return None
 else:return None
 dates=record.get('published',{}).get('date-parts') or []
 if not dates or not dates[0]:return None
 year=dates[0][0];doi=record.get('DOI','')
 if not isinstance(year,int) or not 1900<=year<=datetime.now().year+1 or not doi.startswith('10.'):return None
 return dict(title=clean_title,venue=venue,venue_short=short,year=year,url='https://doi.org/'+doi,kind='conference' if conference else 'journal',authors=', '.join((a.get('given','')+' '+a.get('family','')).strip() for a in authors),source='Crossref publisher metadata')

def enrich(author,previous=None):
 old=(previous or {}).get('verified_publications',{});results={};excluded=[];failures=[]
 for pid,pub in author['publications'].items():
  title=pub.get('bib',{}).get('title','');suffix=pid.split(':')[-1]
  if suffix in PATENTS:
   excluded.append({'id':pid,'reason':'patent'});continue
  cached=old.get(pid)
  if cached and cached.get('scholar_title')!=title:cached=None
  item=dict(cached) if cached else None
  if suffix=='iH-uZ7U-co4C' and normalize(title)==normalize('Robust model-based reinforcement learning for autonomous greenhouse control'):
   item=dict(title=title,venue='Asian Conference on Machine Learning',venue_short='ACML',year=2021,url='https://proceedings.mlr.press/v157/zhang21e.html',kind='conference',authors='Wanpeng Zhang, Xiaoyan Cao, Yao Yao, Zhicheng An, Xi Xiao, Dijun Luo',source='PMLR official proceedings')
  if not item:
   try:
    if suffix in DOIS:
     records=[get_json('https://api.crossref.org/works/'+urllib.parse.quote(DOIS[suffix],safe=''))['message']]
    else:
     query=urllib.parse.urlencode({'query.title':title,'rows':5})
     records=get_json('https://api.crossref.org/works?'+query)['message']['items']
    item=next((r for m in records if (r:=candidate(title,m))),None)
    time.sleep(1)
   except Exception as error:
    print('Metadata lookup failed:',pid,type(error).__name__);failures.append(pid)
  if item:
   item['venue_short']=short_venue(item['venue']);item['scholar_title']=title;item['scholar_id']=pid;item['citations']=pub.get('num_citations',0)
   results[pid]=item
  else:excluded.append({'id':pid,'reason':'no verified journal or recognized conference paper'})
 # Do not silently publish an incomplete catalog when metadata services fail.
 if failures:raise RuntimeError('Metadata unavailable for '+str(len(failures))+' records; retaining previous dataset')
 author['catalog_schema']=1;author['verified_publications']=results;author['excluded_publications']=excluded
 print('Verified formal papers:',len(results),'Excluded / unverified:',len(excluded))
 return author

def main():
 from scholarly import scholarly
 author=scholarly.search_author_id(os.environ['GOOGLE_SCHOLAR_ID'])
 scholarly.fill(author,sections=['basics','indices','counts','publications'])
 author['updated']=datetime.now(timezone.utc).isoformat()
 author['publications']={p['author_pub_id']:p for p in author['publications']}
 try:previous=get_json('https://raw.githubusercontent.com/'+os.environ['GITHUB_REPOSITORY']+'/google-scholar-stats/gs_data.json')
 except Exception:previous={}
 enrich(author,previous)
 if not author['verified_publications']:raise RuntimeError('No verified publications; retaining previous dataset')
 os.makedirs('results',exist_ok=True)
 with open('results/gs_data.json','w') as f:json.dump(author,f,ensure_ascii=False)
 with open('results/gs_data_shieldsio.json','w') as f:json.dump({'schemaVersion':1,'label':'citations','message':str(author['citedby'])},f)
if __name__=='__main__':main()
