import json,re,urllib.parse,urllib.request,xml.etree.ElementTree as ET
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
tz=timezone(timedelta(hours=3));now=datetime.now(tz);new=[]
for q in NEWS:add_feed("https://news.google.com/rss/search?q="+urllib.parse.quote(q)+"&hl=tr&gl=TR&ceid=TR:tr","Haber",now,new)
for platform,q in SOCIAL:add_feed("https://www.bing.com/search?format=rss&q="+urllib.parse.quote(q),platform,now,new)
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
items=sorted(merged.values(),key=lambda x:x["published"],reverse=True)[:1500]
for i,e in enumerate(items,1):e["id"]=i
with open("data/events.json","w",encoding="utf-8") as f:json.dump({"updated_at":now.isoformat(),"events":items,"sources":["Google News RSS","X (indekslenen açık gönderiler)","Facebook (indekslenen açık sayfa/gruplar)","Instagram","YouTube","TikTok"]},f,ensure_ascii=False,indent=2)
