from pathlib import Path
from html import escape
import json, argparse, shutil, os, re
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
from html.parser import HTMLParser
from seo_content import CITIES, GUIDES
from content import ORIGIN, INSTAGRAM, NAME, ROUTES, UI, SERVICES, ALTS, FILMS, SOURCES
from booking import booking_dialog
from analytics import analytics_head
from motherhood_content import POSTPARTUM

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description='Build the Vicon Creator static website.')
parser.add_argument('--origin', default=ORIGIN, help='Full public site base URL, including a repository path if needed.')
parser.add_argument('--output', type=Path, default=ROOT/'dist')
indexing = parser.add_mutually_exclusive_group()
indexing.add_argument('--index', dest='index', action='store_true', help='Enable public indexing (the default).')
indexing.add_argument('--no-index', dest='index', action='store_false', help='Disable indexing for an intentional private preview.')
parser.set_defaults(index=True)
parser.add_argument('--portable', action='store_true', help='Use relative navigation and asset URLs.')
args = parser.parse_args()
ORIGIN = args.origin.rstrip('/')
origin_parts = urlsplit(ORIGIN)
if args.index and (origin_parts.scheme != 'https' or not origin_parts.hostname or 'example.' in origin_parts.hostname or origin_parts.hostname.endswith('.chatgpt.site')):
 parser.error('Public indexing requires the real HTTPS GitHub Pages URL or custom domain.')
DIST = args.output.resolve()
DIST.mkdir(parents=True, exist_ok=True)
if DIST != ROOT/'dist':
 shutil.copytree(ROOT/'dist/assets', DIST/'assets', dirs_exist_ok=True)
ASSETS = json.loads((ROOT/'src/assets.json').read_text())
PUBLIC_INDEXING = args.index
LANGS = ('en','nl')
PAGES = []
USED_IMAGES = set()

def e(s): return escape(str(s), quote=True)
def pick(values, lang): return values[LANGS.index(lang)]
def url(key, lang): return pick(ROUTES[key], lang)
def br(s): return e(s).replace('\n','<br>')
def arrow(): return '<span class="arrow" aria-hidden="true">↗&#xfe0e;</span>'
def link(key, label, lang, cls='text-link', session=''):
 booking=f' data-booking-open data-session="{e(session)}"' if key=='contact' else ''
 return f'<a class="{cls}" href="{url(key,lang)}"{booking}>{e(label)} {arrow()}</a>'
def photo(id, lang, cls='', eager=False, sizes='(max-width: 760px) 92vw, 48vw'):
 a=ASSETS[id];USED_IMAGES.add(id)
 alt=pick(ALTS.get(id,('Photograph by Viktoriia Loskutova','Foto door Viktoriia Loskutova')),lang)
 attrs='loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
 return f'<img class="{cls}" src="{a["src"]}" srcset="{a["small"]} {a["smallWidth"]}w, {a["src"]} {a["width"]}w" sizes="{sizes}" width="{a["width"]}" height="{a["height"]}" alt="{e(alt)}" {attrs} decoding="async">'

def language_switch(key,lang):
 return '<div class="language" aria-label="Language / Taal">'+''.join(f'<a href="{url(key,l)}" lang="{l}" hreflang="{l}" aria-current="{str(l==lang).lower()}" aria-label="{ "English" if l=="en" else "Nederlands" }">{l.upper()}</a>' for l in LANGS)+'</div>'

def header(key,lang):
 t=UI[lang]
 nav=''.join(f'<a href="{url(k,lang)}"'+(' aria-current="page"' if key==k else '')+f'>{e(t[v])}</a>' for k,v in [('portfolio','work'),('about','about'),('prices','prices')])
 cta=f'<a class="nav-cta" href="{url("contact",lang)}" data-booking-open>{e(pick(("Let’s talk","Plan je shoot"),lang))}</a>'
 return f'''<a class="skip" href="#main">{t['skip']}</a><header class="site-header wrap">
 <a class="brand" href="{url('home',lang)}" aria-label="Viktoriia Loskutova · Home"><span class="brand-main">Viktoriia Loskutova</span><span class="brand-sub">Vicon Creator · Photography</span></a>
 <nav class="desktop-nav" aria-label="{e(t['navigation'])}">{nav}{cta}</nav>
 <div class="header-actions">{language_switch(key,lang)}<button class="menu-button" aria-expanded="false" aria-controls="mobile-navigation">{t['menu']} <span aria-hidden="true">☰</span></button></div>
 <nav class="mobile-menu" id="mobile-navigation" aria-label="{e(t['navigation'])}">{nav}<a href="{url('contact',lang)}" data-booking-open>{t['contact']}</a>{language_switch(key,lang)}</nav></header>'''

def footer(lang):
 t=UI[lang]
 services=''.join(f'<a href="{url(k,lang)}">{e(pick(v["label"],lang))}</a>' for k,v in SERVICES.items())
 services+=f'<a href="{url("postpartum",lang)}">{pick(("Postpartum & baby","Kraamreportage & baby"),lang)}</a>'
 nav=''.join(f'<a href="{url(k,lang)}">{e(v)}</a>' for k,v in [('about',t['about']),('prices',t['prices']),('locations',t['locations']),('guides',pick(('Session guides','Fotoshoot tips'),lang)),('contact',pick(('Get in touch','Neem contact op'),lang))])
 return f'''<footer class="site-footer"><div class="footer-top"><div><a class="footer-brand" href="{url('home',lang)}">Viktoriia<br>Loskutova<span aria-hidden="true">.</span></a><p class="footer-caption">{pick(('Cinematic photographs.<br>For the way it felt.','Filmische foto’s.<br>Voor hoe het voelde.'),lang)}</p><p class="footer-caption">{t['base']}<br>{t['travel']}</p></div>
 <div><span class="footer-label">{t['services']}</span><nav class="footer-links" aria-label="{t['services']}">{services}</nav></div>
 <div><span class="footer-label">{t['navigation']}</span><nav class="footer-links" aria-label="{t['navigation']}">{nav}</nav></div>
 <div><span class="footer-label">{t['connect']}</span><div class="footer-links"><a href="{INSTAGRAM}" target="_blank" rel="noopener noreferrer">Instagram · @vicon.creator ↗</a></div></div></div>
 <div class="footer-bottom"><span>© 2026 {NAME} · {t['business']}</span><a href="{url('privacy',lang)}">{t['privacy']}</a></div></footer>'''

def breadcrumb(label,lang,portfolio=False):
 t=UI[lang]; middle=f'<span aria-hidden="true">/</span><a href="{url("portfolio",lang)}">{t["work"]}</a>' if portfolio else ''
 return f'<nav class="breadcrumbs" aria-label="{pick(("Breadcrumb","Kruimelpad"),lang)}"><a href="{url("home",lang)}">{t["home"]}</a>{middle}<span aria-hidden="true">/</span><span>{e(label)}</span></nav>'

def cta(lang):
 t=UI[lang]
 return f'<section class="cta-band wrap"><span class="eyebrow">{pick(("Your story, next","Jouw verhaal, hierna"),lang)}</span><h2>{br(t["cta"])}</h2><p>{e(t["ctaText"])}</p>{link("contact",t["contact"],lang,"button")}</section>'

def tabs(key,lang):
 return '<nav class="category-tabs" aria-label="'+UI[lang]['services']+'">'+''.join(f'<a href="{url(k,lang)}"'+(' aria-current="page"' if k==key else '')+f'>{e(pick(v["label"],lang))}</a>' for k,v in SERVICES.items())+'</nav>'

def cards(lang):
 return '<div class="portfolio-grid">'+''.join(f'<a class="portfolio-card" href="{url(k,lang)}"><div class="card-image">{photo(v["card"],lang,sizes="(max-width: 380px) calc(100vw - 36px), (max-width: 760px) 44vw, 29vw")}</div><div class="card-meta"><h3>{e(pick(v["label"],lang))}</h3><span>0{n+1}</span></div><p class="card-desc">{e(pick(v["tag"],lang))}</p></a>' for n,(k,v) in enumerate(SERVICES.items()))+'</div>'

def gallery(ids,lang,wide=(),two=False):
 t=UI[lang]
 figures=[]
 for i,id in enumerate(ids):
  cls='wide' if id in wide else ('contain' if id in ('kids-01','event-02') else '')
  figures.append(f'<figure class="{cls}"><button class="gallery-photo" data-lightbox data-full="{ASSETS[id]["src"]}" aria-label="{t["open"]}: {e(pick(ALTS[id],lang))}">{photo(id,lang,sizes="(max-width: 760px) 48vw, 50vw" if cls=="wide" else "(max-width: 760px) 44vw, 29vw")}</button><figcaption>{i+1:02d} <span aria-hidden="true">/</span> {e(pick(("A moment, kept","Een moment, bewaard"),lang))}</figcaption></figure>')
 return f'<div class="photo-gallery {"two" if two else ""}">'+''.join(figures)+'</div>'

def lightbox(lang):
 t=UI[lang]
 return f'<dialog class="lightbox" aria-label="{t["selected"]}"><div class="lightbox-inner"><span class="lb-counter" aria-live="polite"></span><button class="lb-close" aria-label="{t["close"]}">×</button><button class="lb-prev" aria-label="{t["prev"]}">‹</button><img alt=""><p class="lb-caption" aria-live="polite"></p><button class="lb-next" aria-label="{t["next"]}">›</button></div></dialog>'

def faq(items,lang):
 idx=0 if lang=='en' else 2;t=UI[lang]
 content=''.join(f'<details><summary>{e(x[idx])}</summary><p>{e(x[idx+1])}</p></details>' for x in items)
 return f'<section class="section faq wrap"><div class="faq-grid"><div><span class="eyebrow">{t["faqLabel"]}</span><h2>{br(t["faq"])}</h2></div><div class="faq-list">{content}</div></div></section>'

def films(names,lang):
 t=UI[lang]; fs=''
 for name in names:
  fs+=f'<figure class="film-card"><video controls muted playsinline preload="none" poster="/assets/films/{name}.jpg" aria-label="{e(pick(FILMS[name],lang))}"><source src="/assets/films/{name}.mp4" type="video/mp4"><a href="/assets/films/{name}.mp4">{e(pick(FILMS[name],lang))}</a></video><figcaption>{e(pick(FILMS[name],lang))}</figcaption></figure>'
 return f'<section class="section film-section wrap"><div class="gallery-intro"><div><span class="eyebrow">{t["filmLabel"]}</span><h2>{t["film"]}</h2></div><p>{t["filmNote"]}</p></div><div class="film-grid {"single" if len(names)==1 else ""}">{fs}</div></section>'

def page(key,lang,title,description,body,theme='cream',hero=None,service=None):
 u=ORIGIN+url(key,lang);t=UI[lang]
 alternates=''.join(f'<link rel="alternate" hreflang="{l}" href="{ORIGIN+url(key,l)}">' for l in LANGS)+f'<link rel="alternate" hreflang="x-default" href="{ORIGIN+url(key,"en")}">'
 org={'@type':'Organization','@id':ORIGIN+'/#business','name':'Vicon Creator','legalName':'Vicon Creator','url':ORIGIN+'/', 'founder':{'@id':ORIGIN+'/#photographer'},'identifier':{'@type':'PropertyValue','propertyID':'KVK','value':'97270725'},'areaServed':[{'@type':'Country','name':'Netherlands'},{'@type':'Country','name':'Belgium'}],'sameAs':[INSTAGRAM]}
 graph=[{'@type':'Person','@id':ORIGIN+'/#photographer','name':NAME,'url':ORIGIN+url('about',lang),'worksFor':{'@id':ORIGIN+'/#business'}},org,{'@type':'WebSite','@id':ORIGIN+'/#website','name':'Viktoriia Loskutova · Vicon Creator','url':ORIGIN+'/','inLanguage':['en','nl'],'publisher':{'@id':ORIGIN+'/#business'}},{'@type':'WebPage','@id':u+'#page','url':u,'name':title,'description':description,'inLanguage':lang,'isPartOf':{'@id':ORIGIN+'/#website'}}]
 if hero:
  image_url=ORIGIN+ASSETS[hero]['src']
  graph.append({'@type':'ImageObject','@id':u+'#main-image','contentUrl':image_url,'creator':{'@id':ORIGIN+'/#photographer'},'creditText':NAME,'copyrightNotice':'© '+NAME,'width':ASSETS[hero]['width'],'height':ASSETS[hero]['height']})
  next(n for n in graph if n.get('@type')=='WebPage')['primaryImageOfPage']={'@id':u+'#main-image'}
 if key!='home':graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':t['home'],'item':ORIGIN+url('home',lang)},{'@type':'ListItem','position':2,'name':title.split('|')[0].strip(),'item':u}]})
 if service:graph.append({'@type':'Service','name':pick(SERVICES[service]['seoLabel'],lang),'serviceType':pick(SERVICES[service]['label'],lang),'provider':{'@id':ORIGIN+'/#business'},'url':u,'areaServed':{'@type':'Country','name':'Netherlands'}})
 if key=='postpartum':graph.append({'@type':'Service','name':pick(('Postpartum and lifestyle newborn photography','Kraamreportage en lifestyle newborn fotografie'),lang),'serviceType':pick(('Postpartum photography','Kraamreportage'),lang),'provider':{'@id':ORIGIN+'/#business'},'url':u,'areaServed':{'@type':'Country','name':'Netherlands'}})
 preload=f'<link rel="preload" as="image" href="{ASSETS[hero]["src"]}" imagesrcset="{ASSETS[hero]["small"]} {ASSETS[hero]["smallWidth"]}w, {ASSETS[hero]["src"]} {ASSETS[hero]["width"]}w" imagesizes="{ "100vw" if key=="home" else "(max-width: 760px) 92vw, 48vw" }">' if hero else ''
 verification=os.environ.get('GOOGLE_SITE_VERIFICATION','').strip()
 verification_meta=f'<meta name="google-site-verification" content="{e(verification)}">' if verification else ''
 robots='index, follow, max-image-preview:large' if PUBLIC_INDEXING else 'noindex, follow'
 text=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="{robots}"><meta name="author" content="{e("Vicon Creator" if key in GUIDES else NAME)}">{verification_meta}<meta name="theme-color" content="#20271f"><link rel="canonical" href="{u}">{alternates}<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{u}"><meta property="og:site_name" content="Vicon Creator"><meta property="og:locale" content="{ 'en_GB' if lang=='en' else 'nl_NL' }"><link rel="icon" href="/favicon.svg" type="image/svg+xml">{preload}<link rel="stylesheet" href="/assets/fonts/fonts.css"><link rel="stylesheet" href="/assets/site.css"><script src="/assets/site.js" defer></script><script type="module" src="/assets/booking.mjs"></script><script type="application/ld+json">{json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('</','<\\/')}</script>{analytics_head()}</head><body data-theme="{theme}" data-session="{service or ("postpartum" if key=="postpartum" else "")}">{header(key,lang)}<main id="main">{body}</main>{footer(lang)}{lightbox(lang)}{booking_dialog(lang)}</body></html>'''
 path=DIST/url(key,lang).strip('/')/'index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
 PAGES.append({'key':key,'lang':lang,'url':u,'path':str(path.relative_to(DIST)),'title':title})

def home(lang):
 t=UI[lang]
 hero_title=pick(('A feeling.<em>Kept forever.</em>','Een gevoel.<em>Voor altijd.</em>'),lang)
 hero_text=pick(('Cinematic photography for the people, places and moments you want to hold on to.','Filmische fotografie voor de mensen, plekken en momenten die je wilt vasthouden.'),lang)
 intro=pick(('Life moves.\nPhotographs let\nus stay a little.','Het leven gaat door.\nEen foto laat ons\neven blijven.'),lang)
 introtext=pick(('I’m Viktoriia, the photographer behind Vicon Creator. I photograph weddings, love stories, portraits and the chapters in between. With warm light, thoughtful colour and a little direction, we create something that feels like you.','Ik ben Viktoriia, de fotograaf achter Vicon Creator. Ik fotografeer bruiloften, liefdesverhalen, portretten en de hoofdstukken daartussen. Met warm licht, zorgvuldige kleuren en een beetje richting maken we iets dat bij jou past.'),lang)
 journey_titles=pick((['Tell me your story','Be in the moment','Keep the feeling'],['Vertel je verhaal','Blijf in het moment','Bewaar het gevoel']),lang)
 journey_text=pick((['Share what you’re planning, where and when. We’ll talk about the atmosphere, the practical details and the right session for you.','We’ll make space for natural moments, with guidance when you need it. You can move, laugh, take a breath and simply be yourself.','A thoughtful selection and a consistent edit bring the photographs together. Your delivery details are agreed before the shoot.'],['Deel wat je van plan bent, waar en wanneer. We bespreken de sfeer, de praktische details en de sessie die bij je past.','Er is ruimte voor spontane momenten, met begeleiding wanneer je die nodig hebt. Je mag bewegen, lachen, ademhalen en jezelf zijn.','Een doordachte selectie en een samenhangende bewerking brengen de foto’s bij elkaar. De levering spreken we vóór de shoot af.']),lang)
 journey=''.join(f'<div class="journey-item"><span class="step">0{i+1}</span><h3>{e(journey_titles[i])}</h3><p>{e(journey_text[i])}</p></div>' for i in range(3))
 body=f'''<section class="home-hero">{photo('lovestory-06',lang,eager=True,sizes='100vw')}<div class="hero-content wrap"><div class="hero-topline"><span>{pick(('Cinematic photography','Filmische fotografie'),lang)}</span><span>{pick(('The Netherlands<br>& wherever your story goes','Nederland<br>& waar jouw verhaal je brengt'),lang)}</span></div><div class="hero-bottom"><h1 class="hero-title">{hero_title}</h1><div class="hero-note"><p>{hero_text}</p>{link('portfolio',pick(('Discover the work','Ontdek het werk'),lang),lang)}</div></div></div><span class="hero-credit">Viktoriia Loskutova · Vicon Creator</span></section>
 <section class="section wrap intro-grid"><div class="intro-aside"><span class="eyebrow">{pick(('Photography with feeling','Fotografie met gevoel'),lang)}</span><p class="intro-caption">{pick(('Wedding, couples & portrait photographer<br>Based in the Netherlands','Trouw-, loveshoot- & portretfotograaf<br>Vanuit Nederland'),lang)}</p></div><div><h2>{br(intro)}</h2><div class="body-copy"><p>{introtext}</p>{link('about',pick(('Meet your photographer','Maak kennis met mij'),lang),lang)}</div></div></section>
 <section class="wrap section" style="padding-top:0"><div class="section-heading"><div><span class="eyebrow">{pick(('Six ways to tell a story','Zes manieren om een verhaal te vertellen'),lang)}</span><h2>{pick(('The work.','Het werk.'),lang)}</h2>{link('portfolio',pick(('View all work','Bekijk alles'),lang),lang)}</div></div>{cards(lang)}</section>
 <div class="marquee-static wrap"><span>{pick(('Honest moments','Oprechte momenten'),lang)}</span><span>{pick(('Cinematic light','Filmisch licht'),lang)}</span><span>{pick(('Thoughtful colour','Zorgvuldige kleuren'),lang)}</span><span>{pick(('A feeling that stays','Een gevoel dat blijft'),lang)}</span></div>
 <section class="section about-strip wrap"><div class="about-photo">{photo('me-02',lang)}</div><div class="about-copy"><span class="eyebrow">{pick(('The person behind the camera','De persoon achter de camera'),lang)}</span><h2>{pick(('Hi, I’m Viktoriia.<br><em>I notice the little things.</em>','Hoi, ik ben Viktoriia.<br><em>Ik zie de kleine dingen.</em>'),lang)}</h2><p>{pick(('The light falling across a face. A look that lasts a second. The closeness you forget anyone else can see. These are the things I look for — and the things I want you to recognise in your photographs.','Het licht dat over een gezicht valt. Een blik die een seconde duurt. De nabijheid waarvan je vergeet dat anderen die kunnen zien. Daar zoek ik naar — en dat wil ik je laten herkennen in je foto’s.'),lang)}</p>{link('about',pick(('A little more about me','Meer over mij'),lang),lang)}<div class="signature">Viktoriia</div></div></section>
 <section class="quote-band"><div class="wrap"><p>{pick(('Remember the light.<br><em>Keep the feeling.</em>','Herinner het licht.<br><em>Bewaar het gevoel.</em>'),lang)}</p></div></section>
 <section class="section wrap"><span class="eyebrow">{pick(('Making photographs together','Samen foto’s maken'),lang)}</span><h2>{br(t['process'])}</h2><div class="journey">{journey}</div></section>
 <section class="section region-block wrap"><div><span class="eyebrow">{t['locations']}</span><h2>{pick(('Close to home.<br>Open to elsewhere.','Dicht bij huis.<br>Open voor verder weg.'),lang)}</h2></div><div><p>{pick(('Based in the Netherlands, I work across Amsterdam, The Hague, Rotterdam, Utrecht, Delft and the rest of the Netherlands. For a celebration in Belgium or elsewhere in Europe, let’s talk about the journey.','Vanuit Nederland werk ik in Amsterdam, Den Haag, Rotterdam, Utrecht, Delft en de rest van Nederland. Voor een viering in België of elders in Europa bespreken we samen de reis.'),lang)}</p><div class="region-links">{link('amsterdam',pick(('Weddings in Amsterdam','Trouwen in Amsterdam'),lang),lang)}{link('the-hague',pick(('Love stories in The Hague','Loveshoot in Den Haag'),lang),lang)}{link('locations',pick(('Across the Netherlands','Door heel Nederland'),lang),lang)}{link('belgium',pick(('Weddings in Belgium','Trouwen in België'),lang),lang)}</div></div></section>{cta(lang)}'''
 page('home',lang,pick(('Viktoriia Loskutova | Cinematic Photographer Netherlands','Viktoriia Loskutova | Filmische fotograaf Nederland'),lang),pick(('Wedding, couples, portrait, maternity, postpartum, family and event photography by Vicon Creator. Based in the Netherlands, photographing stories across the Netherlands.','Trouwfoto’s, loveshoots, portretten, zwangerschapsfoto’s, kraamreportages en gezins- en evenementenfotografie door Vicon Creator. Vanuit Nederland, door heel Nederland.'),lang),body,hero='lovestory-06')

def motherhood_chapters(lang):
 return f'''<section class="section wrap motherhood-chapters"><div><span class="eyebrow">01 · {pick(('Maternity','Zwangerschap'),lang)}</span><h2>{pick(('Before we meet.','Voor de eerste ontmoeting.'),lang)}</h2><p>{pick(('Pregnancy portraits outdoors or in a familiar indoor space. We plan the light, clothing and movement around what feels comfortable to you.','Zwangerschapsportretten buiten of op een vertrouwde binnenlocatie. Licht, kleding en beweging stemmen we af op wat voor jou prettig voelt.'),lang)}</p>{link('contact',pick(('Plan maternity photographs','Plan zwangerschapsfoto’s'),lang),lang,session='maternity')}</div><div><span class="eyebrow">02 · {pick(('Postpartum','Kraamtijd'),lang)}</span><h2>{pick(('Now you are here.','Nu je er bent.'),lang)}</h2><p>{pick(('Life with your baby: holding, feeding and the quiet moments in between. Explore the postpartum photographs and how a relaxed session at home can work.','Het leven met jullie baby: vasthouden, voeden en de rustige momenten ertussen. Bekijk de kraamfoto’s en lees hoe een ontspannen sessie thuis kan verlopen.'),lang)}</p>{link('postpartum',pick(('Discover postpartum photography','Ontdek de kraamreportage'),lang),lang)}</div></section>'''

def postpartum(lang):
 v=POSTPARTUM;t=UI[lang]
 body=f'''<div class="wrap page-top">{breadcrumb(pick(('Postpartum & baby','Kraamreportage & baby'),lang),lang,True)}<section class="collection-hero"><div class="collection-title"><span class="eyebrow">{pick(('Motherhood · Postpartum & lifestyle newborn photography','Moederschap · Kraamreportage & lifestyle newborn fotografie'),lang)}</span><h1>{br(pick(v['heading'],lang))}</h1><p class="lede">{e(pick(v['intro'],lang))}</p><div class="button-row">{link('contact',pick(('Plan your session','Plan jullie sessie'),lang),lang,'button','postpartum')}{link('maternity',pick(('All Motherhood photographs','Alle moederschapsfoto’s'),lang),lang)}</div></div><figure class="collection-visual">{photo('motherhood-07',lang,eager=True)}<figcaption>Motherhood · Vicon Creator</figcaption></figure></section>{tabs('maternity',lang)}</div>'''
 body+=f'<section class="section wrap"><div class="gallery-intro"><div><span class="eyebrow">{t["selected"]}</span><h2>{pick(("Your little world.","Jullie kleine wereld."),lang)}</h2></div><p>{pick(("Postpartum portraits, feeding and the details of being together.","Portretten na de geboorte, voedingsmomenten en de details van het samenzijn."),lang)}</p></div>{gallery(v["gallery"],lang)}</section>'
 for headings,paragraphs in v['sections']:
  body+=f'<section class="wrap section service-details postpartum-copy"><h2>{e(pick(headings,lang))}</h2><p>{e(pick(paragraphs,lang))}</p></section>'
 body+=faq(v['faq'],lang)
 body+=f'<section class="section wrap"><div class="region-links">{link("guide-outfits",pick(("What to wear","Wat trek je aan?"),lang),lang)}{link("maternity",pick(("Maternity & Motherhood","Zwangerschap & moederschap"),lang),lang)}{link("family",pick(("Family photographs","Gezinsfoto’s"),lang),lang)}{link("contact",pick(("Ask for a postpartum proposal","Vraag een voorstel voor een kraamreportage"),lang),lang,session="postpartum")}</div></section>'
 page('postpartum',lang,pick(v['title'],lang),pick(v['description'],lang),body,'rose','motherhood-07')

def collection(key,lang):
 v=SERVICES[key];t=UI[lang];label=pick(v['label'],lang)
 landscape=' landscape' if key=='couples' else ''
 body=f'<div class="wrap page-top">{breadcrumb(label,lang,True)}<section class="collection-hero{landscape}"><div class="collection-title"><span class="eyebrow">{e(pick(v["seoLabel"],lang))}</span><h1>{br(pick(v["heading"],lang))}</h1><p class="lede">{e(pick(v["intro"],lang))}</p><div class="button-row">{link("contact",t["enquire"],lang,"button",key)}{link("prices",t["prices"],lang)}</div></div><figure class="collection-visual">{photo(v["hero"],lang,eager=True)}<figcaption><span>{label} · Vicon Creator</span><span>{pick(("A selected frame","Een geselecteerd beeld"),lang)}</span></figcaption></figure></section>{tabs(key,lang)}</div>'
 if key=='maternity':body+=motherhood_chapters(lang)
 if v['gallery']:
  body+=f'<section class="section wrap"><div class="gallery-intro"><div><span class="eyebrow">{t["selected"]}</span><h2>{t["gallery"]}</h2></div><p>{e(pick(v["galleryIntro"],lang))}</p></div>{gallery(v["gallery"],lang,v.get("wide",()),two=len(v["gallery"])==2)}</section>'
 items=''.join(f'<li>{e(x)}</li>' for x in pick(v['includes'],lang))
 body+=f'<section class="section service-details wrap"><div><span class="eyebrow">{t["experience"]}</span><h2>{br(t["approach"])}</h2><p>{e(pick(v["body"],lang))}</p><p class="muted">{e(pick(v["body2"],lang))}</p></div><div><span class="eyebrow">{t["included"]}</span><ul class="detail-list">{items}</ul><p class="price-teaser">{v["price"] if lang=="en" else v["price"].replace(",", ".")} <small>· {t["guide"]}</small></p><p class="price-note">{e(pick(v["unit"],lang))}<br>{t["guideNote"]}</p>{link("prices",t["investmentLink"],lang)}</div></section>'
 if v.get('films'):body+=films(v['films'],lang)
 body+=faq(v['faq'],lang)
 body+=related_reading(lang,service=key)
 if key=='weddings':body+=f'<div class="wrap region-links" style="padding-bottom:70px">{link("amsterdam",pick(("Wedding photographer Amsterdam","Trouwfotograaf Amsterdam"),lang),lang)}{link("belgium",pick(("Wedding photography in Belgium","Trouwfotografie in België"),lang),lang)}</div>'
 if key=='couples':body+=f'<div class="wrap" style="padding-bottom:70px">{link("the-hague",pick(("Plan a love story in The Hague","Plan een loveshoot in Den Haag"),lang),lang)}</div>'
 keys=list(SERVICES);i=keys.index(key);prev=keys[(i-1)%len(keys)];nxt=keys[(i+1)%len(keys)]
 body+=f'<nav class="collection-pagination wrap" aria-label="{t["services"]}"><a href="{url(prev,lang)}"><small>{t["previousCollection"]}</small>{e(pick(SERVICES[prev]["label"],lang))}</a><a href="{url(nxt,lang)}"><small>{t["nextCollection"]}</small>{e(pick(SERVICES[nxt]["label"],lang))} →</a></nav>{cta(lang)}'
 page(key,lang,pick(v['title'],lang),pick(v['description'],lang),body,v['theme'],v['hero'],key)

def portfolio(lang):
 t=UI[lang]
 body=f'<div class="wrap page-top">{breadcrumb(t["work"],lang)}<section class="page-heading"><span class="eyebrow">Viktoriia Loskutova · Photography</span><h1>{pick(("Different chapters.<br><em>The same feeling.</em>","Andere hoofdstukken.<br><em>Hetzelfde gevoel.</em>"),lang)}</h1><p class="lede">{pick(("Weddings, love stories, portraits, motherhood, childhood and the evenings that bring us together. Choose a chapter and take a closer look.","Bruiloften, liefdesverhalen, portretten, moederschap, kindertijd en de avonden die ons samenbrengen. Kies een hoofdstuk en kijk verder."),lang)}</p></section>{cards(lang)}<div style="height:80px"></div></div>{cta(lang)}'
 page('portfolio',lang,pick(('Photography portfolio | Viktoriia Loskutova · Vicon Creator','Fotografieportfolio | Viktoriia Loskutova · Vicon Creator'),lang),pick(('Explore cinematic wedding, couples, portrait, maternity, family and event photographs by Viktoriia Loskutova, Vicon Creator in the Netherlands.','Bekijk filmische trouwfoto’s, loveshoots, portretten, zwangerschapsfoto’s, gezins- en evenementenfotografie van Viktoriia Loskutova, Vicon Creator.'),lang),body)

def about(lang):
 t=UI[lang]
 body=f'''<div class="wrap page-top">{breadcrumb(t['about'],lang)}<section class="about-hero"><div><span class="eyebrow">{pick(('Meet your photographer','Maak kennis met je fotograaf'),lang)}</span><h1>Viktoriia<br><em>Loskutova.</em></h1><p class="lede">{pick(('The photographer behind Vicon Creator. Based in the Netherlands, following stories across the Netherlands and beyond.','De fotograaf achter Vicon Creator. Vanuit Nederland volg ik verhalen door Nederland en daarbuiten.'),lang)}</p><p>{pick(('My work brings together honest connection and a cinematic eye. I’m drawn to expressive light, natural movement and the small gestures that make a photograph feel personal.','In mijn werk komen oprechte verbinding en een filmische blik samen. Ik zoek expressief licht, natuurlijke beweging en de kleine gebaren die een foto persoonlijk maken.'),lang)}</p>{link('contact',pick(('Let’s get to know each other','Laten we kennismaken'),lang),lang)}</div><div class="image-stack">{photo('me-02',lang,'main-portrait',True)}{photo('me-01',lang,'small-portrait')}</div></section></div>
 <section class="section about-story wrap"><div><span class="eyebrow">{pick(('How I see it','Hoe ik het zie'),lang)}</span><h2>{pick(('A photograph<br>should feel<br><em>like something.</em>','Een foto<br>mag iets<br><em>laten voelen.</em>'),lang)}</h2></div><div class="story-body"><p>{pick(('Beautiful light matters. So does the person standing in it. My approach gives both room: an intentional composition, a little guidance, and enough freedom for something unplanned to happen.','Mooi licht doet ertoe. De persoon die erin staat ook. Mijn aanpak geeft beide ruimte: een bewuste compositie, een beetje begeleiding en genoeg vrijheid voor iets onverwachts.'),lang)}</p><p>{pick(('I photograph weddings and couples, individual portraits, maternity and postpartum, children, families and events. The pace changes with each session, but the attention stays the same. I look for photographs with atmosphere and a clear sense of the people in them.','Ik fotografeer bruiloften en koppels, individuele portretten, zwangerschappen en de kraamtijd, kinderen, gezinnen en evenementen. Het tempo verandert per sessie, maar de aandacht blijft hetzelfde. Ik zoek beelden met sfeer en een duidelijk gevoel voor de mensen erin.'),lang)}</p><p>{pick(('Editing is part of that vision. Warm colour, considered contrast and expressive black and white help the photographs belong together, while keeping the feeling of the moment.','Bewerking hoort bij die visie. Warme kleuren, zorgvuldig contrast en expressief zwart-wit brengen samenhang in de foto’s, terwijl het gevoel van het moment blijft.'),lang)}</p><div class="signature">Viktoriia</div></div></section>
 <div class="wide-interlude">{photo('lovestory-09',lang,sizes='100vw')}</div>
 <section class="section wrap"><div class="section-heading"><div><span class="eyebrow">{pick(('Find your chapter','Vind jouw hoofdstuk'),lang)}</span><h2>{pick(('What shall we make?','Wat gaan we maken?'),lang)}</h2></div></div><div class="region-links">{''.join(link(k,pick(v['label'],lang),lang) for k,v in SERVICES.items())}</div></section>{cta(lang)}'''
 page('about',lang,pick(('About Viktoriia Loskutova | Vicon Creator photographer','Over Viktoriia Loskutova | Fotograaf Vicon Creator'),lang),pick(('Meet Viktoriia Loskutova, the photographer behind Vicon Creator. Cinematic wedding and lifestyle photography, based in the Netherlands and working across the Netherlands.','Maak kennis met Viktoriia Loskutova, de fotograaf achter Vicon Creator. Filmische trouw- en lifestylefotografie vanuit Nederland, door heel Nederland.'),lang),body,hero='me-02')

def prices(lang):
 t=UI[lang]
 head=pick(('Photographs to keep.\nAn investment in feeling.','Foto’s om te bewaren.\nEen waardevol gevoel.'),lang)
 lead=pick(('A starting point for planning your session. These are provisional guide prices; your collection and final total will be confirmed in a personal proposal.','Een startpunt voor het plannen van je sessie. Dit zijn voorlopige richtprijzen. De inhoud en definitieve totaalprijs bevestigen we in een persoonlijk voorstel.'),lang)
 names=pick((['The intimate day','The full story','A little longer'],['De intieme dag','Het hele verhaal','Nog wat langer']),lang)
 rates=pick((['€2,200','€2,750','€3,250'],['€2.200','€2.750','€3.250']),lang);hours=[6,8,10]
 descriptions=pick((['For a ceremony, portraits and the moments around them.','Room for more of the day, from one chapter to the next.','More space for preparations, the celebration and the evening.'],['Voor de ceremonie, portretten en de momenten eromheen.','Ruimte voor meer van de dag, van het ene hoofdstuk naar het volgende.','Meer ruimte voor de voorbereidingen, het feest en de avond.']),lang)
 includes=pick((['Pre-wedding planning conversation','Carefully edited photographs','High-resolution digital delivery','Final selection and timing by agreement'],['Voorbespreking van jullie trouwdag','Zorgvuldig bewerkte foto’s','Digitale levering in hoge resolutie','Selectie en levertermijn in overleg']),lang)
 grid=''
 for i in range(3):
  grid+=f'<article class="price-card {"featured" if i==1 else ""}"><span class="eyebrow">{pick(("Wedding collection","Trouwcollectie"),lang)} 0{i+1}</span><h2>{names[i]}</h2><span class="duration">{hours[i]} {pick(("hours of photography","uur fotografie"),lang)}</span><div class="price">{rates[i]}</div><span class="duration">{t["guide"]}</span><p>{descriptions[i]}</p><ul>'+''.join(f'<li>{x}</li>' for x in includes)+f'</ul>{link("contact",pick(("Ask about your day","Vraag jullie datum aan"),lang),lang)}</article>'
 rows=''
 for key in ['couples','portraits','maternity','family','events']:
  v=SERVICES[key]
  rows+=f'<div class="price-row"><h3><a href="{url(key,lang)}">{e(pick(v["label"],lang))}</a></h3><span class="session-duration">{e(pick(v["unit"],lang))}</span><span class="row-price">{v["price"]}</span>{link(key,pick(("Details","Meer info"),lang),lang)}</div>'
 rows+=f'<div class="price-row"><h3><a href="{url("postpartum",lang)}">{pick(("Postpartum & baby","Kraamreportage & baby"),lang)}</a></h3><span class="session-duration">{pick(("Duration and collection agreed around your family","Duur en collectie afgestemd op jullie gezin"),lang)}</span><span class="row-price quote-price">{pick(("On request","Op aanvraag"),lang)}</span>{link("contact",pick(("Ask for a quote","Vraag een voorstel"),lang),lang,session="postpartum")}</div>'
 body=f'''<div class="wrap page-top">{breadcrumb(t['prices'],lang)}<section class="page-heading"><span class="eyebrow">{pick(('Photography collections · Guide prices','Fotografiecollecties · Richtprijzen'),lang)}</span><h1>{br(head)}</h1><p class="lede">{lead}</p></section><div class="price-grid">{grid}</div><section class="section session-prices"><div class="section-heading"><div><span class="eyebrow">{pick(('For every other chapter','Voor ieder ander hoofdstuk'),lang)}</span><h2>{pick(('Your session.','Jouw fotoshoot.'),lang)}</h2></div></div>{rows}<div style="height:35px"></div><p class="pricing-note">{pick(('All amounts are in euros and are indicative, not confirmed booking offers. The final total, including any applicable VAT, travel, studio or venue costs and usage licence, will be stated before you book. Albums, additional hours and special production requirements can be discussed separately.','Alle bedragen zijn in euro’s en zijn indicatief; het zijn geen definitieve boekingsaanbiedingen. De totaalprijs, inclusief eventuele btw, reiskosten, studio- of locatiekosten en gebruikslicentie, wordt vóór de boeking vermeld. Albums, extra uren en bijzondere productievragen bespreken we apart.'),lang)}</p></section></div>'''
 qs=[('Why are the prices marked as provisional?','They are planning estimates for the current collections. A personal proposal confirms exactly what is included and the full price for your date and location.','Waarom zijn de tarieven voorlopig?','Het zijn planningsindicaties voor de huidige collecties. Een persoonlijk voorstel bevestigt precies wat is inbegrepen en wat de totaalprijs is voor jouw datum en locatie.'),('Are travel and studio hire included?','Any travel, accommodation, studio or location costs will be discussed and included in the final total before you commit to booking.','Zijn reiskosten en studiohuur inbegrepen?','Eventuele reis-, overnachtings-, studio- en locatiekosten bespreken we en nemen we op in de totaalprijs voordat je boekt.'),('How do I book?','Open the enquiry form and choose your session, preferred date and contact method. Share the location when we discuss your plans. We’ll discuss your ideas and confirm the scope, price, delivery and booking terms together.','Hoe boek ik?','Open het aanvraagformulier en kies je fotoshoot, gewenste datum en contactmethode. Deel de locatie wanneer we je plannen bespreken. We bespreken je ideeën en bevestigen samen de inhoud, prijs, levering en boekingsvoorwaarden.')]
 body+=faq(qs,lang)+cta(lang)
 page('prices',lang,pick(('Photography prices Netherlands | Weddings & sessions','Fotografie tarieven Nederland | Bruiloften & fotoshoots'),lang),pick(('Explore guide prices for cinematic wedding photography, couples, portraits, maternity, family and events with Viktoriia Loskutova in the Netherlands.','Bekijk richtprijzen voor filmische trouwfotografie, loveshoots, portretten, zwangerschapsfoto’s, gezins- en evenementenfotografie door Viktoriia Loskutova.'),lang),body)

def contact(lang):
 t=UI[lang]
 checklist=pick(([('The chapter','A wedding, love story, portrait, maternity or postpartum session, family photographs or an event.'),('The when & where','Your preferred date, city or venue. A rough idea is welcome too.'),('What you have in mind','The atmosphere, the people involved and anything you want me to know.')],[('Het hoofdstuk','Een bruiloft, loveshoot, portret, zwangerschapsshoot of kraamreportage, gezinsfoto’s of een evenement.'),('Het moment & de plek','Je gewenste datum, stad of locatie. Een globaal idee is ook welkom.'),('Wat je voor ogen hebt','De sfeer, wie erbij zijn en alles wat je me wilt vertellen.')]),lang)
 lis=''.join(f'<li><span class="number">0{i+1}</span><div><strong>{e(a)}</strong><p>{e(b)}</p></div></li>' for i,(a,b) in enumerate(checklist))
 body=f'''<div class="wrap page-top">{breadcrumb(pick(('Contact','Contact'),lang),lang)}<section class="page-heading"><span class="eyebrow">{pick(('It begins with a conversation','Het begint met een gesprek'),lang)}</span><h1>{pick(('Tell me<br><em>your story.</em>','Vertel me<br><em>jouw verhaal.</em>'),lang)}</h1><p class="lede">{pick(('A whole plan or just the beginning of an idea — I’d love to hear it. Send an enquiry and choose how you’d like me to reply.','Een compleet plan of het begin van een idee — ik hoor het graag. Stuur een aanvraag en kies hoe je graag een reactie ontvangt.'),lang)}</p></section><section class="contact-grid">{photo('lovestory-24',lang,'contact-photo',True)}<div class="contact-card"><span class="eyebrow">Viktoriia Loskutova · Vicon Creator</span><h2>{pick(('Let’s make it<br><em>feel like you.</em>','Laten we iets maken<br><em>dat bij jou past.</em>'),lang)}</h2><p>{pick(('These details help us plan your session:','Deze informatie helpt ons je sessie te plannen:'),lang)}</p><ol class="contact-checklist">{lis}</ol>{link("contact",pick(("Open booking form","Open het aanvraagformulier"),lang),lang,"button")}<p class="price-note" style="margin-top:15px">{pick(('Choose your session, preferred date and contact method.','Kies je fotoshoot, gewenste datum en contactmethode.'),lang)}</p><div class="business-details">{t['base']}<br>{t['travel']}<br>Vicon Creator · KVK 97270725</div></div></section></div>'''
 page('contact',lang,pick(('Contact Viktoriia Loskutova | Book a photography session','Contact Viktoriia Loskutova | Fotoshoot aanvragen'),lang),pick(('Enquire about wedding photography or a couples, portrait, maternity, family or event session in the Netherlands. Choose your session, date and preferred contact method.','Vraag trouwfotografie of een loveshoot, portret-, zwangerschaps-, gezins- of evenementensessie in Nederland aan. Neem contact op met Vicon Creator.'),lang),body,hero='lovestory-24')

def locations(lang):
 t=UI[lang]
 blocks=pick(([
  ('Amsterdam','Canal-side walks, quieter streets and an urban rhythm. An Amsterdam session can feel intimate with a small route and time to pause.'),
  ('The Hague & the coast','A city setting, somewhere familiar or time towards the coast. The variety of settings makes this a natural place to start planning.'),
  ('Rotterdam & Delft','From a stronger architectural backdrop to a quieter walk together, we can build the route around your preferred pace and mood.'),
  ('Utrecht & the rest of the Netherlands','Your story may belong close to home. Tell me the place you have in mind and we’ll discuss timing, travel and the right approach.')
 ],[
  ('Amsterdam','Wandelingen langs de grachten, rustigere straten en het ritme van de stad. Met een korte route en tijd om stil te staan kan een shoot heel intiem voelen.'),
  ('Den Haag & de kust','De stad, een vertrouwde omgeving of een plek richting de kust. De verschillende omgevingen bieden een mooi begin voor het plannen van een sessie.'),
  ('Rotterdam & Delft','Van een krachtige architecturale achtergrond tot een rustige wandeling samen. We bouwen de route rond jullie gewenste tempo en sfeer.'),
  ('Utrecht & de rest van Nederland','Je verhaal kan juist dicht bij huis passen. Vertel welke plek je voor ogen hebt, dan bespreken we het moment, de reis en de aanpak.')
 ]),lang)
 dest=''.join(f'<article class="destination-card"><h2>{e(a)}</h2><p>{e(b)}</p>{link("contact",pick(("Plan a session here","Plan hier je shoot"),lang),lang)}</article>' for a,b in blocks)
 body=f'''<div class="wrap page-top">{breadcrumb(t['locations'],lang)}<section class="destination-intro"><div><span class="eyebrow">{pick(('Photographer in the Netherlands','Fotograaf in Nederland'),lang)}</span><h1>{pick(('A place.<br><em>Your kind of feeling.</em>','Een plek.<br><em>Jouw soort gevoel.</em>'),lang)}</h1><p class="lede">{pick(('Based in the Netherlands, photographing weddings, couples, portraits, maternity, children, families and events throughout the Netherlands.','Vanuit Nederland fotografeer ik bruiloften, koppels, portretten, zwangerschappen, kinderen, gezinnen en evenementen door heel Nederland.'),lang)}</p><p>{pick(('The location is part of the story. We’ll choose it for the light, the atmosphere and the way you want the session to feel — then agree the practical details and travel before booking.','De locatie hoort bij het verhaal. We kiezen haar vanwege het licht, de sfeer en hoe de sessie moet voelen. Daarna spreken we de praktische details en reis af vóór de boeking.'),lang)}</p>{link('contact',t['enquire'],lang,'button')}</div>{photo('lovestory-07',lang,eager=True)}</section><section class="destination-cards">{city_links(lang)}</section><section class="section"><span class="eyebrow">{pick(('A little more inspiration','Meer inspiratie'),lang)}</span><div class="region-links">{link('amsterdam',pick(('Wedding photographer Amsterdam','Trouwfotograaf Amsterdam'),lang),lang)}{link('the-hague',pick(('Couples photographer The Hague','Loveshoot Den Haag'),lang),lang)}{link('belgium',pick(('Wedding photographer Belgium','Trouwfotograaf België'),lang),lang)}{link('portfolio',t['all'],lang)}</div></section></div>{cta(lang)}'''
 page('locations',lang,pick(('Photographer Netherlands | Amsterdam, The Hague & more','Fotograaf Nederland | Amsterdam, Den Haag & meer'),lang),pick(('Vicon Creator photography across the Netherlands: Amsterdam, The Hague, Rotterdam, Delft and Utrecht. Weddings, couples, portraits, family and events.','Vicon Creator fotografeert door heel Nederland: Amsterdam, Den Haag, Rotterdam, Delft en Utrecht. Bruiloften, loveshoots, portretten, gezinnen en evenementen.'),lang),body,hero='lovestory-07')

def destination(key,lang):
 t=UI[lang]
 data={
 'amsterdam':{
  'title':('Wedding photographer Amsterdam | Viktoriia Loskutova','Trouwfotograaf Amsterdam | Viktoriia Loskutova'),
  'desc':('Cinematic wedding photography in Amsterdam by Vicon Creator. Plan a relaxed portrait route, natural moments and coverage that fits your wedding day.','Filmische trouwfotografie in Amsterdam door Vicon Creator. Plan een ontspannen portretroute, natuurlijke momenten en een reportage die bij jullie dag past.'),
  'h1':('Wedding photographer\nin Amsterdam.','Trouwfotograaf\nin Amsterdam.'),'hero':'wedding-18','theme':'cream','service':'weddings',
  'intro':('A city wedding, with room for the two of you. Cinematic photographs of the people, the light and the moments that make the day yours.','Een bruiloft in de stad, met ruimte voor jullie twee. Filmische foto’s van de mensen, het licht en de momenten die de dag van jullie maken.'),
  'sections':[
   ('Let the day lead the photographs.','For an Amsterdam wedding, the most useful starting point is your timeline: where the ceremony happens, how you move between places and when you want to spend time with your guests. We can plan a short portrait route nearby, keeping space for quiet moments without making photography the whole schedule.','Laat de dag de foto’s leiden.','Bij een Amsterdamse bruiloft beginnen we met jullie planning: waar de ceremonie is, hoe jullie tussen locaties reizen en wanneer jullie bij de gasten willen zijn. We kunnen een korte portretroute in de buurt plannen, met ruimte voor rustige momenten zonder de hele dag om fotografie te laten draaien.'),
   ('A portrait plan that fits the city.','Tell me whether you imagine canal-side portraits, a simple urban walk or staying close to your venue. We’ll discuss light, walking distances, crowds and an indoor alternative. Any access permissions or venue requirements are checked as part of planning; a landmark does not need to be the centre of every photograph.','Een portretplan dat bij de stad past.','Vertel of jullie portretten langs de grachten, een korte stadswandeling of foto’s dicht bij de locatie voor ogen hebben. We bespreken het licht, loopafstanden, drukte en een binnenalternatief. Toegang en locatievoorwaarden nemen we mee in de planning. Niet iedere foto hoeft om een herkenbare plek te draaien.'),
   ('Start with the moments that matter.','The provisional wedding collections begin at €2,200 for six hours. Longer coverage can make room for preparations or the evening. Share your date and locations for a personal proposal with the final total, travel details and delivery agreed in advance.','Begin bij de momenten die belangrijk zijn.','De voorlopige trouwcollecties beginnen bij €2.200 voor zes uur. Met een langere reportage ontstaat ruimte voor voorbereidingen of de avond. Deel jullie datum en locaties voor een persoonlijk voorstel met de totaalprijs, reisinformatie en levering vooraf afgesproken.')],
  'gallery':['wedding-03','wedding-06','wedding-08']
 },
 'the-hague':{
  'title':('Love story & couples photographer The Hague | Vicon Creator','Loveshoot Den Haag | Koppelfotograaf Vicon Creator'),
  'desc':('Plan a cinematic love story photoshoot in The Hague, Den Haag or by the coast. Relaxed couples photography by Viktoriia Loskutova, based in the Netherlands.','Plan een filmische loveshoot in Den Haag of aan de kust. Ontspannen koppelfotografie door Viktoriia Loskutova, vanuit Nederland.'),
  'h1':('Your love story\nin The Hague.','Jullie loveshoot\nin Den Haag.'),'hero':'lovestory-09','theme':'olive','service':'couples',
  'intro':('A city walk or the feeling of the sea. A couples session in Den Haag can be a small escape, with the two of you at the centre.','Een stadswandeling of het gevoel van de zee. Een loveshoot in Den Haag kan een klein uitstapje zijn, met jullie twee centraal.'),
  'sections':[
   ('City streets or an open horizon?','The Hague gives us more than one direction for a love story. We can discuss a walk in the city, a setting near home or time towards Scheveningen and the coast. The choice starts with your preferred atmosphere, not a checklist of locations. I photograph couples throughout the Netherlands, including The Hague and the coast.','Stadsstraten of een open horizon?','Den Haag geeft ons meerdere richtingen voor een loveshoot. We kunnen een wandeling in de stad bespreken, een plek dicht bij huis of tijd richting Scheveningen en de kust. We beginnen bij de gewenste sfeer. Ik fotografeer koppels door heel Nederland, waaronder in Den Haag en aan de kust.'),
   ('Make room for the weather.','For a coastal session, wind, light and the distance from the meeting point all affect the experience. We’ll plan a manageable route and discuss a weather alternative. Comfortable layers and clothes that move naturally can help you feel at ease. Access to any particular location is confirmed during planning.','Geef het weer ruimte.','Aan de kust bepalen wind, licht en de afstand vanaf het ontmoetingspunt mede de ervaring. We plannen een haalbare route en bespreken een alternatief bij ander weer. Comfortabele lagen en kleding die natuurlijk beweegt helpen om je prettig te voelen. De toegang tot een specifieke plek bevestigen we tijdens de voorbereiding.'),
   ('No special occasion required.','An anniversary, engagement, weekend away or an ordinary day together can all be a reason for photographs. A couples session has an indicative starting price of €350 for approximately one hour. Tell me your preferred date and mood so we can make a plan.','Een bijzondere aanleiding is niet nodig.','Een jubileum, verloving, weekendje weg of een gewone dag samen kan een reden voor foto’s zijn. De richtprijs voor een loveshoot is €350 voor ongeveer een uur. Vertel welke datum en sfeer jullie voor ogen hebben, dan maken we een plan.')],
  'gallery':['lovestory-22','lovestory-24','lovestory-25']
 },
 'belgium':{
  'title':('Wedding photographer Belgium | Vicon Creator · Netherlands based','Trouwfotograaf België | Vicon Creator · Vanuit Nederland'),
  'desc':('Planning a wedding in Belgium? Discuss cinematic wedding photography with Netherlands-based Viktoriia Loskutova. Travel, coverage and pricing by arrangement.','Trouwen in België? Bespreek filmische trouwfotografie met Viktoriia Loskutova vanuit Nederland. Reis, reportage en prijs in overleg.'),
  'h1':('Your wedding\nin Belgium.','Jullie bruiloft\nin België.'),'hero':'wedding-09','theme':'cream','service':'weddings',
  'intro':('A celebration across the border, with the same attention to light and feeling. Wedding photography in Belgium is available by arrangement from my base in the Netherlands.','Een viering over de grens, met dezelfde aandacht voor licht en gevoel. Trouwfotografie in België is in overleg mogelijk vanuit mijn basis in Nederland.'),
  'sections':[
   ('Begin with the place and the plan.','Whether you are planning in Antwerp, Ghent, Brussels or elsewhere in Belgium, share the venue, date and outline of the day. These details help us understand travel, the coverage you need and whether an overnight stay makes sense. Availability is confirmed individually.','Begin bij de plek en het plan.','Of jullie nu plannen maken in Antwerpen, Gent, Brussel of elders in België: deel de locatie, datum en dagindeling. Daarmee kunnen we de reis, benodigde reportage en een eventuele overnachting bespreken. Beschikbaarheid bevestigen we persoonlijk.'),
   ('One considered photographic story.','My approach combines natural moments with intentional portraits and consistent editing. We’ll discuss the visual atmosphere you want, when portraits can fit comfortably and which people and moments are most important to you. The collection below shows my photographic style; it is not presented as a Belgian wedding reportage.','Eén doordacht fotografisch verhaal.','Mijn aanpak combineert natuurlijke momenten met bewuste portretten en een samenhangende bewerking. We bespreken de gewenste sfeer, een passend moment voor portretten en welke mensen en momenten het belangrijkst zijn. De selectie hieronder laat mijn stijl zien; de foto’s worden niet gepresenteerd als een Belgische trouwreportage.'),
   ('Travel agreed before you book.','The Netherlands wedding guide prices are a starting point, not a fixed destination quote. Travel, accommodation if needed, coverage, delivery and the final total are set out in a personal proposal before booking. Send your details through @vicon.creator to begin.','Reisafspraken vóór de boeking.','De Nederlandse richtprijzen voor bruiloften zijn een startpunt, geen vaste offerte voor een buitenlandse bestemming. Reis, eventuele overnachting, reportage, levering en totaalprijs staan in het persoonlijke voorstel vóór de boeking. Stuur jullie details via @vicon.creator om te beginnen.')],
  'gallery':['wedding-12','wedding-15','wedding-18']
 }}[key]
 ix=0 if lang=='en' else 2
 text=''.join(f'<h2>{e(s[ix])}</h2><p>{e(s[ix+1])}</p>' for s in data['sections'])
 caption=pick(('Selected photographs from the portfolio. They illustrate the style; specific shoot locations are not attributed here.','Geselecteerde foto’s uit het portfolio. Ze laten de stijl zien; er worden hier geen specifieke opnamelocaties aan toegeschreven.'),lang)
 body=f'''<div class="wrap page-top">{breadcrumb(pick(data['h1'],lang).replace('\n',' '),lang)}<section class="destination-intro"><div><span class="eyebrow">Vicon Creator · {pick(('Netherlands & Europe','Nederland & Europa'),lang)}</span><h1>{br(pick(data['h1'],lang))}</h1><p class="lede">{e(pick(data['intro'],lang))}</p>{link('contact',t['enquire'],lang,'button')}</div>{photo(data['hero'],lang,eager=True)}</section><article class="editorial-body">{text}<div class="button-row">{link(data['service'],pick(('Explore the full collection','Bekijk de volledige collectie'),lang),lang)}{link('prices',t['prices'],lang)}</div></article><section class="section"><div class="gallery-intro"><div><span class="eyebrow">{t['selected']}</span><h2>{pick(('A sense of the work.','Een gevoel bij het werk.'),lang)}</h2></div><p>{caption}</p></div>{gallery(data['gallery'],lang)}</section></div>{cta(lang)}'''
 page(key,lang,pick(data['title'],lang),pick(data['desc'],lang),body,data['theme'],data['hero'])

def privacy(lang):
 t=UI[lang]
 body=f'''<div class="wrap page-top">{breadcrumb(t['privacy'],lang)}<section class="page-heading"><span class="eyebrow">Vicon Creator</span><h1>{pick(('Privacy &<br>business details.','Privacy &<br>bedrijfsgegevens.'),lang)}</h1></section><article class="editorial-body" style="padding-bottom:100px"><h2>{pick(('Business','Bedrijf'),lang)}</h2><p>Vicon Creator<br>Viktoriia Loskutova<br>KVK: 97270725<br>{pick(('Legal form: sole proprietorship','Rechtsvorm: eenmanszaak'),lang)}<br>{pick(('Branch number','Vestigingsnummer'),lang)}: 000062524429<br>Netherlands</p><h2>{pick(('Visiting the portfolio','Het portfolio bezoeken'),lang)}</h2><p>{pick(('Photographs, videos and fonts are served with the site. Hosting may process technical request data to deliver and protect the site. Google Analytics 4 loads automatically to measure visits and page use. Advertising storage and personalisation remain disabled. Analytics cookies use the vicon prefix and are configured to expire after 180 days. Google processes analytics data under its own privacy terms; processing may involve countries outside the EEA.','Foto’s, video’s en lettertypen worden via de site geladen. De hosting kan technische verzoekgegevens verwerken om de site te leveren en te beschermen. Google Analytics 4 wordt automatisch geladen om bezoeken en paginagebruik te meten. Advertentieopslag en personalisatie blijven uitgeschakeld. Analytische cookies gebruiken de prefix vicon en zijn ingesteld op een looptijd van 180 dagen. Google verwerkt analysegegevens volgens zijn eigen privacyvoorwaarden; verwerking kan ook buiten de EER plaatsvinden.'),lang)}</p><h2>{pick(('Getting in touch','Contact opnemen'),lang)}</h2><p>{pick(('The enquiry form asks for your name, session type, preferred date if provided, contact method and contact details. If you choose Other, it also asks for your idea. These details, the page address and submission time are sent through a dedicated Google Apps Script service, recorded in a Google Sheet and forwarded to the photographer by email and Telegram. The website administrator operates this service for Vicon Creator. These enquiry fields are not sent to Google Analytics. They are not published on the site or saved in browser storage. The selected contact method is how you would like to receive a reply; it does not change how the form is submitted. You can also contact @vicon.creator directly on Instagram, where Instagram’s own privacy settings and policies apply.','Het aanvraagformulier vraagt om je naam, het soort fotoshoot, een eventuele voorkeursdatum, contactmethode en contactgegevens. Kies je Anders, dan vragen we ook naar je idee. Deze gegevens, het pagina-adres en het verzendtijdstip worden via een eigen Google Apps Script-service opgeslagen in een Google Sheet en per e-mail en Telegram aan de fotograaf doorgestuurd. De websitebeheerder beheert deze service voor Vicon Creator. De aanvraagvelden worden niet naar Google Analytics verstuurd. Ze worden niet op de site gepubliceerd of in browseropslag bewaard. De gekozen contactmethode bepaalt hoe je graag een reactie ontvangt, niet hoe het formulier wordt verstuurd. Je kunt ook rechtstreeks contact opnemen met @vicon.creator op Instagram. Daar gelden de privacyinstellingen en het beleid van Instagram.'),lang)}</p><p><a class="text-link" href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google Privacy Policy ↗</a></p><h2>{pick(('Your information','Jouw gegevens'),lang)}</h2><p>{pick(('For questions about your enquiry, access, correction or deletion of personal data, contact vicon.creator@gmail.com. Information is used to handle your request and any resulting booking. Publication of client photographs is discussed separately.', 'Voor vragen over je aanvraag, inzage, correctie of verwijdering van persoonsgegevens kun je mailen naar vicon.creator@gmail.com. Gegevens worden gebruikt om je aanvraag en een eventuele boeking af te handelen. Publicatie van klantfoto’s wordt apart besproken.'),lang)}</p><h2>{pick(('Photographs & use','Foto’s & gebruik'),lang)}</h2><p>{pick(('The photographs and films in this portfolio are the work of Viktoriia Loskutova / Vicon Creator. Displaying them here does not grant permission to reuse or publish them. For usage requests or a concern about a photograph, please contact the photographer.','De foto’s en films in dit portfolio zijn het werk van Viktoriia Loskutova / Vicon Creator. De weergave hier geeft geen toestemming om ze opnieuw te gebruiken of te publiceren. Neem voor gebruiksverzoeken of vragen over een foto contact op met de fotograaf.'),lang)}</p><a class="text-link" href="{INSTAGRAM}" target="_blank" rel="noopener noreferrer">@vicon.creator {arrow()}</a></article></div>'''
 page('privacy',lang,pick(('Privacy & business details | Vicon Creator','Privacy & bedrijfsgegevens | Vicon Creator'),lang),pick(('Business details for Vicon Creator, KVK 97270725, and information about visiting the photography portfolio and contacting Viktoriia Loskutova.','Bedrijfsgegevens van Vicon Creator, KVK 97270725, en informatie over het bezoeken van het portfolio en contact met Viktoriia Loskutova.'),lang),body)

def city_links(lang):
 return ''.join(f'<article class="destination-card"><h2>{e(pick(v["name"],lang))}</h2><p>{e(pick(v["intro"],lang))}</p>{link(k,pick(("Plan a session here","Plan hier je fotoshoot"),lang),lang)}</article>' for k,v in CITIES.items())

def guide_cards(keys,lang):
 return '<div class="guide-cards">'+''.join(f'<article class="guide-card"><h3>{e(pick(GUIDES[k]["title"],lang))}</h3><p>{e(pick(GUIDES[k]["intro"],lang))}</p>{link(k,pick(("Read the guide","Lees de tips"),lang),lang)}</article>' for k in keys)+'</div>'

def related_reading(lang,service=None):
 keys=[k for k,v in GUIDES.items() if not service or service in v['services']][:3]
 return f'<section class="section wrap related-reading"><span class="eyebrow">{pick(("Planning your session","Je fotoshoot voorbereiden"),lang)}</span><h2>{pick(("A little preparation.","Goed voorbereid."),lang)}</h2>{guide_cards(keys,lang)}<div class="button-row">{link("guides",pick(("All session guides","Alle fotoshoot tips"),lang),lang)}{link("locations",pick(("Choose a location","Kies een locatie"),lang),lang)}</div></section>'

def city_page(key,lang):
 v=CITIES[key];label=pick(v['name'],lang)
 sections=''.join(f'<section><h2>{e(pick(h,lang))}</h2><p>{e(pick(p,lang))}</p></section>' for h,p in v['sections'])
 links=''.join(link(k,pick(SERVICES[k]['label'],lang) if k in SERVICES else pick(('Wedding photography in Amsterdam','Trouwfotografie in Amsterdam'),lang) if k=='amsterdam' else pick(('Couples in The Hague','Loveshoot in Den Haag'),lang) if k=='the-hague' else UI[lang]['prices'],lang) for k in v['links'])
 source_title,source_url=v['source']
 body=f'''<div class="wrap page-top city-page">{breadcrumb(label,lang)}<section class="page-heading"><span class="eyebrow">Vicon Creator · {pick(('On-location photography','Fotografie op locatie'),lang)}</span><h1>{pick(('Photographer in ','Fotograaf in '),lang)}{e(label)}</h1><p class="lede">{e(pick(v['intro'],lang))}</p></section><div class="guide-layout guide-body"><figure class="guide-cover">{photo(v["hero"],lang,eager=True)}<figcaption class="city-notes">{pick(("From the Vicon Creator portfolio: an example of the photographic style, not a location reference.","Uit het portfolio van Vicon Creator: een voorbeeld van de fotografische stijl, geen verwijzing naar de opnamelocatie."),lang)}</figcaption></figure>{sections}<p class="city-notes">{pick(('Location background:','Achtergrond bij de locatie:'),lang)} <a href="{e(source_url)}" target="_blank" rel="noopener noreferrer">{e(source_title)}</a>. {pick(('Access and any permissions are confirmed for the proposed session.','Toegang en eventuele toestemming worden voor de geplande sessie afgestemd.'),lang)}</p><h2>{pick(('Find your kind of photography','Vind jouw soort fotografie'),lang)}</h2><div class="region-links">{links}</div><div class="button-row">{link('prices',pick(('See guide prices','Bekijk de richtprijzen'),lang),lang)}{link('contact',UI[lang]['enquire'],lang,'button')}</div></div></div>{related_reading(lang,'family' if key=='city-utrecht' else 'events' if key=='city-rotterdam' else 'maternity' if key=='city-hague' else 'couples')}'''
 page(key,lang,pick(v['title'],lang)+' | Vicon Creator',pick(v['intro'],lang).split('. ')[0]+'. '+pick(('Compare settings, plan your route and enquire about a session.','Vergelijk locaties, plan je route en vraag een fotoshoot aan.'),lang),body,hero=v['hero'])

def guides_index(lang):
 title=pick(('Photoshoot guides | Planning, outfits & weather','Fotoshoot tips | Planning, kleding & weer'),lang)
 body=f'''<div class="wrap page-top">{breadcrumb(pick(('Session guides','Fotoshoot tips'),lang),lang)}<section class="page-heading"><span class="eyebrow">Vicon Creator</span><h1>{pick(('Before the<br><em>photographs.</em>','Voor de<br><em>foto’s.</em>'),lang)}</h1><p class="lede">{pick(('Practical guides for choosing your session, planning around the weather and knowing what to discuss before booking.','Praktische tips voor het kiezen van je fotoshoot, een plan voor het weer en de afspraken die je vóór het boeken wilt maken.'),lang)}</p></section>{guide_cards(list(GUIDES),lang)}</div>{cta(lang)}'''
 page('guides',lang,title,pick(('Plan a wedding, couples, maternity, family or event photoshoot with practical guidance on timing, outfits, weather and a useful brief.','Bereid je bruiloft, loveshoot, zwangerschapsshoot, gezinsshoot of evenement voor met tips over planning, kleding, weer en een heldere briefing.'),lang),body)

def guide_page(key,lang):
 v=GUIDES[key];title=pick(v['title'],lang)
 toc=''.join(f'<li><a href="#part-{i}">{e(pick(h,lang))}</a></li>' for i,(h,p) in enumerate(v['sections'],1))
 sections=''.join(f'<section id="part-{i}"><h2>{e(pick(h,lang))}</h2><p>{e(pick(p,lang))}</p></section>' for i,(h,p) in enumerate(v['sections'],1))
 links=''.join(link(k,pick(SERVICES[k]['label'],lang) if k in SERVICES else pick(GUIDES[k]['title'],lang) if k in GUIDES else UI[lang]['prices'],lang) for k in v['services']+v['related'])
 body=f'''<div class="wrap page-top"><div class="guide-layout">{breadcrumb(pick(('Session guide','Fotoshoot tips'),lang),lang)}<article><header class="page-heading"><span class="eyebrow">Vicon Creator · {pick(('Session planning','Voorbereiding'),lang)}</span><h1>{e(title)}</h1><p class="lede">{e(pick(v['intro'],lang))}</p></header><nav class="guide-contents" aria-label="{pick(('On this page','Op deze pagina'),lang)}"><strong>{pick(('In this guide','In deze gids'),lang)}</strong><ol>{toc}</ol></nav><div class="guide-body">{sections}</div><p class="city-notes">{pick(('Planning information from Vicon Creator. Your final session details and terms are agreed personally before booking.','Planningsinformatie van Vicon Creator. De definitieve inhoud en voorwaarden spreken we persoonlijk af vóór de boeking.'),lang)} {link('about',pick(('Meet the photographer','Over de fotograaf'),lang),lang)}</p><div class="region-links">{links}</div><div class="button-row">{link('guides',pick(('All session guides','Alle fotoshoot tips'),lang),lang)}{link('contact',UI[lang]['enquire'],lang,'button',v['services'][0])}</div></article></div></div>'''
 # These general planning pages do not claim personal authorship, client stories or review dates.
 page(key,lang,title+' | Vicon Creator',pick(v['intro'],lang),body)


for lang in LANGS:
 home(lang)
 portfolio(lang)
 for key in SERVICES:collection(key,lang)
 postpartum(lang)
 about(lang);prices(lang);contact(lang);locations(lang)
 for key in ['amsterdam','the-hague','belgium']:destination(key,lang)
 privacy(lang)
 for key in CITIES:city_page(key,lang)
 guides_index(lang)
 for key in GUIDES:guide_page(key,lang)

(DIST/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#20271f"/><text x="32" y="48" text-anchor="middle" font-family="Georgia,serif" font-size="50" fill="#f2efe8">v</text></svg>')
(DIST/'robots.txt').write_text(('User-agent: *\nAllow: /\n' if PUBLIC_INDEXING else 'User-agent: *\nDisallow: /\n')+'\nSitemap: '+ORIGIN+'/sitemap.xml\nSitemap: '+ORIGIN+'/sitemap-images.xml\n')
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
ET.register_namespace('xhtml', 'http://www.w3.org/1999/xhtml')
ET.register_namespace('image', 'http://www.google.com/schemas/sitemap-image/1.1')
def write_xml(path, text):
 tree = ET.ElementTree(ET.fromstring(text))
 ET.indent(tree, space='  ')
 tree.write(path, encoding='utf-8', xml_declaration=True)
 with path.open('a') as output: output.write('\n')
sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
for p in PAGES:
 sitemap+='<url><loc>'+e(p['url'])+'</loc>'+''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{e(ORIGIN+url(p["key"],l))}"/>' for l in LANGS)+f'<xhtml:link rel="alternate" hreflang="x-default" href="{e(ORIGIN+url(p["key"],"en"))}"/></url>'
write_xml(DIST/'sitemap.xml', sitemap+'</urlset>')
# Image discovery reflects the images actually visible on each landing page.
class PageImages(HTMLParser):
 def __init__(self): super().__init__(); self.images=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img' and a.get('src','').startswith('/assets/photos/'):
   self.images.add(ORIGIN+a['src'])
image_map='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
for p in PAGES:
 reader=PageImages();reader.feed((DIST/p['path']).read_text())
 if reader.images:
  image_map+='<url><loc>'+e(p['url'])+'</loc>'+''.join('<image:image><image:loc>'+e(im)+'</image:loc></image:image>' for im in sorted(reader.images))+'</url>'
write_xml(DIST/'sitemap-images.xml', image_map+'</urlset>')
if PUBLIC_INDEXING and not origin_parts.path and not origin_parts.hostname.endswith('.github.io'):
 (DIST/'CNAME').write_text(origin_parts.hostname+'\n')
else:
 (DIST/'CNAME').unlink(missing_ok=True)

(DIST/'404.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found | Vicon Creator</title><link rel="stylesheet" href="/assets/fonts/fonts.css"><link rel="stylesheet" href="/assets/site.css">{analytics_head()}</head><body>{header("home","en")}<main id="main" class="empty-page wrap"><span class="eyebrow">404 · Vicon Creator</span><h1>A different<br><em>way back.</em></h1><p>This page could not be found.<br>Deze pagina bestaat niet.</p>{link("home","Return to the photographs","en","button")}</main>{footer("en")}{booking_dialog("en")}<script src="/assets/site.js" defer></script><script type="module" src="/assets/booking.mjs"></script></body></html>')
(DIST/'_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n/assets/*\n  Cache-Control: public, max-age=86400\n')
(ROOT/'src/pages.json').write_text(json.dumps(PAGES,ensure_ascii=False,indent=2))
(ROOT/'src/used-images.json').write_text(json.dumps(sorted(USED_IMAGES),indent=2))
print(f'Generated {len(PAGES)} pages + 404. {len(USED_IMAGES)} selected photographs. Indexing: {PUBLIC_INDEXING}.')

if args.portable:
 import re
 # A 404 is served at an unknown URL depth, so its links must use the public base.
 error_page=DIST/'404.html'
 error_page.write_text(re.sub(r'(href|src)="(/[^"]*)"', lambda m: m[1]+'="'+ORIGIN+m[2]+'"', error_page.read_text()))
 from portable import rewrite_site
 rewrite_site(DIST)
(DIST/'.nojekyll').write_text('')
