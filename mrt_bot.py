import requests
from bs4 import BeautifulSoup
import os
import time

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=15)
    time.sleep(2)

def check_mrt_status():
    print("Checking for detailed alerts...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # 1. Check SMRT Status (NSL, EWL, CCL, TEL)
        smrt_res = requests.get("https://www.smrt.com.sg/Travel/Service-Indicator", headers=headers, timeout=15)
        smrt_soup = BeautifulSoup(smrt_res.text, 'html.parser')
        # Grabs the specific announcement box if it exists
        smrt_box = smrt_soup.find('div', class_='status-description') or smrt_soup.find('div', class_='announcement-desc')
        smrt_info = smrt_box.get_text(strip=True) if smrt_box else "Normal"

        # 2. Check SBS Status (NEL, DTL, LRTs)
        sbs_res = requests.get("https://www.sbstransit.com.sg", headers=headers, timeout=15)
        sbs_soup = BeautifulSoup(sbs_res.text, 'html.parser')
        # Grabs the marquee or banner text
        sbs_box = sbs_soup.find('div', class_='train-service-status') or sbs_soup.find('div', class_='marquee')
        sbs_info = sbs_box.get_text(strip=True) if sbs_box else "Normal"

        # Logic to determine if we should alert
        # We ignore words like 'Normal' or 'Green'
        smrt_bad = "normal" not in smrt_info.lower() and smrt_info != ""
        sbs_bad = "normal" not in sbs_info.lower() and sbs_info != ""

        if smrt_bad or sbs_bad:
            message = "⚠️ *MRT DISRUPTION DETECTED*\n\n"
            if smrt_bad:
                message += f"🔴 *SMRT Update:*\n_{smrt_info}_\n\n"
            if sbs_bad:
                message += f"🟣 *SBS Update:*\n_{sbs_info}_\n"
            
            message += "📍 [View Live System Map](https://www.lta.gov.sg/content/ltagov/en/getting_around/public_transport/rail_network.html)"
            send_telegram(message)
            print(f"Alert Sent: {smrt_info} | {sbs_info}")
        else:
            print("Status: Everything is Normal.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
