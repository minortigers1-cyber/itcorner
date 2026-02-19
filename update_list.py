import requests

# Your specific IPTV source links
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
    # Headers to mimic a real VLC/IPTV player to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    with open(output_filename, "w", encoding="utf-8") as f:
        # The mandatory first line for all M3U files
        f.write("#EXTM3U\n")
        
        for url in url_list:
            try:
                print(f"🔄 Processing: {url}")
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Split content into lines and filter out empty ones
                lines = [line.strip() for line in response.text.splitlines() if line.strip()]
                
                # If the first line is #EXTM3U, we skip it to prevent mid-file headers
                start_index = 1 if lines and lines[0].startswith("#EXTM3U") else 0
                
                for line in lines[start_index:]:
                    f.write(line + "\n")
                
                print(f"✅ Successfully merged: {url}")
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to fetch {url}: {e}")

if __name__ == "__main__":
    output_file = "merged_playlist.m3u"
    merge_iptv_lists(urls, output_file)
    print(f"\n✨ COMPLETE: Your file '{output_file}' is ready to be uploaded to GitHub.")