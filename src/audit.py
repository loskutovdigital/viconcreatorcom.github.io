"""Release checks for static SEO, balanced markup and root/subpath portability."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, urljoin
from collections import Counter
import argparse, json, re, xml.etree.ElementTree as ET
from content import ORIGIN
parser=argparse.ArgumentParser();parser.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent.parent/'dist');parser.add_argument('--public',action='store_true');parser.add_argument('--expected-origin',default=ORIGIN);args=parser.parse_args();root=args.directory.resolve()
VOID=set('area base br col embed hr img input link meta param source track wbr'.split())
class Document(HTMLParser):
 def __init__(self,file):super().__init__();self.file=file;self.stack=[];self.ids=[];self.links=[];self.headings=0;self.canonical=[];self.alternates={};self.meta={};self.json=False;self.raw='';self.title='';self.in_title=False;self.images=[];self.structured=[]
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
   self.images.append(a['src'])
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
   data=json.loads(self.raw);assert data.get('@context')=='https://schema.org';self.structured.append(data);self.json=False
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
image_map=ET.parse(root/'sitemap-images.xml')
image_ns={'s':ns['s'],'i':'http://www.google.com/schemas/sitemap-image/1.1'}
mapped_images={}
for entry in image_map.findall('s:url',image_ns):
 page_url=entry.findtext('s:loc',namespaces=image_ns)
 assert page_url in known,('Unknown image sitemap page',page_url)
 assert page_url not in mapped_images,('Duplicate image sitemap page',page_url)
 mapped_images[page_url]={n.text for n in entry.findall('i:image/i:loc',image_ns)}
expected_images={}
for page_url,d in known.items():
 images={urljoin(page_url,src) for src in d.images if '/assets/photos/' in urljoin(page_url,src)}
 if images:expected_images[page_url]=images
assert mapped_images==expected_images,'Image sitemap does not match the photographs shown on each page'
for entry in sitemap.findall('s:url',ns):
 page_url=entry.findtext('s:loc',namespaces=ns)
 alternates={n.attrib['hreflang']:n.attrib['href'] for n in entry.findall('{http://www.w3.org/1999/xhtml}link')}
 assert alternates==known[page_url].alternates,('Sitemap language URLs differ from HTML',page_url)
if args.public:
 expected=args.expected_origin.rstrip('/')
 robots=(root/'robots.txt').read_text()
 assert 'Disallow: /' not in robots
 assert {line.split(':',1)[1].strip() for line in robots.splitlines() if line.startswith('Sitemap:')}=={expected+'/sitemap.xml',expected+'/sitemap-images.xml'},'Wrong robots.txt sitemap domain'
 assert all(urlsplit(u).scheme=='https' and 'example.invalid' not in u and '.chatgpt.site' not in u for u in urls),'Invalid public origin'
 def check_structured(value):
  if isinstance(value,dict):
   for key,item in value.items():
    if key in ('url','@id','contentUrl','thumbnailUrl') and isinstance(item,str):assert item.startswith(expected+'/'),('Wrong structured-data domain',item)
    check_structured(item)
  elif isinstance(value,list):
   for item in value:check_structured(item)
 for file,d in pages.items():
  if file.name=='404.html':continue
  path=file.parent.relative_to(root).as_posix()
  assert d.canonical==[expected+('/' if path=='.' else '/'+path+'/')],('Wrong canonical domain/path',file,d.canonical)
  assert d.meta.get('og:url')==d.canonical[0],('Wrong Open Graph URL',file)
  check_structured(d.structured)
 for images in mapped_images.values():
  for image_url in images:
   assert image_url.startswith(expected+'/assets/photos/'),('Wrong image domain',image_url)
   assert (root/unquote(image_url[len(expected)+1:])).is_file(),('Missing sitemap image',image_url)
report={'html_pages':len(pages),'indexable_content_pages':len(known) if args.public else 0,'page_pairs':len(known)//2,'image_sitemap_pages':len(mapped_images),'image_sitemap_entries':sum(map(len,mapped_images.values())),'broken_links':0,'duplicate_titles':0,'duplicate_descriptions':0,'orphan_pages':0,'balanced_html':True,'reciprocal_hreflang':True,'browser_tested':False,'field_core_web_vitals':'not measured','delivery_tested':False}
print(json.dumps(report,indent=2))
