import requests
import json
import urllib3
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Disable SSL warnings (many IPTV servers use self-signed certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_iptv_account(m3u_url):
    # Set a common IPTV player header to avoid being blocked by the server
    headers = {
        'User-Agent': 'IPTVSmarters/1.0.3',
        'Accept': 'application/json'
    }

    try:
        # 1. Extract credentials from the provided URL
        parsed = urlparse(m3u_url)
        base_server = f"{parsed.scheme}://{parsed.netloc}"
        query_params = parse_qs(parsed.query)
        
        # Pull username/password regardless of exact key name used
        user = query_params.get('username', query_params.get('user', [None]))[0]
        pw = query_params.get('password', query_params.get('pass', [None]))[0]

        if not user or not pw:
            print("❌ Error: Could not find username or password in the link.")
            return

        # 2. Build the official Xtream Codes API URL
        api_url = f"{base_server}/player_api.php?username={user}&password={pw}"
        print(f"📡 Connecting to: {base_server}...")

        # 3. Fetch account info
        response = requests.get(api_url, headers=headers, timeout=15, verify=False)
        
        # Check if the server actually sent back content
        if not response.text.strip():
            print("❌ Error: Server returned an empty response. It might be down or your IP is blocked.")
            return

        # 4. Parse JSON safely
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("❌ Error: Server did not return valid JSON. It likely sent an HTML error page.")
            print(f"Status Code: {response.status_code}")
            return

        # 5. Display the results
        if "user_info" in data:
            info = data["user_info"]
            
            # Handle Expiry Date
            exp = info.get("exp_date")
            if exp and exp != "null" and exp != "0":
                dt_object = datetime.fromtimestamp(int(exp))
                expiry_str = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                # Check if currently expired
                status = "🟢 ACTIVE" if int(exp) > datetime.now().timestamp() else "🔴 EXPIRED"
            else:
                expiry_str = "Unlimited / Never Expires"
                status = "🟢 ACTIVE (Lifetime)"

            print("\n" + "═"*40)
            print(f" STATUS: {status}")
            print("═"*40)
            print(f"👤 User:       {info.get('username')}")
            print(f"🔑 Pass:       {info.get('password')}")
            print(f"📅 Expiry:     {expiry_str}")
            print(f"📺 Max Conns:  {info.get('max_connections', '1')}")
            print(f"👥 Active:     {info.get('active_cons', '0')}")
            print(f"🏛️ Server:     {base_server}")
            print("═"*40)
        else:
            print("❌ Login Failed: Credentials may be wrong or the account was deleted.")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Network Error: {e}")

# --- INPUT YOUR LINK HERE ---
# Make sure your link includes http:// and the :port number
test_link = "http://starshare.net:80/get.php?username=Suryaaa&password=SURYAAAA&type=m3u"

if __name__ == "__main__":
    check_iptv_account(test_link)