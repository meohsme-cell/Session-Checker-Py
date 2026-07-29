import requests
import threading
from queue import Queue

q = Queue()
working_proxies = []

with open('proxy.txt', 'r') as f:
    proxies = [line.strip() for line in f if line.strip()]

for p in proxies:
    q.put(p)

def check():
    while not q.empty():
        p = q.get()
        proxy_dict = {"http": f"socks4://{p}", "https": f"socks4://{p}"}
        try:
            response = requests.get("https://www.google.com", proxies=proxy_dict, timeout=5)
            if response.status_code == 200:
                print(f"[LIVE] {p}")
                working_proxies.append(p)
        except:
            pass
        q.task_done()

for _ in range(20):
    t = threading.Thread(target=check)
    t.start()

q.join()

with open('live_proxies.txt', 'w') as f:
    for p in working_proxies:
        f.write(p + "\n")

print(f"\n[+] تم الانتهاء! البروكسيات الشغالة: {len(working_proxies)} في ملف live_proxies.txt")
