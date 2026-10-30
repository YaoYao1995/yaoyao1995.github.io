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


import copy
import urllib.error
from bs4 import BeautifulSoup
class ScholarFetchError(RuntimeError):pass

def _integer(text,label,blank_zero=False):
 text=text.strip().replace(',','').replace('\u00a0','')
 if not text and blank_zero:return 0
 if not re.fullmatch(r'\d+',text):raise ScholarFetchError('Missing or invalid '+label)
 return int(text)

def parse_page(html,scholar_id):
 soup=BeautifulSoup(html,'html.parser')
 if soup.select_one('#gs_captcha_ccl, #recaptcha, .g-recaptcha, form[action*="/sorry/"]') or 'unusual traffic from your computer network' in soup.get_text(' ').lower():raise ScholarFetchError('Google Scholar access challenge; retaining previous data')
 name=soup.select_one('#gsc_prf_in');table=soup.select_one('#gsc_a_b');totals=soup.select('#gsc_rsb_st .gsc_rsb_std');more=soup.select_one('#gsc_bpf_more')
 if not name or not name.get_text(strip=True) or table is None or not totals or more is None:raise ScholarFetchError('Incomplete Scholar profile markup')
 metrics={key:_integer(cell.get_text(),key) for key,cell in zip(('citedby','citedby5y','hindex','hindex5y','i10index','i10index5y'),totals)}
 publications={};rows=table.select('tr.gsc_a_tr')
 if not rows:raise ScholarFetchError('Empty Scholar publication page')
 for row in rows:
  title=row.select_one('a.gsc_a_at');citation_cell=row.select_one('td.gsc_a_c');year_cell=row.select_one('td.gsc_a_y')
  if title is None or citation_cell is None or year_cell is None or not title.get_text(strip=True):raise ScholarFetchError('Incomplete Scholar publication row')
  query=urllib.parse.parse_qs(urllib.parse.urlparse(title.get('href','')).query);pid=query.get('citation_for_view',[''])[0]
  if not re.fullmatch(re.escape(scholar_id)+r':[\w-]+',pid) or pid in publications:raise ScholarFetchError('Invalid, foreign or duplicate Scholar publication ID')
  year=year_cell.get_text(strip=True)
  if year and not re.fullmatch(r'(19|20)\d{2}',year):raise ScholarFetchError('Invalid Scholar publication year')
  citation_number=citation_cell.select_one('a.gsc_a_ac')
  if citation_number is None:raise ScholarFetchError('Missing Scholar citation-count element')
  count=_integer(citation_number.get_text(),'publication citations',blank_zero=True);detail=row.select('.gsc_a_t .gs_gray')
  pub={'container_type':'Publication','source':'AUTHOR_PUBLICATION_ENTRY','bib':{'title':title.get_text(' ',strip=True),'pub_year':year},'filled':False,'author_pub_id':pid,'num_citations':count}
  if detail:pub['bib']['author']=detail[0].get_text(' ',strip=True)
  if len(detail)>1:pub['bib']['citation']=detail[1].get_text(' ',strip=True)
  cite_link=citation_cell.select_one('a[href]')
  if cite_link:
   url=urllib.parse.urljoin('https://scholar.google.com',cite_link['href']);pub['citedby_url']=url;cite_ids=urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('cites',[])
   if cite_ids:pub['cites_id']=cite_ids[0].split(',')
  publications[pid]=pub
 has_more=not more.has_attr('disabled')
 if has_more and len(rows)!=100:raise ScholarFetchError('Truncated Scholar page before pagination')
 return dict(name=name.get_text(' ',strip=True),metrics=metrics,publications=publications,has_more=has_more)

def _profile_html(url,opener,sleeper):
 for attempt in range(3):
  try:
   request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept-Language':'en-US,en;q=0.9'})
   with opener(request,timeout=20) as response:
    status=getattr(response,'status',200)
    if status!=200:raise ScholarFetchError('Unexpected Scholar HTTP '+str(status))
    body=response.read(2*1024*1024+1)
    if len(body)>2*1024*1024:raise ScholarFetchError('Oversized Scholar response')
    print('Scholar HTTP 200: '+str(len(body))+' bytes',flush=True)
    return body.decode('utf-8')
  except urllib.error.HTTPError as error:
   if error.code in (403,429):raise ScholarFetchError('Google Scholar HTTP '+str(error.code)+'; previous data retained') from error
   if error.code<500 or attempt==2:raise ScholarFetchError('Google Scholar HTTP '+str(error.code)) from error
  except (urllib.error.URLError,TimeoutError,OSError) as error:
   if attempt==2:raise ScholarFetchError('Google Scholar network failure: '+type(error).__name__) from error
  sleeper(2*(attempt+1))
 raise ScholarFetchError('Google Scholar fetch failed')

def fetch_scholar(scholar_id,previous=None,opener=urllib.request.urlopen,sleeper=time.sleep,max_pages=10):
 if not re.fullmatch(r'[\w-]+',scholar_id):raise ScholarFetchError('Invalid Scholar profile ID')
 publications={};first=None
 for page in range(max_pages):
  query=urllib.parse.urlencode({'hl':'en','user':scholar_id,'pagesize':100,'cstart':page*100})
  print('Fetching Scholar publication page '+str(page+1),flush=True)
  parsed=parse_page(_profile_html('https://scholar.google.com/citations?'+query,opener,sleeper),scholar_id)
  if publications.keys() & parsed['publications'].keys():raise ScholarFetchError('Repeated Scholar pagination; retaining previous data')
  if first is None:first=parsed
  elif parsed['name']!=first['name']:raise ScholarFetchError('Scholar identity changed between pages')
  publications.update(parsed['publications'])
  if not parsed['has_more']:break
  sleeper(1)
 else:raise ScholarFetchError('Scholar page limit reached before completion')
 old_count=len((previous or {}).get('publications',{}))
 if old_count and len(publications)<old_count*.8:raise ScholarFetchError('Unexpected publication-count drop; retaining previous data')
 author=copy.deepcopy(previous or {})
 author.update(container_type='Author',source='AUTHOR_PROFILE_PAGE',scholar_id=scholar_id,name=first['name'],publications=publications,**first['metrics'])
 author['updated']=datetime.now(timezone.utc).isoformat()
 print('Scholar snapshot complete: '+str(len(publications))+' records, '+str(author['citedby'])+' citations',flush=True)
 return author

def current_week(updated,now=None):
 try:
  stamp=datetime.fromisoformat(updated.replace('Z','+00:00'))
  if stamp.tzinfo is None:stamp=stamp.replace(tzinfo=timezone.utc)
  now=now or datetime.now(timezone.utc)
  from datetime import timedelta
  local=timezone(timedelta(hours=8))
  return stamp<=now and stamp.astimezone(local).isocalendar()[:2]==now.astimezone(local).isocalendar()[:2]
 except (ValueError,AttributeError,TypeError):return False

def validate_snapshot(author,previous):
 expected=os.environ['GOOGLE_SCHOLAR_ID']
 if author.get('scholar_id')!=expected:raise ValueError('Wrong Scholar identity')
 pubs=author.get('publications')
 if not isinstance(pubs,dict) or not pubs:raise ValueError('Empty publication list')
 count=author.get('citedby')
 if not isinstance(count,int) or isinstance(count,bool) or count<0:raise ValueError('Invalid citation total')
 if previous.get('citedby',0)>0 and count==0:raise ValueError('Unexpected empty citation total')
 if len(pubs)<len(previous.get('publications',{}))*.8:raise ValueError('Unexpectedly truncated publication list')
 for pid,pub in pubs.items():
  if not pid.startswith(expected+':') or not pub.get('bib',{}).get('title'):raise ValueError('Invalid publication')
  if not isinstance(pub.get('num_citations'),int) or pub['num_citations']<0:raise ValueError('Invalid paper citation count')

def main():
 import pathlib,shutil,signal
 shutil.rmtree('results',ignore_errors=True)
 previous=get_json('https://raw.githubusercontent.com/'+os.environ['GITHUB_REPOSITORY']+'/google-scholar-stats/gs_data.json')
 validate_snapshot(previous,previous)
 event={}
 if os.environ.get('GITHUB_EVENT_PATH'):
  with open(os.environ['GITHUB_EVENT_PATH']) as event_file:event=json.load(event_file)
 metadata_only=str(event.get('inputs',{}).get('metadata_only','false')).lower()=='true'
 if os.environ.get('GITHUB_EVENT_NAME')=='schedule' and current_week(previous.get('updated')):
  print('Already refreshed this week; no Scholar request needed.',flush=True);return
 class RefreshDeadline(BaseException):pass
 def timed_out(signum,frame):raise RefreshDeadline('Refresh exceeded 240 seconds; previous published data retained')
 signal.signal(signal.SIGALRM,timed_out);signal.alarm(240)
 try:
  if metadata_only:
   author=dict(previous)
   print('Rebuilding catalog from last successful Scholar snapshot',flush=True)
  else:
   print('Fetching Google Scholar profile and publication pages',flush=True)
   author=fetch_scholar(os.environ['GOOGLE_SCHOLAR_ID'],previous)
   validate_snapshot(author,previous)
   author['updated']=datetime.now(timezone.utc).isoformat()
  enrich(author,previous)
  author['catalog_updated']=datetime.now(timezone.utc).isoformat()
  if not author['verified_publications']:raise RuntimeError('No verified publications; retaining previous dataset')
  os.makedirs('results',exist_ok=True)
  for name,data in [('gs_data.json',author),('gs_data_shieldsio.json',{'schemaVersion':1,'label':'citations','message':str(author['citedby'])})]:
   target=pathlib.Path('results')/name;temp=target.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');temp.replace(target)
  print('Validated snapshot:',len(author['publications']),'records,',author['citedby'],'citations',flush=True)
 finally:signal.alarm(0)
if __name__=='__main__':main()
