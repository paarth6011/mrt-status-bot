import requests
from bs4 import BeautifulSoup
import os
import sys
from datetime import datetime, timedelta

# Force-flush logs so they appear in GitHub Actions immediately
def log(msg):
    print(msg, flush=True)

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    log(f"Attempting to send Telegram message...")
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(api_url, data=payload, timeout=15)
        log(f"Telegram Response: {r.status_code}")
    except Exception as e:
        log(f"Telegram Error: {e}")

def check_mrt_status():
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour, sg_minute = now_sg.hour, now_sg.minute

    log(f"--- BOT RUN START: {sg_time_str} SGT ---")
    
    # Check if Secrets are missing
    if not TOKEN or not CHAT_ID:
        log("❌ ERROR: BOT_TOKEN or CHAT_ID is missing from GitHub Secrets!")
        return

    search_url = "https://www.google.com/search?q=mrt+status+singapore+latest+smrt+alerts"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        log("Fetching data from Google...")
        res = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Target the specific search result snippets
        results = soup.select('.VwiC3b') 
        log(f"Found {len(results)} search snippets.")
        
        disruption_content = ""
        keywords = ["delay", "track fault", "train fault", "additional travel time", "no service"]

        for r in results:
            text = r.get_text()
            if any(k in text.lower() for k in keywords):
                disruption_content = text
                log(f"⚠️ DISRUPTION KEYWORD FOUND: {text[:50]}...")
                break 

        # --- OUTPUT LOGIC ---
        if disruption_content:
            log("Sending Live Disruption Update...")
            message = (
                "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
                "🔴 *SMRT Status:*\n"
                f"{disruption_content}\n\n"
                f"🕒 _Last Updated: {sg_time_str}_"
            )
            send_telegram(message)
        
        elif sg_hour == 7 and sg_minute < 25:
            log("Sending Morning Summary...")
            message = (
                "☀️ *GOOD MORNING*\n\n"
                "✅ *SMRT Status:*\n"
                "All MRT lines are running normally. No disruptions reported.\n\n"
                f"🕒 _Status as of {sg_time_str}_"
            )
            send_telegram(message)

        elif sg_minute < 15:
            log("Sending Hourly Check...")
            message = (
                "✅ *Hourly Status Check*\n"
                "All MRT lines are running normally.\n\n"
                f"🕒 _Time: {sg_time_str}_"
            )
            send_telegram(message)
        else:
            log("Condition not met for messaging (Silent Mode).")
            
    except Exception as e:
        log(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    check_mrt_status()
    log("--- BOT RUN FINISHED ---")
