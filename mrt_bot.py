import requests
from bs4 import BeautifulSoup
import os
import time

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        response = requests.post(api_url, data={"chat_id": CHAT_ID, "text": message}, timeout=15)
        print(f"Telegram Sent: {response.status_code}")
        time.sleep(2) 
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_mrt_status():
    print("Checking specific alert sections...")
    
    smrt_url = "https://www.smrt.com.sg/Travel/Service-Indicator"
    sbs_url = "https://www.sbstransit.com.sg"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # 1. SMRT Check (Targeting the service indicator table)
        smrt_res = requests.get(smrt_url, headers=headers, timeout=15)
        smrt_soup = BeautifulSoup(smrt_res.text, 'html.parser')
        # SMRT hides normal status in an image or specific div
        smrt_main = smrt_soup.find('div', {'id': 'service-indicator'})
        smrt_text = smrt_main.get_text().lower() if smrt_main else ""
        
        # 2. SBS Check (Targeting the 'Train Service' banner)
        sbs_res = requests.get(sbs_url, headers=headers, timeout=15)
        sbs_soup = BeautifulSoup(sbs_res.text, 'html.parser')
        # SBS often uses a specific class for alerts
        sbs_banner = sbs_soup.find('div', class_='train-service-status')
        sbs_text = sbs_banner.get_text().lower() if sbs_banner else ""

        # Only alert if these words are found in the ALERT BANNERS specifically
        alerts = ["delay", "disruption", "track fault", "longer travel time"]
        found = []
        
        for word in alerts:
            if word in smrt_text: found.append(f"🔴 SMRT: {word}")
            if word in sbs_text: found.append(f"🟣 SBS: {word}")

        if found:
            send_telegram("🚨 REAL-TIME ALERT:\n" + "\n".join(found))
        else:
            print("✅ Status confirmed Normal in alert boxes.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
