import requests
import urllib3
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# 1. Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. Configuration
URLS = [
    "http://103.229.254.25:7001/playlist.m3u8",
    "https://da.gd/NTOW8q",
    "http://190.61.63.140:12142/playlist.m3u8",
    "https://da.gd/uuaWX0",
    "https://is.gd/u2EgWa.m3u",
    "https://is.gd/y7OKsu.m3u8",
    "https://is.gd/AUxIDc.m3u"
]

HEADERS = {'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18'}
MAX_THREADS = 30
TIMEOUT = 5

def get_group(metadata):
    """Extracts group-title from #EXTINF line using regex."""
    match = re.search(r'group-title="([^"]+)"', metadata)
    return match.group(1) if match else "Uncategorized"

def check_stream(metadata, url):
    """Checks stream status with HEAD/GET fallback."""
    try:
        # Try HEAD first (fast)
        response = requests.head(url, headers=HEADERS, timeout=TIMEOUT, 
                                 verify=False, allow_redirects=True)
        
        # Fallback to GET if HEAD is rejected (403/405)
        if response.status_code >= 400:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, 
                                    verify=False, stream=True, allow_redirects=True)
            response.close()

        if response.status_code == 200:
            return (metadata, url, True)
    except Exception:
        pass
    return (metadata, url, False)

def main():
    extracted_pairs = []
    output_file = "live_playlist_categorized.m3u"
    
    # Using a dictionary to group results by category
    categorized_results = defaultdict(list)

    print("--- [Step 1/2] Fetching & Parsing Playlists ---")
    for playlist_url in URLS:
        try:
            print(f"Reading: {playlist_url}")
            r = requests.get(playlist_url, headers=HEADERS, timeout=15, verify=False)
            r.raise_for_status()
            
            lines = r.text.splitlines()
            current_metadata = "#EXTINF:-1, Unknown Channel"
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#EXTM3U"): continue
                
                if line.startswith("#EXTINF"):
                    current_metadata = line
                elif line.startswith("http"):
                    extracted_pairs.append((current_metadata, line))
                    
        except Exception as e:
            print(f"⚠️ Error accessing {playlist_url}: {e}")

    total_links = len(extracted_pairs)
    print(f"\n--- [Step 2/2] Validating {total_links} Streams ---")
    
    
    
    online_count = 0
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(check_stream, meta, url): url for meta, url in extracted_pairs}
        
        for i, future in enumerate(as_completed(futures), 1):
            metadata, url, is_online = future.result()
            
            if is_online:
                group = get_group(metadata)
                categorized_results[group].append((metadata, url))
                online_count += 1
            
            if i % 10 == 0 or i == total_links:
                print(f"Progress: [{i}/{total_links}] - Found {online_count} online", end='\r')

    # Save to file, grouped by category
    print(f"\n\n--- [Step 3/3] Saving Results ---")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        # Sort groups alphabetically
        for group in sorted(categorized_results.keys()):
            print(f"Adding Group: {group} ({len(categorized_results[group])} channels)")
            for meta, url in categorized_results[group]:
                f.write(f"{meta}\n{url}\n")

    print(f"\n✅ Success! Saved {online_count} channels to '{output_file}'.")

if __name__ == "__main__":
    main()