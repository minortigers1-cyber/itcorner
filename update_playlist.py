import requests
import urllib3

# Disable SSL warnings for the IP-based links
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Your specific IPTV source links
URLS = [
    "http://103.229.254.25:7001/playlist.m3u8",
    "https://da.gd/NTOW8q",
    "http://190.61.63.140:12142/playlist.m3u8",
    "https://da.gd/uuaWX0",
    "https://is.gd/u2EgWa.m3u",
    "https://is.gd/y7OKsu.m3u8",
    "https://is.gd/AUxIDc.m3u"
]

OUTPUT_FILE = "playlist.m3u"

def main():
    headers = {'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18'}
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n") # Start the master file
        
        for url in URLS:
            try:
                print(f"Fetching: {url}")
                # verify=False is key for the IP-based links (103.229... etc)
                response = requests.get(url, headers=headers, timeout=20, verify=False)
                response.raise_for_status()
                response.encoding = 'utf-8'
                
                lines = response.text.splitlines()
                
                # We skip the first line (#EXTM3U) of each link so it's not repeated
                start_index = 1 if lines and lines[0].strip().startswith("#EXTM3U") else 0
                
                for line in lines[start_index:]:
                    if line.strip():
                        f.write(line + "\n")
                print(f"✅ Success")
            except Exception as e:
                print(f"❌ Failed {url}: {e}")

if __name__ == "__main__":
    main()