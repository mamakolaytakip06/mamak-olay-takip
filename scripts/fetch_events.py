import json,re,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from datetime import datetime,timezone,timedelta
Q=["Mamak Ankara kaza OR yangın OR polis OR ambulans","Mamak son dakika","Mamak trafik OR yol kapalı OR altyapı","Tuzluçayır OR Akdere OR Abidinpaşa OR Başak Mamak"]
C=[("Yangın","🔥",["yangın","duman","alev"]),("Trafik","🚗",["kaza","çarpış","trafik"]),("Güvenlik","👮",["polis","silah","kavga","operasyon","hırsız"]),("Sağlık","🚑",["ambulans","yaralı","sağlık"]),("Yol","🚧",["yol","kapalı","çalışma"]),("Altyapı","⚡",["elektrik","su kesinti","doğalgaz"])]
def clean(s): return re.sub(r"<[^>]+>"," ",s or "").strip()
def classify(t):
 t=t.lower()
 for c,i,ks in C:
  if any(k in t for k in ks): return c,i
 return "Diğer","⚠️"
now=datetime.now(timezone(timedelta(hours=3))); items=[]; seen=set()
for q in Q:
 try:
  u="https://news.google.com/rss/search?q="+urllib.parse.quote(q)+"&hl=tr&gl=TR&ceid=TR:tr"
  root=ET.fromstring(urllib.request.urlopen(u,timeout=20).read())
  for x in root.findall(".//item"):
   title=clean(x.findtext("title")); link=x.findtext("link") or ""; pub=x.findtext("pubDate") or ""
   try: dt=datetime.strptime(pub,"%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc).astimezone(now.tzinfo)
   except: continue
   if dt.date()!=now.date() or "mamak" not in (title+" "+clean(x.findtext("description"))).lower(): continue
   key=re.sub(r"\W+","",title.lower())[:70]
   if key in seen: continue
   seen.add(key); cat,icon=classify(title); src=x.find("source"); source=src.text if src is not None else "Açık web"
   items.append({"id":len(items)+1,"category":cat,"icon":icon,"title":title,"location":"Mamak / Ankara","published":dt.isoformat(),"confidence":72 if source!="Açık web" else 55,"sources":1,"status":"Muhtemel" if source!="Açık web" else "Tek kaynak","summary":source+" kaynağında yayımlanan güncel açık web kaydı.","url":link})
 except Exception as e: pass
items.sort(key=lambda x:x["published"],reverse=True)
with open("data/events.json","w",encoding="utf-8") as f: json.dump({"updated_at":now.isoformat(),"events":items[:60]},f,ensure_ascii=False,indent=2)
