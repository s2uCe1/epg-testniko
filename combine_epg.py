import gzip
import io
import xml.etree.ElementTree as ET
import requests
from channel_map import CHANNEL_MAPPING

URLS = [
    "https://www.open-epg.com/files/albania.xml.gz",
    "https://www.open-epg.com/files/australia.xml.gz",
    "https://www.open-epg.com/files/austria.xml.gz",
    "https://www.open-epg.com/files/bosnia.xml.gz",
    "https://www.open-epg.com/files/brazil1.xml.gz",
    "https://www.open-epg.com/files/bulgaria2.xml.gz",
    "https://www.open-epg.com/files/canada.xml.gz",
    "https://www.open-epg.com/files/china1.xml.gz",
    "https://www.open-epg.com/files/colombia1.xml.gz",
    "https://www.open-epg.com/files/croatia.xml.gz",
    "https://www.open-epg.com/files/cyprus1.xml.gz",
    "https://www.open-epg.com/files/czech3.xml.gz",
    "https://www.open-epg.com/files/denmark.xml.gz",
    "https://www.open-epg.com/files/egypt1.xml.gz",
    "https://www.open-epg.com/files/egypt2.xml.gz",
    "https://www.open-epg.com/files/germany.xml.gz",
    "https://www.open-epg.com/files/hungary1.xml.gz",
    "https://www.open-epg.com/files/iceland.xml.gz",
    "https://www.open-epg.com/files/ireland.xml.gz",
    "https://www.open-epg.com/files/italy1.xml.gz",
    "https://www.open-epg.com/files/italy2.xml.gz",
    "https://www.open-epg.com/files/italy3.xml.gz",
    "https://www.open-epg.com/files/italy4.xml.gz",
    "https://www.open-epg.com/files/italy5.xml.gz",
    "https://www.open-epg.com/files/italy7.xml.gz",
    "https://www.open-epg.com/files/italy8.xml.gz",
    "https://www.open-epg.com/files/japan1.xml.gz",
    "https://www.open-epg.com/files/korea1.xml.gz",
    "https://www.open-epg.com/files/macedonia1.xml.gz",
    "https://www.open-epg.com/files/mexico1.xml.gz",
    "https://www.open-epg.com/files/mexico2.xml.gz",
    "https://www.open-epg.com/files/montenegro1.xml.gz",
    "https://www.open-epg.com/files/morocco1.xml.gz",
    "https://www.open-epg.com/files/morocco2.xml.gz",
    "https://www.open-epg.com/files/newzealand.xml.gz",
    "https://www.open-epg.com/files/palestine1.xml.gz",
    "https://www.open-epg.com/files/poland1.xml.gz",
    "https://www.open-epg.com/files/portugal2.xml.gz",
    "https://www.open-epg.com/files/qatar1.xml.gz",
    "https://www.open-epg.com/files/qatar2.xml.gz",
    "https://www.open-epg.com/files/qatar3.xml.gz",
    "https://www.open-epg.com/files/qatar4.xml.gz",
    "https://www.open-epg.com/files/qatar5.xml.gz",
    "https://www.open-epg.com/files/qatar6.xml.gz",
    "https://www.open-epg.com/files/russia.xml.gz",
    "https://www.open-epg.com/files/saudiarabia2.xml.gz",
    "https://www.open-epg.com/files/saudiarabia3.xml.gz",
    "https://www.open-epg.com/files/saudiarabia4.xml.gz",
    "https://www.open-epg.com/files/saudiarabia5.xml.gz",
    "https://www.open-epg.com/files/saudiarabia6.xml.gz",
    "https://www.open-epg.com/files/serbia1.xml.gz",
    "https://www.open-epg.com/files/serbia2.xml.gz",
    "https://www.open-epg.com/files/serbia4.xml.gz",
    "https://www.open-epg.com/files/serbia5.xml.gz",
    "https://www.open-epg.com/files/slovenia.xml.gz",
    "https://www.open-epg.com/files/spain.xml.gz",
    "https://www.open-epg.com/files/sports1.xml.gz",
    "https://www.open-epg.com/files/sports4.xml.gz",
    "https://www.open-epg.com/files/switzerland3.xml.gz",
    "https://www.open-epg.com/files/turkey1.xml.gz",
    "https://www.open-epg.com/files/turkey2.xml.gz",
    "https://www.open-epg.com/files/uae6.xml.gz",
    "https://www.open-epg.com/files/ukraine.xml.gz",
    "https://www.open-epg.com/files/unitedkingdom.xml.gz",
    "https://www.open-epg.com/files/unitedstates1.xml.gz",
    "https://www.open-epg.com/files/unitedstates10.xml.gz",
    "https://www.open-epg.com/files/unitedstates11.xml.gz",
    "https://www.open-epg.com/files/unitedstates2.xml.gz",
    "https://www.open-epg.com/files/unitedstates3.xml.gz",
    "https://www.open-epg.com/files/unitedstates4.xml.gz",
    "https://www.open-epg.com/files/unitedstates5.xml.gz",
    "https://www.open-epg.com/files/unitedstates6.xml.gz",
    "https://www.open-epg.com/files/uzbekistan1.xml.gz",
    "https://www.open-epg.com/files/venezuela1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_AE1.xml.gz",
]

OUTPUT_FILE = "combined_epg.xml.gz"
headers = {"User-Agent": "Mozilla/5.0"}
combined_root = ET.Element("tv")

needed_ids = set(CHANNEL_MAPPING.values())
print(f"Targeting {len(needed_ids)} unique channels.")

for idx, url in enumerate(URLS, 1):
    feed_name = url.split('/')[-1]
    print(f"[{idx}/{len(URLS)}] Fetching {feed_name}...")
    try:
        res = requests.get(url, headers=headers, timeout=60)
        if res.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(res.content)) as gz:
                tree = ET.parse(gz)
                root = tree.getroot()
                
                feed_channel_ids = {ch.get("id") for ch in root.findall("channel")}
                matches = feed_channel_ids.intersection(needed_ids)
                
                if matches:
                    print(f"-> Found {len(matches)} matched channels in {feed_name}")
                    for elem in root:
                        if elem.tag == "channel" and elem.get("id") in needed_ids:
                            combined_root.append(elem)
                        elif elem.tag == "programme" and elem.get("channel") in needed_ids:
                            combined_root.append(elem)
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")

# Ensure every channel retains its explicit channel ID as the primary display-name
channel_elements = {ch.get("id"): ch for ch in combined_root.findall("channel")}

for cid, ch_elem in channel_elements.items():
    existing_names = [dn.text for dn in ch_elem.findall("display-name") if dn.text]
    
    # Place channel ID (e.g. HRT1.hr, SLO1.si) right at the top of display-name tags
    if cid not in existing_names:
        id_dn = ET.Element("display-name")
        id_dn.text = cid
        ch_elem.insert(0, id_dn)

print("Writing XML with native regional IDs preserved...")
with gzip.open(OUTPUT_FILE, "wb") as f_out:
    ET.ElementTree(combined_root).write(f_out, encoding="utf-8", xml_declaration=True)

print("Done! combined_epg.xml.gz updated.")
