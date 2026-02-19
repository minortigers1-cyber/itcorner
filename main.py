import requests
import re
import os
from urllib.parse import urljoin

SOURCES = [
    "http://103.229.254.25:7001/playlist.m3u8",
    "https://da.gd/NTOW8q",
    "http://190.61.63.140:12142/playlist.m3u8",
    "https://da.gd/uuaWX0",
    "https://is.gd/u2EgWa.m3u",
    "https://is.gd/y7OKsu.m3u8",
    "https://is.gd/AUxIDc.m3u"
]

def extract_group(inf_line):
    """Extracts group-title using regex, defaults to 'Uncategorized'."""
    match = re.search(r'group-title="([^"]+)"', inf_line)
    return match.group(1) if match else "Uncategorized"

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) IPTVPlayer/1.0'}
    groups = {}  # Dictionary to hold channels by group
    seen_urls = set()
    
    # Create a directory for individual group files
    if not os.path.exists("groups"):
        os.makedirs("groups")

    for url in SOURCES:
        try:
            r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            r.raise_for_status()
            lines = [line.strip() for line in r.text.splitlines() if line.strip()]
            
            current_inf = None
            for line in lines:
                if line.startswith("#EXTINF"):
                    current_inf = line
                elif not line.startswith("#") and current_inf:
                    full_url = urljoin(url, line)
                    if full_url not in seen_urls:
                        group_name = extract_group(current_inf)
                        
                        if group_name not in groups:
                            groups[group_name] = []
                        
                        groups[group_name].append(f"{current_inf}\n{full_url}")
                        seen_urls.add(full_url)
                    current_inf = None
            print(f"✅ Parsed: {url}")
        except Exception as e:
            print(f"❌ Error at {url}: {e}")

    # 1. Save the Master Playlist
    with open("all_channels.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for channel_list in groups.values():
            f.write("\n".join(channel_list) + "\n")

    # 2. Save Individual Group Files
    for group_name, channels in groups.items():
        # Clean filename (remove special characters)
        clean_name = re.sub(r'[^\w\s-]', '', group_name).strip().replace(' ', '_')
        with open(f"groups/{clean_name}.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("\n".join(channels))

    print(f"\n✨ Success! Created {len(groups)} group files in the /groups folder.")

if __name__ == "__main__":
    main()