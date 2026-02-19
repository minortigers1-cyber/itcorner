import requests

SOURCES = [
    "http://103.229.254.25:7001/playlist.m3u8",
    "https://da.gd/NTOW8q",
    "http://190.61.63.140:12142/playlist.m3u8",
    "https://da.gd/uuaWX0",
    "https://is.gd/u2EgWa.m3u",
    "https://is.gd/y7OKsu.m3u8",
    "https://is.gd/AUxIDc.m3u"
]

def is_alive(url):
    """Checks if a stream URL is actually online."""
    try:
        # We use a 3-second timeout so the script doesn't hang on dead links
        response = requests.head(url, timeout=3, allow_redirects=True)
        return response.status_code < 400
    except:
        return False

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) IPTVPlayer/1.0'}
    combined_content = ["#EXTM3U"]
    seen_urls = set()

    for url in SOURCES:
        try:
            r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            if r.status_code == 200:
                lines = r.text.splitlines()
                
                # Check for single stream link vs playlist
                is_list = any(line.startswith("#EXTINF") for line in lines)
                
                if not is_list:
                    if url not in seen_urls and is_alive(url):
                        name = url.split('/')[-1].split('?')[0] or "Live Stream"
                        combined_content.append(f'#EXTINF:-1 group-title="Online Only",{name}')
                        combined_content.append(url)
                        seen_urls.add(url)
                else:
                    temp_info = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith("#EXTINF"):
                            temp_info = line
                        elif line.startswith("http") and temp_info:
                            if line not in seen_urls:
                                # ONLY add if the channel is currently online
                                if is_alive(line):
                                    combined_content.append(temp_info)
                                    combined_content.append(line)
                                    seen_urls.add(line)
                            temp_info = None
            print(f"✅ Processed source: {url}")
        except Exception as e:
            print(f"❌ Source Error {url}: {e}")

    with open("all_channels.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))

if __name__ == "__main__":
    main()