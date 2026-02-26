import requests
import urllib3

# Suppress security warnings for IP-based links
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS = [
    "http://103.229.254.25:7001/playlist.m3u8",
    "https://da.gd/NTOW8q",
    "https://is.gd/u2EgWa.m3u",
    "https://is.gd/y7OKsu.m3u8",
    "https://is.gd/AUxIDc.m3u"
]

def main():
    # VLC User-Agent prevents servers from blocking the script
    headers = {'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18'}
    output_file = "playlist.m3u"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        for url in URLS:
            try:
                print(f"Processing: {url}")
                # verify=False is mandatory for the IP 103.229... links
                r = requests.get(url, headers=headers, timeout=20, verify=False)
                r.raise_for_status()
                r.encoding = 'utf-8'
                
                lines = r.text.splitlines()
                # Skip the #EXTM3U line if it exists in the source
                start = 1 if lines and lines[0].strip().startswith("#EXTM3U") else 0
                
                for line in lines[start:]:
                    if line.strip():
                        f.write(line + "\n")
                print(f"✅ Added {url}")
            except Exception as e:
                print(f"❌ Failed {url}: {e}")

if __name__ == "__main__":
    main()
