import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. Suppress SSL warnings (common with IPTV IP-based links)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. Configuration
URLS = [
    "http://103.229.254.25:7001/playlist.m3u8",
    "https://da.gd/NTOW8q",
    "https://starshare.net:80/get.php?username=Suryaaa&password=SURYAAAA&type=m3u",
    "https://da.gd/uuaWX0",
    "https://is.gd/u2EgWa.m3u",
    "https://is.gd/y7OKsu.m3u8",
    "https://is.gd/AUxIDc.m3u"
]

HEADERS = {'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18'}
MAX_THREADS = 25  # Increased for faster processing
TIMEOUT = 7       # Seconds to wait for a stream to respond

def check_stream(metadata, url):
    """Checks if a single stream is online."""
    try:
        # stream=True is the most reliable way to check IPTV links
        with requests.get(url, headers=HEADERS, timeout=TIMEOUT, 
                         verify=False, stream=True, allow_redirects=True) as r:
            if r.status_code == 200:
                return (metadata, url, True)
    except Exception:
        pass
    return (metadata, url, False)

def main():
    extracted_pairs = []
    output_file = "live_playlist.m3u"

    print("--- [Step 1/2] Fetching & Parsing Playlists ---")
    for playlist_url in URLS:
        try:
            print(f"Reading: {playlist_url}")
            # Use a slightly longer timeout for the initial download
            r = requests.get(playlist_url, headers=HEADERS, timeout=15, verify=False)
            r.raise_for_status()
            
            lines = r.text.splitlines()
            temp_metadata = "#EXTINF:-1, Unknown Channel"
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                if line.startswith("#EXTINF"):
                    temp_metadata = line
                elif line.startswith("http"):
                    extracted_pairs.append((temp_metadata, line))
                    # Reset metadata to default in case next URL has no header
                    temp_metadata = "#EXTINF:-1, Unknown Channel"
                    
        except Exception as e:
            print(f"⚠️ Error accessing {playlist_url}: {e}")

    print(f"\n--- [Step 2/2] Validating {len(extracted_pairs)} Streams ---")
    
    online_count = 0
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            # Map the function to our pairs
            futures = [executor.submit(check_stream, meta, url) for meta, url in extracted_pairs]
            
            for i, future in enumerate(as_completed(futures)):
                metadata, url, is_online = future.result()
                
                if is_online:
                    f.write(f"{metadata}\n{url}\n")
                    online_count += 1
                
                # Progress Update every 20 streams
                if (i + 1) % 20 == 0 or (i + 1) == len(extracted_pairs):
                    print(f"Processed {i+1}/{len(extracted_pairs)}...")

    print(f"\n✅ Success! Saved {online_count} online channels to '{output_file}'.")

if __name__ == "__main__":
    main()