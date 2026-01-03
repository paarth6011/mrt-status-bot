import requests
from bs4 import BeautifulSoup
import os
import time

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        # Markdown allows for bold and italic text in Telegram
        requests.post(api_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=15)
        time.sleep(2)
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_mrt_status():
    print("Checking for detailed alerts...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        # 1. SMRT Detailed Scrape
        smrt_res = requests.get("https://www.smrt.com.sg/Travel/Service-Indicator", headers=headers, timeout=15)
        smrt_soup = BeautifulSoup(smrt_res.text, 'html.parser')
        
        # SMRT often uses 'status-description' or 'announcement-desc'
        smrt_box = smrt_soup.find('div', class_='status-description') or smrt_soup.find('div', class_='announcement-desc')
        smrt_info = smrt_box.get_text(strip=True) if smrt_box else "Normal Service"

        # 2. SBS Transit Detailed Scrape
        sbs_res = requests.get("https://www.sbstransit.com.sg", headers=headers, timeout=15)
        sbs_soup = BeautifulSoup(sbs_res.text, 'html.parser')
        
        # SBS uses a marquee or a specific status bar on their homepage
        sbs_banner = sbs_soup.find('div', class_='train-service-status') or sbs_soup.find('div', class_='marquee')
        sbs_info = sbs_banner.get_text(strip=True) if sbs_banner else "Normal Service"

        # Logic: If it's NOT "Normal", "Green", or "Service", it's likely a real update
        is_smrt_bad = not any(x in smrt_info.lower() for x in ["normal", "green", "good service"])
        is_sbs_bad = not any(x in sbs_info.lower() for x in ["normal", "green", "good service"])

        if is_smrt_bad or is_sbs_bad:
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
            
            if is_smrt_bad:
                message += f"🔴 *SMRT Status:*\n{smrt_info}\n\n"
            
            if is_sbs_bad:
                message += f"🟣 *SBS Status:*\n{sbs_info}\n"
            
            message += "\n🕒 _Check official sources for latest shuttle bus info._"
            send_telegram(message)
            print(f"Alert Sent: {smrt_info} | {sbs_info}")
        else:
            print("Everything is Normal.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
