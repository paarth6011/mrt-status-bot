import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(api_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=15)
        time.sleep(2)
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_mrt_status():
    # Calculate Singapore Time (UTC +8)
    sg_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%I:%M %p')
    print(f"Checking for live alerts at {sg_time} SGT...")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # 1. Scrape SMRT
        smrt_res = requests.get("https://www.smrt.com.sg/Travel/Service-Indicator", headers=headers, timeout=15)
        smrt_soup = BeautifulSoup(smrt_res.text, 'html.parser')
        smrt_box = smrt_soup.find('div', class_='status-description') or smrt_soup.find('div', class_='announcement-desc')
        smrt_info = smrt_box.get_text(strip=True) if smrt_box else "Normal Service"

        # 2. Scrape SBS
        sbs_res = requests.get("https://www.sbstransit.com.sg", headers=headers, timeout=15)
        sbs_soup = BeautifulSoup(sbs_res.text, 'html.parser')
        sbs_box = sbs_soup.find('div', class_='train-service-status') or sbs_soup.find('div', class_='marquee')
        sbs_info = sbs_box.get_text(strip=True) if sbs_box else "Normal Service"

        smrt_bad = not any(x in smrt_info.lower() for x in ["normal", "green", "good service"])
        sbs_bad = not any(x in sbs_info.lower() for x in ["normal", "green", "good service"])

        if smrt_bad or sbs_bad:
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
            if smrt_bad:
                message += f"🔴 *SMRT Status:*\n_{smrt_info}_\n\n"
            if sbs_bad:
                message += f"🟣 *SBS Status:*\n_{sbs_info}_\n"
            
            # The new timestamp line
            message += f"\n🕒 _Last Updated: {sg_time} SGT_"
            message += "\n📍 [View Official Rail Map](https://www.lta.gov.sg/content/ltagov/en/getting_around/public_transport/rail_network.html)"
            
            send_telegram(message)
            print(f"Real alert sent at {sg_time}")
        else:
            print(f"Status at {sg_time}: Everything is Normal.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
