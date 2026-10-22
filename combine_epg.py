import gzip
import io
import time
import datetime
import xml.etree.ElementTree as ET
import requests

try:
    from channel_map import CHANNEL_MAPPING
except ImportError:
    CHANNEL_MAPPING = {}

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

seen_channels = set()
channel_elements = {}

# Time window: exactly 24 hours back and 24 hours ahead
now = datetime.datetime.now(datetime.timezone.utc)
min_time_str = (now - datetime.timedelta(days=1)).strftime("%Y%m%d%H%M%S")
max_time_str = (now + datetime.timedelta(days=1)).strftime("%Y%m%d%H%M%S")

for idx, url in enumerate(URLS, 1):
    feed_name = url.split('/')[-1]
    print(f"[{idx}/{len(URLS)}] Fetching {feed_name}...")
    try:
        res = requests.get(url, headers=headers, timeout=60)
        if res.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(res.content)) as gz:
                tree = ET.parse(gz)
                root = tree.getroot()
                
                for elem in root:
                    if elem.tag == "channel":
                        cid = elem.get("id")
                        if cid and cid not in seen_channels:
                            seen_channels.add(cid)
                            channel_elements[cid] = elem
                            combined_root.append(elem)
                    elif elem.tag == "programme":
                        start_time = elem.get("start", "")[:14]
                        # Retain only listings within the 2-day window (-24h to +24h)
                        if min_time_str <= start_time <= max_time_str:
                            # Strip ONLY heavy descriptions; leave titles, genres, ratings, etc.
                            for desc in elem.findall("desc"):
                                elem.remove(desc)
                            combined_root.append(elem)
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
    time.sleep(0.5)

print(f"Total channels retained: {len(seen_channels)}")

# Preserve regional IDs in display-name
for cid, ch_elem in channel_elements.items():
    existing_names = [dn.text for dn in ch_elem.findall("display-name") if dn.text]
    if cid not in existing_names:
        id_dn = ET.Element("display-name")
        id_dn.text = cid
        ch_elem.insert(0, id_dn)

# Inject playlist mappings for auto-match
injected_count = 0
for raw_name, target_id in CHANNEL_MAPPING.items():
    if target_id in channel_elements:
        dn = ET.Element("display-name")
        dn.text = raw_name
        channel_elements[target_id].append(dn)
        injected_count += 1

print(f"Injected {injected_count} playlist aliases.")

print("Saving trimmed combined EPG...")
with gzip.open(OUTPUT_FILE, "wb", compresslevel=9) as f_out:
    ET.ElementTree(combined_root).write(f_out, encoding="utf-8", xml_declaration=True)

print("Done! Optimized combined_epg.xml.gz generated.")
