import requests
import re

# List all your source M3U links here
SOURCES = [
    "https://iptv-org.github.io/iptv/countries/us.m3u",
    "https://iptv-org.github.io/iptv/countries/uk.m3u",
    "https://raw.githubusercontent.com/freetv-org/samsung-tv-plus/main/playlists/samsung-tv-plus-all.m3u"
]

def main():
    combined_content = ["#EXTM3U"]
    seen_urls = set()

    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                lines = r.text.splitlines()
                current_info = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("#EXTINF"):
                        current_info = line
                    elif line.startswith("http") and current_info:
                        if line not in seen_urls:
                            combined_content.append(current_info)
                            combined_content.append(line)
                            seen_urls.add(line)
                        current_info = None
            print(f"Successfully processed: {url}")
        except Exception as e:
            print(f"Error skipping {url}: {e}")

    with open("all_channels.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))

if __name__ == "__main__":
    main()