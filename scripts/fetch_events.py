import json,re,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from datetime import datetime,timezone,timedelta
Q=[
"Mamak Ankara cinayet OR kavga OR silahlı OR taciz",
"Mamak Ankara trafik kazası OR yangın OR polis OR ambulans",
"Mamak Ankara hırsızlık OR dolandırıcılık OR uyuşturucu OR kayıp",
"Mamak son dakika olay",
"Mamak trafik OR yol kapalı OR altyapı",
"Tuzluçayır OR Akdere OR Abidinpaşa OR Başak Mamak olay"
]
C=[
("Cinayet","⚫",["cinayet","öldürüldü","öldürdü","ölü bulundu"]),
("Taciz","🟣",["taciz","cinsel saldırı","istismar"]),
("Düğünde Silah","🔫",["düğün","havaya ateş","maganda"]),
("Silahlı Olay","🔫",["silahlı","silah","kurşun","ateş aç"]),
("Kavga","🥊",["kavga","darp","saldırı"]),
("Trafik Kazası","🚗",["trafik kazası","kaza","çarpış","araç devr"]),
("Hırsızlık","🕵️",["hırsız","çaldı","gasp"]),
("Dolandırıcılık","💳",["dolandır"]),
("Uyuşturucu","🚔",["uyuşturucu","narkotik"]),
("Kayıp Kişi","👤",["kayıp","aranıyor"]),
("Yangın","🔥",["yangın","duman","alev"]),
("Sağlık","🚑",["ambulans","yaralı","sağlık"]),
("Yol","🚧",["yol kapalı","yol çalışma"]),
("Altyapı","⚡",["elektrik","su kesinti","doğalgaz"])
]
def clean(s): return re.sub(r"<[^>]+>"," ",s or "").strip()
def classify(t):
 t=t.lower()
 for c,i,ks in C:
  if any(k in t for k in ks): return c,i
 return "Diğer","⚠️"
tz=timezone(timedelta(hours=3));now=datetime.now(tz);new=[]
for q in Q:
 try:
  u="https://news.google.com/rss/search?q="+urllib.parse.quote(q)+"&hl=tr&gl=TR&ceid=TR:tr"
  root=ET.fromstring(urllib.request.urlopen(u,timeout=20).read())
  for x in root.findall(".//item"):
   title=clean(x.findtext("title"));desc=clean(x.findtext("description"));link=x.findtext("link") or "";pub=x.findtext("pubDate") or ""
   try: dt=datetime.strptime(pub,"%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc).astimezone(tz)
   except: continue
   if now-dt>timedelta(days=365) or "mamak" not in (title+" "+desc).lower(): continue
   cat,icon=classify(title+" "+desc);src=x.find("source");source=src.text if src is not None else "Açık web"
   new.append({"category":cat,"icon":icon,"title":title,"location":"Mamak / Ankara","published":dt.isoformat(),"confidence":72 if source!="Açık web" else 55,"sources":1,"status":"Muhtemel" if source!="Açık web" else "Tek kaynak","summary":source+" kaynağında yayımlanan açık web kaydı.","url":link})
 except Exception: pass
try:
 with open("data/events.json",encoding="utf-8") as f: old=json.load(f).get("events",[])
except: old=[]
merged={};cut=now-timedelta(days=365)
for e in old+new:
 try:
  if datetime.fromisoformat(e["published"])<cut: continue
 except: continue
 key=e.get("url") or re.sub(r"\W+","",e.get("title","").lower())[:90]
 merged[key]=e
items=sorted(merged.values(),key=lambda x:x["published"],reverse=True)[:1000]
for i,e in enumerate(items,1): e["id"]=i
with open("data/events.json","w",encoding="utf-8") as f: json.dump({"updated_at":now.isoformat(),"events":items},f,ensure_ascii=False,indent=2)
