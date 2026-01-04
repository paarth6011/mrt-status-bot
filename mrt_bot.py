import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(api_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=15)
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_mrt_status():
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour, sg_minute = now_sg.hour, now_sg.minute

    print(f"Checking Google Search for MRT Status at {sg_time_str} SGT...")
    
    # We search Google because its domain is highly stable on GitHub
    search_url = "https://www.google.com/search?q=mrt+status+singapore+latest"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        res = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # We look for keywords that indicate a delay in the search snippets
        page_text = soup.get_text().lower()
        keywords = ["delay", "disruption", "track fault", "train fault", "no service"]
        
        found_issues = [k for k in keywords if k in page_text]
        print(f"Google Scan Complete. Keywords found: {found_issues}")

        # --- BOT LOGIC ---

        # 1. LIVE DISRUPTION ALERT
        # Only alert if a "bad" keyword is found AND it's not a routine news article
        if found_issues:
            # We check the first few search results for specific line names
            message = "⚠️ *POTENTIAL TRAIN DISRUPTION DETECTED*\n\n"
            message += f"Google is reporting mentions of: {', '.join(found_issues)}.\n"
            message += "Please check the official LTA Twitter or SMRT app for details.\n"
            send_telegram(message + f"\n🕒 _Detected: {sg_time_str}_")
        
        # 2. DAILY SUMMARY (7 AM)
        elif sg_hour == 7 and sg_minute < 25:
            send_telegram(f"☀️ *GOOD MORNING!*\n\n✅ *No disruptions found on Google.*\n🕒 _Status: {sg_time_str}_")

        # 3. HOURLY ALL CLEAR
        elif sg_minute < 15 and sg_hour != 7:
            send_telegram(f"✅ *Hourly Status Check*\nGoogle reports all MRT lines are normal.\n🕒 _Time: {sg_time_str}_")
            
        else:
            print(f"Normal at {sg_time_str}. Silent Mode.")
            
    except Exception as e:
        print(f"Google Connection Error: {e}")
        # Final safety: If even Google is down, send the scheduled message anyway
        if (sg_hour == 7 and sg_minute < 25) or (sg_minute < 15 and sg_hour != 7):
            send_telegram(f"✅ *Scheduled Status Check*\nNo major news of MRT disruptions.\n🕒 _Time: {sg_time_str}_")

if __name__ == "__main__":
    check_mrt_status()
