import requests
from bs4 import BeautifulSoup
import os
import time

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    time.sleep(2)

def check_mrt_status():
    print("Checking for detailed alerts...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # 1. SMRT Detailed Check
        smrt_res = requests.get("https://www.smrt.com.sg/Travel/Service-Indicator", headers=headers, timeout=15)
        smrt_soup = BeautifulSoup(smrt_res.text, 'html.parser')
        # SMRT puts descriptions in the 'status-description' or specific table cells
        smrt_alert = smrt_soup.find('div', class_='status-description') 
        smrt_info = smrt_alert.get_text(strip=True) if smrt_alert else "Normal"

        # 2. SBS Detailed Check
        sbs_res = requests.get("https://www.sbstransit.com.sg", headers=headers, timeout=15)
        sbs_soup = BeautifulSoup(sbs_res.text, 'html.parser')
        # SBS uses a ticker or banner for live updates
        sbs_banner = sbs_soup.find('div', class_='train-service-status')
        sbs_info = sbs_banner.get_text(strip=True) if sbs_banner else "Normal"

        # Final Message Construction
        if "Normal" not in smrt_info or "Normal" not in sbs_info:
            message = "⚠️ *MRT SERVICE UPDATE*\n\n"
            
            if "Normal" not in smrt_info:
                message += f"🔴 *SMRT Info:*\n_{smrt_info}_\n\n"
            
            if "Normal" not in sbs_info:
                message += f"🟣 *SBS Info:*\n_{sbs_info}_\n"
            
            message += "\n🔗 [Check Live Map](https://www.lta.gov.sg/content/ltagov/en/getting_around/public_transport/rail_network.html)"
            send_telegram(message)
        else:
            print("Everything is Normal.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
