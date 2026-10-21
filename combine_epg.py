import gzip
import io
import xml.etree.ElementTree as ET
import requests

# Open-EPG source links for Croatia and Slovenia
URLS = [
    "https://www.open-epg.com/files/croatia.xml.gz",
    "https://www.open-epg.com/files/slovenia.xml.gz",
]

OUTPUT_FILE = "combined_epg.xml.gz"

combined_root = ET.Element("tv")
headers = {"User-Agent": "Mozilla/5.0"}

for url in URLS:
    print(f"Fetching {url}...")
    try:
        res = requests.get(url, headers=headers, timeout=60)
        if res.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(res.content)) as gz:
                tree = ET.parse(gz)
                for elem in tree.getroot():
                    combined_root.append(elem)
            print(f"Successfully merged {url}")
        else:
            print(f"Failed to fetch {url} (Status: {res.status_code})")
    except Exception as e:
        print(f"Error processing {url}: {e}")

print("Writing combined output...")
with gzip.open(OUTPUT_FILE, "wb") as f_out:
    ET.ElementTree(combined_root).write(f_out, encoding="utf-8", xml_declaration=True)

print(f"Finished: {OUTPUT_FILE} created successfully.")
