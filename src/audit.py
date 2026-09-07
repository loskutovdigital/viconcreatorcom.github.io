"""Release checks for static SEO, balanced markup and root/subpath portability."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, urljoin
from collections import Counter
import argparse, json, re, xml.etree.ElementTree as ET
parser=argparse.ArgumentParser();parser.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent.parent/'dist');parser.add_argument('--public',action='store_true');args=parser.parse_args();root=args.directory.resolve()
VOID=set('area base br col embed hr img input link meta param source track wbr'.split())
class Document(HTMLParser):
 def __init__(self,file):super().__init__();self.file=file;self.stack=[];self.ids=[];self.links=[];self.headings=0;self.canonical=[];self.alternates={};self.meta={};self.json=False;self.raw='';self.title='';self.in_title=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag not in VOID:self.stack.append(tag)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='h1':self.headings+=1
  if tag=='title':self.in_title=True
  if tag=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content','')
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
  if tag=='link' and a.get('rel')=='alternate':self.alternates[a.get('hreflang')]=a['href']
  if tag=='script' and a.get('type')=='application/ld+json':self.json=True;self.raw=''
  if tag=='img' and a.get('src'):
   assert a.get('alt'),(self.file,'Image without useful alt')
   assert a.get('width') and a.get('height'),(self.file,'Image without dimensions')
  for attr in ['href','src','poster','data-full']:
   if attr in a:self.links.append(a[attr])
  for attr in ['srcset','imagesrcset']:
   if attr in a:
    self.links.extend(v.strip().split()[0] for v in a[attr].split(','))
 def handle_data(self,data):
  if self.json:self.raw+=data
  if self.in_title:self.title+=data
 def handle_endtag(self,tag):
  assert self.stack and self.stack[-1]==tag,(self.file,tag,self.stack[-6:])
  self.stack.pop()
  if tag=='title':self.in_title=False
  if tag=='script' and self.json:
   data=json.loads(self.raw);assert data.get('@context')=='https://schema.org';self.json=False
pages={}
for file in root.rglob('*.html'):
 d=Document(file);d.feed(file.read_text());assert not d.stack,(file,d.stack)
 assert d.headings==1,(file,'h1',d.headings)
 assert all(n==1 for n in Counter(d.ids).values()),(file,'Duplicate IDs')
 assert 'booking-dialog' in d.ids,(file,'Missing booking modal')
 assert 'width=device-width' in d.meta.get('viewport',''),file
 if file.name!='404.html':
  assert len(d.canonical)==1 and d.meta.get('description'),file
  assert set(d.alternates)=={'en','nl','x-default'},file
  if args.public:assert 'noindex' not in d.meta.get('robots',''),file
 pages[file]=d
 if re.search(r'rijswijk|vicon\.raw|vicon\.jpg|Bilderdijklaan',file.read_text(),re.I):raise AssertionError(('Unexpected private/location text',file))
for field in ['title']:
 assert not [v for v,n in Counter(getattr(d,field) for d in pages.values()).items() if n>1],field
assert len({d.meta.get('description') for f,d in pages.items() if f.name!='404.html'})==len(pages)-1,'Duplicate descriptions'
known={d.canonical[0]:d for d in pages.values() if d.canonical}
incoming=Counter()
for file,d in pages.items():
 for target in d.alternates.values():assert target in known,('Missing alternate',file,target)
 for target in d.alternates.values():
  if d.canonical:assert d.canonical[0] in known[target].alternates.values(),('Non-reciprocal alternate',file)
 for link in d.links:
  parts=urlsplit(link)
  if parts.scheme or link.startswith('//'):continue
  if not parts.path:
   if parts.fragment:assert unquote(parts.fragment) in d.ids,(file,link)
   continue
  dest=root/unquote(parts.path).lstrip('/') if parts.path.startswith('/') else file.parent/unquote(parts.path)
  dest=dest.resolve()
  assert dest.exists(),('Missing link/asset',file,link)
  if dest.is_dir():dest=dest/'index.html';assert dest.exists(),dest
  if dest in pages:
   incoming[dest]+=1
   if parts.fragment:assert unquote(parts.fragment) in pages[dest].ids,(file,link)
for file in pages:
 if file.name!='404.html':assert incoming[file]>0,('Orphan page',file)
for file in root.rglob('*.css'):
 for link in re.findall(r'url\([\'\"]?([^\)\'\"]+)',file.read_text()):
  if urlsplit(link).scheme:continue
  dest=root/link.lstrip('/') if link.startswith('/') else file.parent/link
  assert dest.exists(),('CSS asset',file,link)
sitemap=ET.parse(root/'sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls={n.text for n in sitemap.findall('.//s:loc',ns)};assert urls==set(known),('Sitemap mismatch',len(urls),len(known))
ET.parse(root/'sitemap-images.xml')
if args.public:
 assert 'Disallow: /' not in (root/'robots.txt').read_text()
 assert all(urlsplit(u).scheme=='https' and 'example.invalid' not in u and '.chatgpt.site' not in u for u in urls),'Invalid public origin'
report={'html_pages':len(pages),'indexable_content_pages':len(known) if args.public else 0,'page_pairs':len(known)//2,'broken_links':0,'duplicate_titles':0,'duplicate_descriptions':0,'orphan_pages':0,'balanced_html':True,'reciprocal_hreflang':True,'browser_tested':False,'field_core_web_vitals':'not measured','delivery_tested':False}
print(json.dumps(report,indent=2))
