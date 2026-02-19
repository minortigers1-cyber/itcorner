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

    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                lines = r.text.splitlines()
                current_info = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("#EXTINF"):
                        current_info = line
                    elif line.startswith("http") and current_info:
                        if line not in seen_urls:
                            combined_content.append(current_info)
                            combined_content.append(line)
                            seen_urls.add(line)
                        current_info = None
            print(f"Successfully processed: {url}")
        except Exception as e:
            print(f"Error skipping {url}: {e}")

    with open("all_channels.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))

if __name__ == "__main__":
    main()