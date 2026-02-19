import requests
import urllib3

# Suppress security warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def check_stream(url):
    """Returns True if the stream is online, False otherwise."""
    try:
        # Use HEAD request to save bandwidth and time
        response = requests.head(url, headers=HEADERS, timeout=5, verify=False, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def main():
    output_file = "playlist_online.m3u"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        for playlist_url in URLS:
            try:
                print(f"Checking playlist: {playlist_url}")
                r = requests.get(playlist_url, headers=HEADERS, timeout=15, verify=False)
                r.raise_for_status()
                
                lines = r.text.splitlines()
                current_info = ""

                for line in lines:
                    line = line.strip()
                    if line.startswith("#EXTINF"):
                        current_info = line  # Store metadata
                    elif line.startswith("http"):
                        # This is the actual stream link
                        print(f"  Verifying stream: {line[:50]}...", end=" ")
                        if check_stream(line):
                            f.write(f"{current_info}\n{line}\n")
                            print("✅ ONLINE")
                        else:
                            print("❌ OFFLINE")
            except Exception as e:
                print(f"❌ Could not access playlist {playlist_url}: {e}")

if __name__ == "__main__":
    main()