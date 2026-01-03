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
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour = now_sg.hour
    sg_minute = now_sg.minute

    print(f"Checking for live alerts at {sg_time_str} SGT...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # Scrape SMRT & SBS
        smrt_res = requests.get("https://www.smrt.com.sg/Travel/Service-Indicator", headers=headers, timeout=15)
        smrt_soup = BeautifulSoup(smrt_res.text, 'html.parser')
        smrt_box = smrt_soup.find('div', class_='status-description') or smrt_soup.find('div', class_='announcement-desc')
        smrt_info = smrt_box.get_text(strip=True) if smrt_box else "Normal Service"

        sbs_res = requests.get("https://www.sbstransit.com.sg", headers=headers, timeout=15)
        sbs_soup = BeautifulSoup(sbs_res.text, 'html.parser')
        sbs_box = sbs_soup.find('div', class_='train-service-status') or sbs_soup.find('div', class_='marquee')
        sbs_info = sbs_box.get_text(strip=True) if sbs_box else "Normal Service"

        smrt_bad = not any(x in smrt_info.lower() for x in ["normal", "green", "good service"])
        sbs_bad = not any(x in sbs_info.lower() for x in ["normal", "green", "good service"])

        # 1. THE DISRUPTION ALERT (High Priority)
        if True:
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
            if smrt_bad: message += f"🔴 *SMRT Status:*\n_{smrt_info}_\n\n"
            if sbs_bad: message += f"🟣 *SBS Status:*\n_{sbs_info}_\n"
            message += f"\n🕒 _Last Updated: {sg_time_str} SGT_"
            send_telegram(message)
        
        # 2. THE DAILY SUMMARY (Only at 7:00 AM SGT)
        # Since the bot runs every 5-10 mins, we check if it's the 7:00 AM window
        elif sg_hour == 7 and sg_minute < 10:
            summary = "☀️ *GOOD MORNING!*\\n\n✅ *All MRT lines are running normally.*\\nYour commute is clear for now.\\n\\n🕒 _Sent at: 07:00 AM SGT_"
            send_telegram(summary)
            print("Daily summary sent.")
            
        else:
            print(f"Status at {sg_time_str}: Everything is Normal.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
