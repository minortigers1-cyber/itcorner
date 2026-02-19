import requests
import re

# List all your source M3U links here
SOURCES = [
    "http://103.229.254.25:7001/playlist.m3u8",
    "https://da.gd/NTOW8q",
    "http://190.61.63.140:12142/playlist.m3u8",
    "https://da.gd/uuaWX0",
    "https://is.gd/u2EgWa.m3u",
    "https://is.gd/y7OKsu.m3u8",
    "https://is.gd/AUxIDc.m3u"
]

def main():
    combined_content = ["#EXTM3U"]
    seen_urls = set()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) IPTVPlayer/1.0'
    }

    for url in SOURCES:
        try:
            r = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
            if r.status_code == 200:
                lines = r.text.splitlines()
                
                # Check for single stream link vs playlist
                if not any(line.startswith("#EXTINF") for line in lines):
                    if url not in seen_urls:
                        # Add a default logo and group for single streams
                        name = url.split('/')[-1].replace('.m3u8', '').replace('.m3u', '') or "Live Stream"
                        combined_content.append(f'#EXTINF:-1 tvg-logo="" group-title="My Streams",{name}')
                        combined_content.append(url)
                        seen_urls.add(url)
                else:
                    current_info = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith("#EXTINF"):
                            # Ensure every channel has a group-title if it's missing
                            if 'group-title="' not in line:
                                line = line.replace('#EXTINF:-1', '#EXTINF:-1 group-title="Uncategorized"')
                            current_info = line
                        elif line.startswith("http") and current_info:
                            if line not in seen_urls:
                                combined_content.append(current_info)
                                combined_content.append(line)
                                seen_urls.add(line)
                            current_info = None
            print(f"✅ Processed: {url}")
        except Exception as e:
            print(f"❌ Error {url}: {e}")

    with open("all_channels.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))

if __name__ == "__main__":
    main()