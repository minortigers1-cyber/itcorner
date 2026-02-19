import requests
import urllib3

# This disables the "InsecureRequestWarning" if we have to skip SSL verification
urllib3.disable_warnings(urllib3.exceptions.InsecureVerificationWarning)

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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    combined_content = ["#EXTM3U"]
    seen_urls = set()

    for url in SOURCES:
        try:
            # verify=False added to bypass SSL certificate issues common with link shorteners
            r = requests.get(url, headers=headers, timeout=15, allow_redirects=True, verify=False)
            
            if r.status_code == 200:
                # Use splitlines to handle different newline characters (\n vs \r\n)
                lines = [l.strip() for l in r.text.splitlines() if l.strip()]
                
                # Check if it's already an M3U file or just a raw stream link
                is_m3u = any(line.startswith("#EXTINF") for line in lines)
                
                if not is_m3u:
                    # Treat as a direct stream link
                    if url not in seen_urls:
                        name = url.split('/')[-1] or "Stream_Source"
                        combined_content.append(f'#EXTINF:-1 group-title="Consolidated",{name}')
                        combined_content.append(url)
                        seen_urls.add(url)
                else:
                    # Parse existing M3U content
                    current_info = ""
                    for line in lines:
                        if line.startswith("#EXTINF"):
                            current_info = line
                        elif line.startswith("http") or not line.startswith("#"):
                            stream_url = line if line.startswith("http") else url.rsplit('/', 1)[0] + '/' + line
                            if stream_url not in seen_urls:
                                combined_content.append(current_info if current_info else "#EXTINF:-1,Channel")
                                combined_content.append(stream_url)
                                seen_urls.add(stream_url)
                                current_info = ""
                print(f"✅ Processed: {url}")
            else:
                print(f"⚠️ Warning: {url} returned status {r.status_code}")
                
        except Exception as e:
            print(f"❌ Failed {url}: {str(e)}")

    # Final Save
    with open("all_channels.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))
    print(f"\n🚀 Done! Created all_channels.m3u with {len(seen_urls)} channels.")

if __name__ == "__main__":
    main()