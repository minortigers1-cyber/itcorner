import requests
import urllib3

# Suppress the "Insecure Request" warnings for the IP-based links
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

urls = [
    "http://103.229.254.25:7001/playlist.m3u8",
    "https://da.gd/NTOW8q",
    "http://190.61.63.140:12142/playlist.m3u8",
    "https://da.gd/uuaWX0",
    "https://is.gd/u2EgWa.m3u",
    "https://is.gd/y7OKsu.m3u8",
    "https://is.gd/AUxIDc.m3u"
]

def merge_iptv_lists(url_list, output_filename):
    headers = {'User-Agent': 'Mozilla/5.0 (VLC)'} # Simpler agent often works better for IPTV
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        for url in url_list:
            try:
                print(f"🔄 Processing: {url}")
                # Added verify=False to bypass SSL errors
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                response.raise_for_status()
                response.encoding = 'utf-8'
                
                lines = [line.strip() for line in response.text.splitlines() if line.strip()]
                start_index = 1 if lines and lines[0].startswith("#EXTM3U") else 0
                
                for line in lines[start_index:]:
                    f.write(line + "\n")
                print(f"✅ Success")
                
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    merge_iptv_lists(urls, "merged_playlist.m3u")