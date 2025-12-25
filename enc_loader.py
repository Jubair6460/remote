import os
import sys
import time
import uuid

# --- 1. AUTO INSTALLER ---
try:
    import requests
    from rich.console import Console
except ImportError:
    print("Installing libraries...")
    os.system("pip install requests bs4 rich")
    import requests

# --- 2. CONFIGURATION ---
# আপনার গিটহাব লিংকগুলো ঠিকমত বসান
GITHUB_USERS = "https://raw.githubusercontent.com/jubairbro/access/main/users.txt"
GITHUB_CODE  = "https://raw.githubusercontent.com/Jubair6460/remote/main/encrypt_source.py"
GITHUB_JSON  = "https://raw.githubusercontent.com/Jubair6460/remote/main/servers.json"

# আপনার বট তথ্য (সরাসরি বসান)
BOT_TOKEN = "#" 
ADMIN_ID = "8486562838"
CHANNEL = "https://t.me/+5ygHfkZxVBc0Mjdl"

def get_key():
    path = "/sdcard/.jubair_tool"
    if not os.path.exists(path): os.makedirs(path)
    file = f"{path}/key.txt"
    
    if os.path.exists(file):
        with open(file, "r") as f: return f.read().strip()
    
    # নতুন কী তৈরি
    new_key = f"KEY-SENSEI-{str(uuid.uuid4()).split('-')[0].upper()}"
    with open(file, "w") as f: f.write(new_key)
    return new_key

def send_request(key):
    """আপনার বটে কী পাঠিয়ে দিবে"""
    try:
        import getpass
        msg = f"🔔 **Approval Request**\nKey: `{key}`\nUser: {getpass.getuser()}"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={'chat_id': ADMIN_ID, 'text': msg, 'parse_mode': 'Markdown'})
    except: pass

def main():
    os.system('clear')
    print("\033[1;32m[●] CONNECTING TO JUBAIR SERVER...\033[0m")
    
    # চ্যানেল ওপেন
    os.system(f"xdg-open {CHANNEL} > /dev/null 2>&1")
    
    my_key = get_key()
    
    try:
        # ইউজার লিস্ট চেক
        users = requests.get(GITHUB_USERS, timeout=10).text
        
        if my_key in users:
            print("\033[1;32m[✓] ACCESS GRANTED\033[0m")
            time.sleep(0.5)
            
            # কোড ডাউনলোড ও রান
            code = requests.get(GITHUB_CODE).text
            
            # সেইফ এক্সিকিউশন (namespace ব্যবহার করে)
            namespace = {}
            exec(code, globals(), namespace)
            
            # মেইন ফাংশন কল
            if 'start_scraping' in namespace:
                namespace['start_scraping'](GITHUB_JSON)
            else:
                print("\033[1;31m[!] Error: Main function not found!\033[0m")
                
        else:
            print("\n" + "━"*30)
            print(f"\033[1;31m[x] DEVICE NOT APPROVED\033[0m")
            print(f"Key: \033[1;33m{my_key}\033[0m")
            print("━"*30)
            
            print("[!] Sending Request to Admin...")
            send_request(my_key)
            print("\033[1;32m[✓] Request Sent! Wait for approval.\033[0m")
            
            # অটো কপি
            os.system(f"termux-clipboard-set {my_key}")
            
    except Exception as e:
        print(f"\033[1;31m[!] Server/Internet Error: {e}\033[0m")

if __name__ == "__main__":
    main()
