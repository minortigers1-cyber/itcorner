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

# Set a global User-Agent to stay consistent
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) IPTVPlayer/1.0'}

def check_link(url):
    """Checks if a URL is alive without downloading the content."""
    try:
        # We use HEAD to save bandwidth and time
        response = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        # If HEAD fails, some servers require GET
        try:
            response = requests.get(url, headers=HEADERS, timeout=5, stream=True)
            return response.status_code == 200
        except:
            return False

def extract_group(inf_line):
    match = re.search(r'group-title="([^"]+)"', inf_line)
    return match.group(1) if match else "Uncategorized"

def main():
    groups = {}
    seen_urls = set()
    
    if not os.path.exists("groups"):
        os.makedirs("groups")

    for url in SOURCES:
        print(f"🔍 Fetching source: {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            lines = [line.strip() for line in r.text.splitlines() if line.strip()]
            
            current_inf = None
            for line in lines:
                if line.startswith("#EXTINF"):
                    current_inf = line
                elif not line.startswith("#") and current_inf:
                    full_url = urljoin(url, line)
                    
                    if full_url not in seen_urls:
                        # Validation Step: Only add if the link is active
                        if check_link(full_url):
                            group_name = extract_group(current_inf)
                            if group_name not in groups:
                                groups[group_name] = []
                            groups[group_name].append(f"{current_inf}\n{full_url}")
                            seen_urls.add(full_url)
                            print(f"  ✅ Added: {full_url[:50]}...")
                        else:
                            print(f"  ❌ Dead Link Skipped: {full_url[:50]}...")
                    current_inf = None
        except Exception as e:
            print(f"⚠️ Source Error {url}: {e}")

    # Save logic (same as before)
    with open("all_channels.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for channel_list in groups.values():
            f.write("\n".join(channel_list) + "\n")

    for group_name, channels in groups.items():
        clean_name = re.sub(r'[^\w\s-]', '', group_name).strip().replace(' ', '_')
        with open(f"groups/{clean_name}.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("\n".join(channels))

if __name__ == "__main__":
    main()