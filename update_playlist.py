import requests
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs

def get_account_info(m3u_url):
    try:
        # 1. Parse credentials from the M3U URL
        parsed_url = urlparse(m3u_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        params = parse_qs(parsed_url.query)
        
        username = params.get('username', [None])[0]
        password = params.get('password', [None])[0]

        if not username or not password:
            return "❌ Error: Could not find username or password in the URL."

        # 2. Construct the Xtream Codes API Player URL
        # Format: http://server:port/player_api.php?username=USER&password=PASS
        api_url = f"{base_url}/player_api.php?username={username}&password={password}"

        # 3. Request account details
        response = requests.get(api_url, timeout=10, verify=False)
        data = response.json()

        if "user_info" in data:
            user = data["user_info"]
            
            # Convert Unix timestamp to readable date
            exp_timestamp = user.get("exp_date")
            if exp_timestamp and exp_timestamp != "null":
                expiry_date = datetime.fromtimestamp(int(exp_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                expiry_date = "Unlimited / Never Expires"

            # Print Results
            print("-" * 30)
            print(f"✅ ACCOUNT FOUND")
            print("-" * 30)
            print(f"User ID:    {user.get('username')}")
            print(f"Password:   {user.get('password')}")
            print(f"Status:     {user.get('status')}")
            print(f"Expiry:     {expiry_date}")
            print(f"Max Conns:  {user.get('max_connections')}")
            print(f"Active now: {user.get('active_cons')}")
            print("-" * 30)
        else:
            print("❌ Invalid Credentials or Server Rejected request.")

    except Exception as e:
        print(f"⚠️ Error: {e}")

# --- SETUP ---
# Replace this with your actual M3U link
test_url = "http://starshare.net:80/get.php?username=Suryaaa&password=SURYAAAA&type=m3u"

if __name__ == "__main__":
    get_account_info(test_url)