from pathlib import Path
import re,json,hashlib,importlib.util,base64
from collections import Counter

ROOT=Path(__file__).parent
source=ROOT/'QazPrice_Астана_4_дүкен.html'
original=source.read_text(encoding='utf-8')
backup=ROOT/'QazPrice_before_redesign_2026-11-11.html'
if not backup.exists():backup.write_text(original,encoding='utf-8')
base=backup.read_text(encoding='utf-8')
old_products=json.loads(re.search(r'const PRODUCTS:Product\[\]=(\[.*?\]);',base,re.S)[1])
old_offers=json.loads(re.search(r'const OFFERS:Record<number,Record<string,number>>=(\{.*?\});',base,re.S)[1])
products=[dict(p) for p in old_products];offers={k:dict(v) for k,v in old_offers.items()}
live_groups=json.loads((ROOT/'arzan-taxonomy-live.json').read_text(encoding='utf-8'))['categories']
excluded_categories={'1280','2084','1279'}
groups=[dict(id=g['id'],name=g['name'],icon=g['icon'],subs=g['subcategories']) for g in live_groups if g['id'] not in excluded_categories]
gid_by_name={g['name']:g['id'] for g in groups}
group_map={'vegetables':'1042','fruit':'1043','dairy':'1044','canned':'1277','meat':'1278','other-Бакалея':'1045','other-Тәттілер':'1593','other-Мұздатылған өнімдер':'1591','other-Тұрмыстық тауарлар':'1405','other-Шай және кофе':'1281'}
assignments=json.loads((ROOT/'catalog-assignments.json').read_text(encoding='utf-8'))
legacy={p['cat']:group_map.get(assignments[str(p['id'])][0],gid_by_name.get(p['cat'],'')) for p in old_products}
legacy.update(gid_by_name)
store_ids={'Galmart':'galmart','MagnumGO':'magnum','METRO':'metro','Small':'small','Arbuz':'arbuz','AyanMarket':'ayanmarket','Choco Рядом':'ryadom','Fix Price':'fixprice','Детский Мир':'detmir','Жанұя Оптомаркет':'zhanuya','Яндекс Лавка':'lavka'}
store_meta=json.loads((ROOT/'arzan-stores-live.json').read_text(encoding='utf-8'))['stores']
stores=[dict(id=store_ids[s['name']],name=s['name'],logo=s['logo']) for s in store_meta]
maps={'small':'https://2gis.kz/astana/branches/70000001018073339','metro':'https://2gis.kz/astana/firm/70000001018070415','magnum':'https://2gis.kz/astana/branches/70000001055171492','galmart':'https://2gis.kz/astana/branches/70000001021282200'}
for store in stores:
 store['map']=maps.get(store['id'],'https://2gis.kz/astana/search/'+__import__('urllib.parse',fromlist=['quote']).quote(store['name'],safe=''))
 store['mapKind']='branch' if store['id'] in maps else 'search'
normalize=lambda s:re.sub(r'[^\w]','',s.casefold().replace('ё','е'))
def matched(n,pattern):return bool(re.search(pattern,n,re.I))
def assign_sub(name,gid):
 n=name.casefold()
 if gid=='1044':
  if matched(n,r'яйц|жұмыртқа'):return 5
  if matched(n,r'масло|маргарин|спред|сары май'):return 4
  if matched(n,r'\bсыр\b|ірімшік|курт|құрт'):return 3
  if matched(n,r'йогурт|творо|сүзбе|десерт|пудинг|сырок|сырки|даниссимо'):return 2
  if matched(n,r'кефир|айран|сметан|қаймақ|ряжен|қатық|кумыс|қымыз|шұбат|шубат|биолакт|простокваша|снежок|кисломолоч|actimel|\bтан\b'):return 1
  return 0
 if gid=='1045':
  rules=[(9,r'дәмдеу|приправ|бульон|дәм-тат|куркума|зира|кориандр|даршын|корица|перец|бұрыш|тимьян|розмарин|зімбір|лавр'),(10,r'ашытқы|дрожж|разрых|қопсыт|ванил|желатин|крахмал|кондитер|қант ұнтағы|сода|агар|глазур|цукат'),(12,r'таңғы ас|завтрак|хлопья|қауыз|гранола|мюсли|шарик|подушеч'),(11,r'тосап|варень|джем|бал\b|мед\b|арахис паста|джем|повидло|nutella|шоколад паста|медовый|тәтті паста'),(8,r'тұздық|тұздығы|соус|кетчуп|майонез|горчиц|қыша|васаби|хрен|аджик|табаско'),(7,r'сірке|уксус'),(6,r'майы|май\b|масло'),(4,r'қант|сахар|стевия|эритр|фруктоз'),(5,r'^тұз|соль'),(3,r'ұн\b|мука'),(1,r'макарон|паста|спагет|вермиш|кеспе|лапша|рожки|пенне|фарфал|фузилл|тальятел|лингвин|феттуч|каннел|лазан|манты жайма|жайма|гнезда'),(2,r'жасымық|чечев|бұршақ|фасол|нут\b|горох|үрме|маш\b'),(0,r'күріш|рис\b|қарақұмық|греч|тары|пшено|жарма|крупа|сұлы|овсян|булгур|кус-кус|киноа|перлов|арпа')]
  for sub,pattern in rules:
   if matched(n,pattern):return sub
  return 9 if matched(n,r'kotanyi|knorr|магги|maggi|vegeta|айдиго|омега|прип') else 0
 if gid=='1593':
  for sub,pat in [(3,r'батончик|twix|snickers|bounty|mars|kitkat'),(4,r'жевател|сағыз|orbit|драже'),(7,r'печень|піспенан|cookies'),(8,r'вафл'),(9,r'пряник|пірәндік'),(5,r'мармел|желе'),(6,r'зефир|суфле|пастила'),(2,r'карамел|леден'),(0,r'шоколад'),(1,r'конфет|кәмпит')]:
   if matched(n,pat):return sub
  return 10
 if gid=='1591':return 2 if matched(n,r'овощ|көкөніс|смесь|ягод|жеміс') else 1
 if gid=='1405':return 2 if matched(n,r'мыло|сабын') else 0
 if gid=='1281':return 2 if matched(n,r'какао|шашыратқы|цикор|кілегей|сливк|шоколадты') else (1 if matched(n,r'кофе|cappuccino|espresso|caffe|café') else 0)
 return 0

for p in products:
 custom,sub=assignments[str(p['id'])];p['group']=group_map[custom];p['sub']=sub if not custom.startswith('other-') else assign_sub(p['name'],p['group'])

existing_names={normalize(p['name']):p['id'] for p in products}
for p in products:
 if not normalize(p['name']).endswith(normalize(p['size'])):
  existing_names.setdefault(normalize(p['name']+p['size']),p['id'])
source_ids={};dates={}
def get_uuid(url):
 m=re.search(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}',url)
 return m[0] if m else None
for path in ROOT.glob('*import-report.json'):
 for entry in json.loads(path.read_text(encoding='utf-8')).get('products',[]):
  namekey=normalize(entry.get('name',''))
  if namekey in existing_names and entry.get('source'):
   source_ids[get_uuid(entry['source'])]=existing_names[namekey];dates[str(existing_names[namekey])]='2026-10-22'
prior=json.loads((ROOT/'import-report.json').read_text(encoding='utf-8'))
for entry in prior['products']:
 if normalize(entry['name']) in existing_names:source_ids[get_uuid(entry['source'])]=existing_names[normalize(entry['name'])]

new_records=json.loads((ROOT/'arzan-products-live.json').read_text(encoding='utf-8'))
added=0;updated_existing=0;unavailable=0;no_offer=0;next_id=max(p['id'] for p in products)+1;lookup={p['id']:p for p in products}
for row in new_records:
 prices={}
 for offer in row['offers']:
  if offer.get('unavailable') or '—' in offer['store'] or matched(offer['text'],r'жоқ|нет в наличии'):
   unavailable+=1;continue
  sid=store_ids.get(offer['store']);m=re.search(r'(\d[\d\s\u00a0\u202f]*)\s*₸\s*$',offer['text'])
  if not sid or not m:continue
  value=int(re.sub(r'\s','',m[1]));assert value>0
  prices[sid]=min(value,prices.get(sid,value))
 if not prices:no_offer+=1;continue
 group=gid_by_name.get(row['category'])
 if not group or group in ('1279','1280','2084','2012'):continue
 uid=get_uuid(row['url']);pid=source_ids.get(uid) or existing_names.get(normalize(row['name']))
 if pid:
  # Keep old offers intact; add only previously unknown store prices.
  target=offers[str(pid)];before=len(target)
  for sid,value in prices.items():target.setdefault(sid,value)
  updated_existing+=len(target)>before
 else:
  pid=next_id;next_id+=1
  p=dict(id=pid,name=row['name'],brand='',size=row['size'],cat=row['category'],e=next(g['icon'] for g in groups if g['id']==group),img=row['img'],group=group,sub=assign_sub(row['name'],group))
  products.append(p);lookup[pid]=p;offers[str(pid)]=prices;existing_names[normalize(row['name'])]=pid;added+=1
 source_ids[uid]=pid;dates[str(pid)]=row.get('observedAt','2026-11-11')

# Preserve previously published product dates, including an explicitly unknown date.
previous_payload_match=re.search(r'id="qazprice-data">(.*?)</script>',original,re.S)
if previous_payload_match:
 previous_payload=json.loads(previous_payload_match[1]);previous_dates=previous_payload.get('productDates',{})
 for previous_product in previous_payload.get('products',[]):
  previous_id=str(previous_product['id'])
  if previous_id in previous_dates:dates[previous_id]=previous_dates[previous_id]
  else:dates.pop(previous_id,None)

match=re.search(r'<div className="mt-8 pt-4 border-t border-mint.*?">(.*?)</div></div></footer>',base,re.S)
description=match[1] if match else '<p>QazPrice — Жасанды интеллект курсының оқу жобасы (MVP).</p>'
description=description.replace('className=','class=')
logo_match=re.search(r'<img src="(data:image/png;base64,[^"]+)" alt="QazPrice',base)
assert logo_match, 'Original QazPrice logo not found'
logo=logo_match[1]
custom_logo=ROOT/'qazprice-background-logo.png'
if custom_logo.exists():logo='data:image/png;base64,'+base64.b64encode(custom_logo.read_bytes()).decode('ascii')
(ROOT/'qazprice-original-logo.png').write_bytes(base64.b64decode(logo_match[1].split(',',1)[1]))
data=dict(products=products,offers=offers,groups=groups,stores=stores,legacyCategories=legacy,descriptionHtml=description,importDate='2026-11-11',productDates=dates,logo=logo)
assert len(products)==len({p['id'] for p in products})
assert len(lookup)==len(products)
assert all(p['group'] in {g['id'] for g in groups} for p in products)
assert all(0<=p['sub']<max(1,len(next(g for g in groups if g['id']==p['group'])['subs'])) for p in products)
assert all(all(offers[k][sid]==value for sid,value in old.items()) for k,old in old_offers.items())
assert all({k:v for k,v in p.items() if k not in ('group','sub')}==old_products[i] for i,p in enumerate(products[:len(old_products)]))
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
shell=(ROOT/'site-shell.html').read_text(encoding='utf-8')
app=(ROOT/'site-app.js').read_text(encoding='utf-8')
output=shell.replace('__DATA__',payload).replace('__APP__',app)
(ROOT/'QazPrice_preview.html').write_text(output,encoding='utf-8')
report=dict(original_products=len(old_products),new_products=added,total_products=len(products),existing_with_new_stores=updated_existing,source_cards=len(new_records),unavailable_excluded=unavailable,no_available_offers=no_offer,stores=len(stores),categories=len(groups),subcategories=sum(len(g['subs']) for g in groups),all_old_data_preserved=True,category_counts=dict(Counter(p['group'] for p in products)),coverage=json.loads((ROOT/'arzan-products-coverage.json').read_text(encoding='utf-8')))
(ROOT/'replica-build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='coverage'},ensure_ascii=True))
