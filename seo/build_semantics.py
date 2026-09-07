"""Curated query hypotheses mapped to client intents; no invented demand metrics."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
from content import ROUTES
# Each source documents terminology/intent, NOT search volume or a verified Google position.
GROUPS=[
('weddings','P1','commercial','NL','https://sjoerdbooij.nl/',
'wedding photographer Netherlands|wedding photography Netherlands|cinematic wedding photographer Netherlands|intimate wedding photographer Netherlands|wedding photographer Holland|wedding photography packages Netherlands|natural wedding photography Netherlands',
'trouwfotograaf Nederland|trouwfotografie Nederland|bruidsfotograaf Nederland|bruidsfotografie Nederland|filmische trouwfotografie|spontane trouwfotografie|fotograaf kleine bruiloft|intieme bruiloft fotograaf'),
('couples','P1','commercial','NL','https://www.charlottevanwooning.nl/love-shoot-den-haag/',
'couples photographer Netherlands|couple photoshoot Netherlands|love story photographer Netherlands|engagement photoshoot Netherlands|anniversary photoshoot Netherlands|romantic photoshoot Netherlands|outdoor couples photography|cinematic couples photography',
'loveshoot fotograaf|loveshoot Nederland|love shoot Nederland|koppelfotografie|koppelshoot|fotoshoot stel|verlovingsshoot|verlovingsfotografie|romantische fotoshoot|jubileum fotoshoot'),
('portraits','P1','commercial','NL','https://andraslens.com/portfolio/portraits/',
'portrait photographer Netherlands|portrait photography Netherlands|cinematic portrait photographer|black and white portrait photographer|outdoor portrait photoshoot Netherlands|creative portrait photography|individual photoshoot Netherlands|personal portrait photographer',
'portretfotograaf Nederland|portretfotografie Nederland|portret fotoshoot|zwart wit portretfotografie|creatieve portretfotografie|artistieke portretfotografie|buiten portretfotografie|persoonlijke portretfoto|filmische portretten'),
('maternity','P1','commercial','NL','https://www.wiesjefotografie.nl/zwangerschapsshootdenhaag',
'maternity photographer Netherlands|maternity photoshoot Netherlands|pregnancy photoshoot Netherlands|pregnancy portrait photographer|outdoor maternity photoshoot|natural maternity photography|maternity photos with partner',
'zwangerschapsfotografie|zwangerschapsshoot Nederland|zwangerschapsfotograaf|zwangerschap fotoshoot|zwangerschapsreportage|zwangerschapsshoot buiten|zwangerschapsshoot met partner|natuurlijke zwangerschapsfotografie'),
('family','P1','commercial','NL','https://www.ohbeautifulworld.com/',
'family photographer Netherlands|family photoshoot Netherlands|children photographer Netherlands|kids photoshoot Netherlands|outdoor family photography|natural family portraits|lifestyle family photographer|child portrait photographer',
'familiefotograaf Nederland|gezinsfotografie|familiefotografie|gezinsshoot|familie fotoshoot|kinderfotograaf|kinderfotografie|kinderportretten|gezinsfotoshoot buiten|spontane familiefotografie'),
('events','P1','commercial','NL','https://www.willemmartinot.nl/en/event-photographer-rotterdam/',
'event photographer Netherlands|event photography Netherlands|corporate event photographer Netherlands|company event photographer|brand event photography|celebration photographer|party photographer Netherlands|event photography quote',
'evenementenfotograaf|evenementenfotografie|event fotograaf|fotograaf bedrijfsfeest|bedrijfsfeest fotografie|fotograaf evenement|feestfotograaf|evenementenfotografie offerte'),
('amsterdam','P1','local commercial','NL','https://sjoerdbooij.nl/',
'wedding photographer Amsterdam|Amsterdam wedding photography|cinematic wedding photographer Amsterdam|intimate wedding photographer Amsterdam|wedding photography Amsterdam prices',
'trouwfotograaf Amsterdam|bruidsfotograaf Amsterdam|trouwfotografie Amsterdam|bruidsfotografie Amsterdam|kleine bruiloft fotograaf Amsterdam'),
('the-hague','P1','local commercial','NL','https://www.charlottevanwooning.nl/love-shoot-den-haag/',
'couples photographer The Hague|couple photoshoot The Hague|love story photographer Den Haag|engagement photoshoot The Hague|couples photoshoot Scheveningen',
'loveshoot Den Haag|love shoot Den Haag|koppelshoot Den Haag|fotoshoot stel Den Haag|loveshoot Scheveningen|verlovingsshoot Den Haag'),
('belgium','P2','local commercial','BE','https://elinefotografie.be/huwelijken-aanbod',
'wedding photographer Belgium|wedding photography Belgium|cinematic wedding photographer Belgium|intimate wedding photographer Belgium|Netherlands based wedding photographer Belgium',
'trouwfotograaf België|huwelijksfotograaf België|bruidsfotograaf België|trouwfotografie België|huwelijksfotografie België|Nederlandse trouwfotograaf België'),
('locations','P2','commercial','NL','https://sjoerdbooij.nl/',
'photographer Netherlands|photography Netherlands|photographer Holland|photoshoot Netherlands|on location photographer Netherlands',
'fotograaf Nederland|fotoshoot Nederland|fotograaf op locatie|fotoshoot op locatie|fotografie Nederland'),
('prices','P1','commercial comparison','NL','https://maartjehensen.com/en/pricing/',
'photography prices Netherlands|photographer cost Netherlands|wedding photographer cost Netherlands|couple photoshoot price|portrait photoshoot price|maternity photoshoot price|family photoshoot cost|event photographer hourly rate',
'fotografie tarieven|fotograaf kosten|trouwfotograaf kosten|loveshoot prijs|portretfotografie tarieven|zwangerschapsshoot prijs|familie fotoshoot kosten|evenementenfotograaf tarief'),
('city-amsterdam','P1','local commercial','NL','https://www.joannapantigoso.com/portfolio/vacation-photography/1672416-family-photography-jordaan-amsterdam',
'photographer Amsterdam|photoshoot Amsterdam|portrait photographer Amsterdam|couple photoshoot Amsterdam|family photographer Amsterdam|family photoshoot Amsterdam|outdoor portrait photoshoot Amsterdam|canal photoshoot Amsterdam',
'fotograaf Amsterdam|fotoshoot Amsterdam|portretfotograaf Amsterdam|loveshoot Amsterdam|familiefotograaf Amsterdam|gezinsshoot Amsterdam|portret fotoshoot Amsterdam|fotoshoot grachten Amsterdam'),
('city-hague','P1','local commercial','NL','https://www.wiesjefotografie.nl/zwangerschapsshootdenhaag',
'photographer The Hague|photographer Den Haag|maternity photographer The Hague|pregnancy photoshoot The Hague|family photographer The Hague|portrait photographer The Hague|maternity photoshoot Scheveningen',
'fotograaf Den Haag|fotoshoot Den Haag|zwangerschapsshoot Den Haag|zwangerschapsfotograaf Den Haag|familiefotograaf Den Haag|portretfotograaf Den Haag|zwangerschapsshoot Scheveningen|gezinsshoot Den Haag'),
('city-rotterdam','P2','local commercial','NL','https://www.willemmartinot.nl/en/event-photographer-rotterdam/',
'photographer Rotterdam|portrait photographer Rotterdam|event photographer Rotterdam|corporate event photography Rotterdam|couples photoshoot Rotterdam|creative portrait Rotterdam',
'fotograaf Rotterdam|portretfotograaf Rotterdam|evenementenfotograaf Rotterdam|fotograaf bedrijfsfeest Rotterdam|loveshoot Rotterdam|creatieve fotoshoot Rotterdam'),
('city-utrecht','P2','local commercial','NL','https://www.ohbeautifulworld.com/',
'photographer Utrecht|family photographer Utrecht|family photoshoot Utrecht|couples photoshoot Utrecht|portrait photographer Utrecht|children photographer Utrecht',
'fotograaf Utrecht|familiefotograaf Utrecht|gezinsshoot Utrecht|familie fotoshoot Utrecht|loveshoot Utrecht|portretfotograaf Utrecht|kinderfotograaf Utrecht'),
('guide-wedding','P2','informational','NL','https://www.fionakellyphotography.com/how-to-get-the-perfect-wedding-day-timeline/',
'how many hours wedding photography|wedding photography timeline|6 vs 8 hours wedding photography|8 vs 10 hours wedding photography|when to take wedding portraits',
'hoeveel uur trouwfotograaf|planning trouwfotografie|6 of 8 uur trouwfotograaf|wanneer trouwfoto maken|draaiboek trouwfotografie'),
('guide-outfits','P2','informational','NL','https://www.moniekvanselmfotografie.nl/inspiratie/kledingtips-voor-fotoshoots-in-utrecht-en-omgeving-een-compleet-overzicht/',
'what to wear for a photoshoot|couples photoshoot outfits|family photoshoot outfits|portrait photoshoot clothing|what to wear outdoor photoshoot',
'kleding fotoshoot|kleding familie fotoshoot|kleding loveshoot|kledingtips fotoshoot|wat aantrekken fotoshoot'),
('guide-rain','P2','informational','NL','https://louiserosephotography.com/outdoor-family-photography-rain-wet-weather/',
'photoshoot in the rain|what if it rains on photoshoot day|cloudy day photoshoot|rain backup wedding photos|outdoor family photos rain',
'fotoshoot regen|wat als het regent tijdens fotoshoot|fotoshoot bewolkt weer|trouwfoto regen alternatief|buiten fotoshoot slecht weer'),
('guide-maternity','P2','informational','NL','https://www.wiesjefotografie.nl/zwangerschapsshootdenhaag',
'when to book maternity photos|how to prepare maternity photoshoot|maternity photoshoot with partner|maternity photoshoot location ideas',
'wanneer zwangerschapsshoot boeken|zwangerschapsshoot voorbereiden|zwangerschapsshoot plannen|locatie zwangerschapsshoot kiezen'),
('guide-family','P2','informational','NL','https://www.ohbeautifulworld.com/',
'how to prepare children for family photos|family photoshoot checklist|family photoshoot with young children|what to bring family photoshoot',
'gezinsshoot voorbereiden|kinderen voorbereiden fotoshoot|familie fotoshoot checklist|wat meenemen gezinsshoot'),
('guide-events','P2','informational','NL','https://www.willemmartinot.nl/en/event-photographer-rotterdam/',
'event photography brief|event photographer checklist|how to brief an event photographer|event photography shot list',
'briefing evenementenfotograaf|evenementenfotografie checklist|fotograaf briefing voorbeeld|shotlist evenement'),
('home','P1','brand','NL / BE','https://www.instagram.com/vicon.creator/',
'Viktoriia Loskutova photographer|Vicon Creator photographer|vicon.creator|cinematic photographer Netherlands',
'Viktoriia Loskutova fotograaf|Vicon Creator fotografie|filmische fotograaf Nederland'),
]
rows=[];seen=set()
GROUPS.append(('postpartum','P1','commercial / planning','NL','https://www.shertakescare.com/geboortefotografie-kraamreportage',
 'postpartum photographer Netherlands|postpartum photography Netherlands|postpartum photoshoot|postpartum portrait photography|postpartum photographer Amsterdam|postpartum photographer The Hague|postpartum photographer Den Haag|postpartum photographer Rotterdam|postpartum photographer Utrecht|motherhood photographer Netherlands|motherhood photoshoot Netherlands|mother and baby photographer|mother and baby photoshoot Netherlands|mother and baby photoshoot Amsterdam|mother and baby photography The Hague|newborn photographer Netherlands|lifestyle newborn photographer Netherlands|lifestyle newborn photography at home|newborn photoshoot at home Netherlands|natural newborn photography Netherlands|documentary newborn photography|in home newborn photographer Amsterdam|lifestyle newborn photographer The Hague|newborn photographer Den Haag|lifestyle newborn photographer Rotterdam|lifestyle newborn photographer Utrecht|breastfeeding photographer Netherlands|breastfeeding photography|breastfeeding photoshoot|nursing photography|feeding baby photoshoot|postpartum family photography|father and baby photoshoot|new parents photoshoot|baby and parents photography|fourth trimester photography|when to book postpartum photos|what to wear for newborn photos at home|how to prepare for a lifestyle newborn photoshoot|postpartum photoshoot price|at home newborn photography cost',
 'kraamreportage|kraamreportage Nederland|kraamfotograaf|kraamtijd fotografie|fotograaf kraamtijd|kraamreportage aan huis|kraamreportage thuis|kraamreportage Amsterdam|kraamreportage Den Haag|kraamreportage Rotterdam|kraamreportage Utrecht|postpartum fotografie|postpartum fotoshoot|fotografie na de bevalling|moederschapsfotografie|moederschap fotoshoot|moeder en baby fotoshoot|moeder baby fotografie|moeder kind fotoshoot|moeder baby fotoshoot Amsterdam|moeder baby fotoshoot Den Haag|newborn fotograaf Nederland|lifestyle newborn fotografie|lifestyle newborn fotograaf|lifestyle newborn fotoshoot|newbornshoot thuis|newborn fotografie aan huis|natuurlijke newborn fotografie|newborn fotograaf Amsterdam|newborn fotograaf Den Haag|lifestyle newborn fotograaf Rotterdam|lifestyle newborn fotograaf Utrecht|borstvoedingsfotografie|borstvoeding fotoshoot|borstvoedingsshoot|fotograaf borstvoeding|vader baby fotoshoot|fotoshoot ouders met baby|babyfotografie thuis|kraamreportage kosten|kraamreportage prijs|newbornshoot thuis kosten|wanneer kraamreportage plannen|newbornshoot thuis voorbereiden|kleding newbornshoot thuis'))
for key,priority,intent,market,source,en,nl in GROUPS:
 for i,terms in enumerate([en,nl]):
  for keyword in terms.split('|'):
   marker=(keyword.casefold(),i)
   assert marker not in seen,marker
   seen.add(marker)
   rows.append({'keyword':keyword,'language':['EN','NL'][i],'market':market,'intent':intent,'cluster':key,'target_path':ROUTES[key][i],'priority':priority,'evidence':'Terminology/intent source; exact query is an unmeasured hypothesis','source_url':source,'monthly_searches_nl':None,'monthly_searches_be':None,'volume_status':'Not measured; not zero','implementation':'Page implemented; ranking not verified'})
(ROOT/'seo/keyword-map.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
(ROOT/'seo/keyword-planner-import.txt').write_text('\n'.join(dict.fromkeys(r['keyword'] for r in rows))+'\n')
print(len(rows),'unique language/query rows across',len(GROUPS),'clusters')
