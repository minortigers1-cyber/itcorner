import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor

# Suppress SSL warnings for servers with invalid certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SOURCES = [
    "http://103.229.254.25:7001/playlist.m3u8",
    "https://da.gd/NTOW8q",
    "http://190.61.63.140:12142/playlist.m3u8",
    "https://da.gd/uuaWX0",
    "https://is.gd/u2EgWa.m3u",
    "https://is.gd/y7OKsu.m3u8",
    "https://is.gd/AUxIDc.m3u"
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) IPTVPlayer/1.0'}

def is_alive(url):
    """Checks if a stream URL is online using a HEAD request."""
    try:
        # Added headers and verify=False to prevent blocks/crashes
        response = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True, verify=False)
        return response.status_code < 400
    except:
        return False

def process_source(url):
    """Downloads a playlist and extracts potential channel info."""
    found_channels = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        if r.status_code == 200:
            lines = r.text.splitlines()
            is_list = any(line.startswith("#EXTINF") for line in lines)
            
            if not is_list:
                found_channels.append((f'#EXTINF:-1 group-title="Direct Links",{url.split("/")[-1]}', url))
            else:
                temp_info = None
                for line in lines:
                    line = line.strip()
                    if line.startswith("#EXTINF"):
                        temp_info = line
                    elif line.startswith("http") and temp_info:
                        found_channels.append((temp_info, line))
                        temp_info = None
        print(f"✅ Fetched source: {url}")
    except Exception as e:
        print(f"❌ Failed source {url}: {e}")
    return found_channels

def main():
    all_channels = []
    seen_urls = set()
    
    # 1. Collect all potential links
    for source in SOURCES:
        all_channels.extend(process_source(source))

    # 2. Filter duplicates
    unique_channels = []
    for info, url in all_channels:
        if url not in seen_urls:
            unique_channels.append((info, url))
            seen_urls.add(url)

    print(f"🔍 Testing {len(unique_channels)} channels for status...")

    # 3. Check status in parallel (Speed boost!)
    final_playlist = ["#EXTM3U"]
    
    def validate_and_format(channel_data):
        info, url = channel_data
        if is_alive(url):
            return f"{info}\n{url}"
        return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(validate_and_format, unique_channels))
        
    final_playlist.extend([r for r in results if r])

    # 4. Save
    with open("all_channels.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(final_playlist))
    
    print(f"✨ Success! Generated 'all_channels.m3u' with {len(final_playlist)-1} active streams.")

if __name__ == "__main__":
    main()