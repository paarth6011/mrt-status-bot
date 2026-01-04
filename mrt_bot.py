import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(api_url, data=payload, timeout=15)

def check_mrt_status():
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour, sg_minute = now_sg.hour, now_sg.minute

    search_url = "https://www.google.com/search?q=mrt+status+singapore+latest+smrt+alerts"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        res = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # We look for the "Snippet" or "Description" parts of search results
        results = soup.select('.VwiC3b') 
        
        disruption_content = ""
        keywords = ["delay", "track fault", "train fault", "additional travel time", "no service"]

        for r in results:
            text = r.get_text()
            if any(k in text.lower() for k in keywords):
                disruption_content = text
                break # Take the most recent relevant result

        # --- THE EXACT FORMATTING YOU REQUESTED ---

        # 1. LIVE DISRUPTION ALERT
        if disruption_content:
            message = (
                "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
                "🔴 *SMRT Status:*\n"
                f"{disruption_content}\n\n"
                f"🕒 _Last Updated: {sg_time_str}_"
            )
            send_telegram(message)
        
        # 2. DAILY SUMMARY (7 AM)
        elif sg_hour == 7 and sg_minute < 25:
            message = (
                "☀️ *GOOD MORNING*\n\n"
                "✅ *SMRT Status:*\n"
                "All MRT lines are running normally. No disruptions reported.\n\n"
                f"🕒 _Status as of {sg_time_str}_"
            )
            send_telegram(message)

        # 3. HOURLY ALL CLEAR
        elif sg_minute < 15 and sg_hour != 7:
            message = (
                "✅ *Hourly Status Check*\n"
                "All MRT lines are running normally.\n\n"
                f"🕒 _Time: {sg_time_str}_"
            )
            send_telegram(message)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
