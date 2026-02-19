import requests

# List your IPTV M3U source links here
urls = [
    "https://example.com/playlist1.m3u",
    "https://example.com/playlist2.m3u",
    "https://raw.githubusercontent.com/someone/list/master/index.m3u"
]

def merge_playlists(url_list, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        # Write the required M3U header once
        f.write("#EXTM3U\n")
        
        for url in url_list:
            try:
                print(f"Fetching: {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                lines = response.text.splitlines()
                
                # Skip the first line (#EXTM3U) of each source to avoid duplicates
                start_index = 1 if lines and lines[0].startswith("#EXTM3U") else 0
                
                for line in lines[start_index:]:
                    if line.strip(): # Avoid empty lines
                        f.write(line + "\n")
                        
            except Exception as e:
                print(f"Error fetching {url}: {e}")

if __name__ == "__main__":
    merge_playlists(urls, "merged_playlist.m3u")
    print("Done! Created merged_playlist.m3u")