import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress security warnings for IP-based links
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
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
MAX_THREADS = 20  # How many streams to check at once
TIMEOUT = 5       # Seconds to wait for a stream response

def check_stream(stream_info):
    """
    Checks if a single stream is online.
    Input: A tuple (metadata_line, stream_url)
    Output: (metadata_line, stream_url, is_online)
    """
    metadata, url = stream_info
    try:
        # We use stream=True and a short timeout to avoid downloading the whole video
        # Some servers block HEAD requests, so GET with stream=True is more reliable
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, 
                                verify=False, stream=True, allow_redirects=True)
        is_online = response.status_code == 200
        response.close() # Close connection immediately
        return (metadata, url, is_online)
    except:
        return (metadata, url, False)

def main():
    all_streams = []
    output_file = "filtered_playlist.m3u"

    print("--- Phase 1: Downloading Playlists ---")
    for playlist_url in URLS:
        try:
            print(f"Fetching: {playlist_url}")
            r = requests.get(playlist_url, headers=HEADERS, timeout=15, verify=False)
            r.raise_for_status()
            
            lines = r.text.splitlines()
            current_metadata = ""
            
            for line in lines:
                line = line.strip()
                if line