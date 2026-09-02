import json,re,os,urllib.parse,urllib.request,xml.etree.ElementTree as ET,unicodedata
from difflib import SequenceMatcher
from datetime import datetime,timezone,timedelta
NEWS=[
"Mamak Ankara cinayet OR kavga OR silahlı OR taciz",
"Mamak Ankara trafik kazası OR yangın OR polis OR ambulans",
"Mamak Ankara hırsızlık OR dolandırıcılık OR uyuşturucu OR kayıp",
"Mamak son dakika olay","Mamak trafik OR yol kapalı OR altyapı",
"Tuzluçayır OR Akdere OR Abidinpaşa OR Başak Mamak olay"]
SOCIAL=[
("X","site:x.com Mamak Ankara (kaza OR yangın OR polis OR kavga OR son dakika)"),
("X","site:x.com/ankara_cevirme Mamak"),("X","site:x.com/EmniyetAnkara Mamak"),
("X","site:x.com/radyotrafik06 Mamak"),("X","site:x.com/ankaratrafikcev Mamak"),
("Facebook","site:facebook.com Mamak Ankara son dakika olay"),
("Facebook","site:facebook.com/mamaktime Mamak"),("Facebook","site:facebook.com/groups/1067945807725915 Mamak"),
("Facebook","site:facebook.com/groups/233752440399327 Mamak"),("Facebook","site:facebook.com/mamakbelediyesi Mamak"),
("Instagram","site:instagram.com/ankaradatrafik Mamak"),("Instagram","site:instagram.com/ankara.sondakika Mamak"),
("Instagram","site:instagram.com/mamak.sondakika Mamak"),("Instagram","site:instagram.com/ankaradantrafik Mamak"),
("Instagram","site:instagram.com/ankarasondakikahaberleri.06 Mamak"),
("YouTube","site:youtube.com Mamak Ankara son dakika olay"),
("TikTok","site:tiktok.com Mamak Ankara kaza yangın polis")

]

ALERT_QUERY_TEMPLATES=[
"site:x.com Mamak (cinayet OR kavga OR kaza OR yangın OR polis)",
"site:facebook.com Mamak (cinayet OR kavga OR kaza OR yangın OR polis)",
"site:instagram.com Mamak (cinayet OR kavga OR kaza OR yangın OR polis)",
"site:x.com \"Mamak son dakika\"",
"site:facebook.com \"Mamak son dakika\"",
"site:instagram.com \"Mamak son dakika\"",
"site:x.com Ankara Mamak asayiş",
"site:facebook.com Ankara Mamak asayiş",
"site:instagram.com Ankara Mamak asayiş"
]


NEIGHBORHOODS={
"Tuzluçayır":(39.9169,32.9430),"Akdere":(39.9148,32.9158),"Abidinpaşa":(39.9209,32.9072),
"Başak":(39.9369,32.9920),"Boğaziçi":(39.9480,32.9420),"Cengizhan":(39.9381,32.9565),
"Demirlibahçe":(39.9277,32.8957),"Durali Alıç":(39.9445,32.9681),"General Zeki Doğan":(39.9258,32.9527),
"Kayaş":(39.9217,32.9971),"Kutlu":(39.9108,32.9360),"Mutlu":(39.9056,32.9248),
"Şafaktepe":(39.9297,32.9302),"Şahintepe":(39.9482,32.9830),"Türközü":(39.9009,32.9144),
"Üreğil":(39.9370,32.9820),"Altıağaç":(39.9453,32.9285),"Ekin":(39.9467,32.9490),
"Hüseyingazi":(39.9587,32.9440),"Gülveren":(39.9361,32.9161),"Misket":(39.9585,32.9683),
"Natoyolu":(39.9087,32.9488),"Yeşilbayır":(39.9496,33.0065)
}

C=[("Cinayet","⚫",["cinayet","öldürüldü","öldürdü","ölü bulundu","ceset"]),("İntihar","🟣",["intihar","yaşamına son"]),("Terör","🚨",["terör","terörist","örgüt operasyon","bombalı"]),("Taciz","🟣",["taciz","cinsel saldırı","istismar"]),("Düğünde Silah","🔫",["düğünde silah","havaya ateş","maganda"]),("Silahlı Olay","🔫",["silahlı","silah","kurşun","ateş aç"]),("Kavga","🥊",["kavga","darp","saldırı"]),("Trafik Kazası","🚗",["trafik kazası","kaza","çarpış","araç devr"]),("Hırsızlık","🕵️",["hırsız","çaldı","gasp","soygun"]),("Dolandırıcılık","💳",["dolandır"]),("Uyuşturucu","🚔",["uyuşturucu","narkotik"]),("Kayıp Kişi","👤",["kayıp","aranıyor"]),("Yangın","🔥",["yangın","duman","alev"]),("Sağlık","🚑",["ambulans","yaralı","sağlık"]),("Yol","🚧",["yol kapalı","yol çalışma"]),("Altyapı","⚡",["elektrik","su kesinti","doğalgaz"]),("Asayiş","👮",["polis","emniyet","asayiş","gözaltı","tutuklandı","yakalandı","operasyon","şüpheli","suç"])]
RELEVANT=["cinayet","öldür","ceset","intihar","terör","bomba","taciz","cinsel saldırı","istismar","silah","kurşun","ateş aç","kavga","darp","saldırı","trafik kazası","kaza","çarpış","devrildi","hırsız","gasp","soygun","dolandır","uyuşturucu","narkotik","kayıp","yangın","alev","ambulans","yaralı","polis","emniyet","asayiş","gözaltı","tutuk","yakalandı","operasyon","şüpheli","suç","patlama","rehin","kaçakçılık","bıçak"]
BLOCK=["menu","food","restaurant","restoran","yemek","kampanya","indirim","satılık","kiralık","maç","transfer","konser","etkinlik","iş ilanı","job"]
def clean(s): return re.sub(r"<[^>]+>"," ",s or "").strip()
def relevant(t):
 t=t.lower()
 return any(k in t for k in RELEVANT) and not any(k in t for k in BLOCK)
def classify_all(t):
 t=t.lower();found=[];icon="⚠️"
 for c,i,ks in C:
  if any(k in t for k in ks):
   found.append(c)
   if icon=="⚠️":icon=i
 return (found or ["Diğer"]),icon
def classify(t):
 cats,icon=classify_all(t)
 return cats[0],icon
def parse_date(s,tz):
 for fmt in ("%a, %d %b %Y %H:%M:%S %Z","%a, %d %b %Y %H:%M:%S %z"):
  try:return datetime.strptime(s,fmt).replace(tzinfo=timezone.utc).astimezone(tz) if fmt.endswith("%Z") else datetime.strptime(s,fmt).astimezone(tz)
  except:pass
 return None
def add_feed(url,platform,now,out):
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
  root=ET.fromstring(urllib.request.urlopen(req,timeout=25).read())
  for x in root.findall(".//item"):
   title=clean(x.findtext("title"));desc=clean(x.findtext("description"));link=x.findtext("link") or "";dt=parse_date(x.findtext("pubDate") or "",now.tzinfo)
   if not dt or now-dt>timedelta(days=365) or "mamak" not in (title+" "+desc).lower() or not relevant(title+" "+desc):continue
   categories,icon=classify_all(title+" "+desc);cat=categories[0];src=x.find("source");source=src.text if src is not None and src.text else platform
   out.append({"category":cat,"categories":categories,"icon":icon,"title":title,"location":"Mamak / Ankara","published":dt.isoformat(),"confidence":75 if platform=="Haber" else 60,"sources":1,"status":"Muhtemel" if platform=="Haber" else "Sosyal medya / doğrulanmamış","summary":source+" üzerinden bulunan herkese açık kayıt.","url":link,"platform":platform})
 except Exception:pass
def detect_platform(link):
 low=link.lower()
 if "x.com/" in low or "twitter.com/" in low:return "X"
 if "facebook.com/" in low or "fb.com/" in low:return "Facebook"
 if "instagram.com/" in low:return "Instagram"
 if "youtube.com/" in low or "youtu.be/" in low:return "YouTube"
 if "tiktok.com/" in low:return "TikTok"
 return "Google Alerts"
def add_alert_feed(url,now,out):
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
  root=ET.fromstring(urllib.request.urlopen(req,timeout=25).read())
  entries=root.findall(".//{*}entry")+root.findall(".//item")
  for x in entries:
   title=clean(x.findtext("{*}title") or x.findtext("title"))
   desc=clean(x.findtext("{*}content") or x.findtext("{*}summary") or x.findtext("description"))
   node=x.find("{*}link");link=(node.get("href") if node is not None else None) or x.findtext("link") or ""
   qs=urllib.parse.parse_qs(urllib.parse.urlparse(link).query);link=(qs.get("url") or qs.get("q") or [link])[0]
   rawdate=x.findtext("{*}published") or x.findtext("{*}updated") or x.findtext("pubDate") or ""
   try:dt=datetime.fromisoformat(rawdate.replace("Z","+00:00")).astimezone(now.tzinfo)
   except:dt=parse_date(rawdate,now.tzinfo)
   text=(title+" "+desc).lower()
   if not dt or now-dt>timedelta(days=365) or "mamak" not in text or not relevant(text):continue
   platform=detect_platform(link)
   categories,icon=classify_all(text);cat=categories[0]
   out.append({"category":cat,"categories":categories,"icon":icon,"title":title,"location":"Mamak / Ankara","published":dt.isoformat(),"confidence":60,"sources":1,"status":"Sosyal medya / doğrulanmamış","summary":"Google Alerts üzerinden bulunan herkese açık "+platform+" kaydı.","url":link,"platform":platform})
 except Exception:pass
STOP_WORDS={"mamak","ankara","son","dakika","haber","haberi","olay","olayi","ilcesi","ilcesinde","mahallesi","icin","ile","bir","ve","da","de","ta","te","the"}
SYNONYMS={"agaclik":"orman","koruluk":"orman","alevler":"yangin","alev":"yangin","itfaiye":"yangin","carpisti":"kaza","carpisma":"kaza","devrildi":"kaza","gozaltina":"gozalti","yakalandi":"gozalti"}

def ascii_text(value):
 value=(value or "").translate(str.maketrans("çğıöşüÇĞİÖŞÜ","cgiosuCGIOSU"))
 value=unicodedata.normalize("NFKD",value).encode("ascii","ignore").decode().lower()
 return re.sub(r"[^a-z0-9 ]+"," ",value)

def title_tokens(title):
 base=(title or "").rsplit(" - ",1)[0]
 words=[]
 for word in ascii_text(base).split():
  word=SYNONYMS.get(word,word)
  if len(word)>=3 and word not in STOP_WORDS:words.append(word)
 return set(words)

def subtype(title):
 t=ascii_text(title)
 groups=[("orman",("orman","agaclik","koruluk")),("cati",("cati",)),("bina",("bina","apartman","ev ","fabrika","depo")),("arac",("arac","otomobil","minibus","otobus","kamyon")),("motosiklet",("motosiklet","motor")),("yaya",("yaya","cocuk")),("silah",("silah","kursun","ates ac")),("bicak",("bicak",))]
 return next((name for name,keys in groups if any(k in t for k in keys)),"")

def same_event(a,b):
 try:
  da=datetime.fromisoformat(a["published"]);db=datetime.fromisoformat(b["published"])
  if abs((da-db).total_seconds())>60*60*48:return False
 except:return False
 ca=set(a.get("categories") or [a.get("category")]);cb=set(b.get("categories") or [b.get("category")])
 if not (ca&cb):return False
 na=ascii_text((a.get("title") or "").rsplit(" - ",1)[0]);nb=ascii_text((b.get("title") or "").rsplit(" - ",1)[0])
 if na==nb:return True
 ta=title_tokens(a.get("title",""));tb=title_tokens(b.get("title",""))
 if not ta or not tb:return False
 inter=len(ta&tb);contain=inter/min(len(ta),len(tb));jac=inter/len(ta|tb)
 if SequenceMatcher(None,na,nb).ratio()>=0.72:return True
 if inter>=3 and contain>=0.55 and jac>=0.32:return True
 sa=subtype(a.get("title",""));sb=subtype(b.get("title",""))
 primary=a.get("category")
 if sa and sa==sb and primary==b.get("category") and da.date()==db.date() and sa in {"orman","cati"}:return True
 return bool(sa and sa==sb and primary==b.get("category") and da.date()==db.date() and inter>=1)

def add_location(e):
 text=(e.get("title","")+" "+e.get("summary","")).lower()
 found=next(((name,coords) for name,coords in NEIGHBORHOODS.items() if name.lower() in text),None)
 if found:
  e["neighborhood"]=found[0];e["lat"],e["lon"]=found[1];e["location"]=found[0]+" / Mamak / Ankara";e["location_precision"]="mahalle"
 else:
  e["neighborhood"]="Mamak Geneli";e["lat"],e["lon"]=39.9308,32.9307;e["location"]="Mamak / Ankara";e["location_precision"]="ilçe"
 return e

def source_entries(e):
 existing=e.get("source_links") or []
 current={"platform":e.get("platform") or "Haber","title":e.get("title",""),"url":e.get("url",""),"published":e.get("published","")}
 result=[];positions={}
 for x in existing+[current]:
  key=x.get("url") or x.get("title")
  if not key:continue
  if key in positions:
   saved=result[positions[key]]
   for field in ("platform","title","url","published"):
    if not saved.get(field) and x.get(field):saved[field]=x[field]
  else:positions[key]=len(result);result.append(dict(x))
 return result

def combine_events(target,e):
 links=source_entries(target)
 for x in source_entries(e):
  if not any(y.get("url")==x.get("url") for y in links):links.append(x)
 target["source_links"]=links;target["sources"]=len(links)
 target["confidence"]=max(target.get("confidence",0),e.get("confidence",0))
 target["categories"]=list(dict.fromkeys((target.get("categories") or [target.get("category")])+(e.get("categories") or [e.get("category")])))
 if len(e.get("title",""))>len(target.get("title","")):target["title"]=e["title"]
 target["published"]=min(target["published"],e["published"])
 target["last_updated"]=max(target.get("last_updated",target["published"]),e.get("last_updated",e["published"]))
 if len(links)>1:target["summary"]=str(len(links))+" farklı açık kaynakta bulunan aynı olay tek kayıtta birleştirildi."
 return target

def deduplicate_events(events):
 result=[]
 for e in sorted(events,key=lambda x:x.get("published",""),reverse=True):
  match=next((x for x in result if same_event(x,e)),None)
  if match:combine_events(match,e)
  else:
   e["source_links"]=source_entries(e);e["sources"]=len(e["source_links"]);result.append(e)
 final=[]
 for e in result:
  try:key=(datetime.fromisoformat(e["published"]).date(),e.get("category"),subtype(e.get("title","")))
  except:key=(None,None,None)
  match=next((x for x in final if key[0] and key[1]=="Yangın" and key[2] in {"orman","cati"} and x["_bucket"]==key),None)
  if match:combine_events(match,e)
  else:e["_bucket"]=key;final.append(e)
 for e in final:e.pop("_bucket",None)
 return final

tz=timezone(timedelta(hours=3));now=datetime.now(tz);new=[]
for q in NEWS:add_feed("https://news.google.com/rss/search?q="+urllib.parse.quote(q)+"&hl=tr&gl=TR&ceid=TR:tr","Haber",now,new)
for platform,q in SOCIAL:add_feed("https://www.bing.com/search?format=rss&q="+urllib.parse.quote(q),platform,now,new)
raw_alert_urls=[u.strip() for u in re.split(r"[\n,;]+",os.getenv("GOOGLE_ALERT_FEEDS","")) if u.strip()]
alert_urls=list(dict.fromkeys(u for u in raw_alert_urls if re.match(r"^https://[^/]*google[^/]*/alerts/feeds/",u,re.I)))
for alert_url in alert_urls:add_alert_feed(alert_url,now,new)
try:
 with open("data/events.json",encoding="utf-8") as f:old=json.load(f).get("events",[])
except:old=[]
merged={};cut=now-timedelta(days=365)
for e in old+new:
 if e.get("platform") in ("Telegram","Threads") or not relevant(e.get("title","")+" "+e.get("summary","")):continue
 try:
  if datetime.fromisoformat(e["published"])<cut:continue
 except:continue
 key=e.get("url") or re.sub(r"\W+","",e.get("title","").lower())[:90]
 merged[key]=e
items=deduplicate_events(sorted(merged.values(),key=lambda x:x["published"],reverse=True))[:1500]
for i,e in enumerate(items,1):add_location(e);e["id"]=i
with open("data/events.json","w",encoding="utf-8") as f:json.dump({"updated_at":now.isoformat(),"events":items,"google_alerts_active":bool(alert_urls),"google_alert_feed_count":len(alert_urls),"google_alert_invalid_count":len(raw_alert_urls)-len(alert_urls),"google_alert_query_count":len(ALERT_QUERY_TEMPLATES),"sources":["Google Alerts RSS","Google News RSS","X (indekslenen açık gönderiler)","Facebook (indekslenen açık sayfa/gruplar)","Instagram","YouTube","TikTok"]},f,ensure_ascii=False,indent=2)
