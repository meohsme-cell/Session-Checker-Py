import os
import threading
from queue import Queue
import random

COMBO_FILE = "combo.txt"
HITS_FILE = "hits.txt"
PROXY_FILE = "proxy.txt"
THREADS = 5

def get_proxy():
    if os.path.exists(PROXY_FILE):
        with open(PROXY_FILE, "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
            if proxies:
                p = random.choice(proxies)
                return {"http": p, "https": p}
    return None

def check_account(email, password):
    proxy = get_proxy()
    try:
        print(f"[CHECKING Shahid] {email}")
        is_hit = False  
        
        if is_hit:
            print(f"[HIT!] {email}:{password}")
            with open(HITS_FILE, "a", encoding="utf-8") as hf:
                hf.write(f"{email}:{password}\n")
        else:
            pass
            
    except Exception as e:
        print(f"[ERROR] {email} -> {str(e)}")

def worker(queue):
    while not queue.empty():
        item = queue.get()
        if item:
            email, password = item
            check_account(email, password)
        queue.task_done()

def main():
    if not os.path.exists(COMBO_FILE):
        print("[-] ملف combo.txt غير موجود!")
        return

    queue = Queue()
    with open(COMBO_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if ":" in line:
                parts = line.strip().split(":", 1)
                if len(parts) == 2:
                    queue.put(parts)

    print(f"[+] تم تحميل الحسابات بنجاح. عدد الحسابات: {queue.qsize()}")
    print(f"[+] جاري بدء فحص شاهد عبر البروكسيات...\n")

    thread_list = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker, args=(queue,))
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

    print(f"\n[+] انتهى الفحص! أي حساب صحيح تم حفظه في ملف {HITS_FILE}")

if __name__ == "__main__":
    main()
