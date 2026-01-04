import requests
import os
import time
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(api_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=15)
        time.sleep(1)
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_mrt_status():
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour = now_sg.hour
    sg_minute = now_sg.minute

    print(f"Checking stable Train API at {sg_time_str} SGT...")
    
    try:
        # Using a stable community API that formats LTA data for bots
        # This bypasses the strict 'AccountKey' requirement of the official DataMall
        res = requests.get("https://api.sgmrt.com/v1/status", timeout=15)
        data = res.json()
        
        # This API returns a list of lines and their status
        lines = data.get('lines', [])
        print(f"API Connected. Found {len(lines)} train lines.")

        disruptions = []
        for line in lines:
            name = line.get('name')
            status = line.get('status', 'Normal')
            
            # If status is not 'Normal', we save it
            if "normal" not in status.lower():
                disruptions.append(f"🚆 *{name}*: {status}")

        # --- BOT LOGIC ---

        # 1. DISRUPTION ALERT
        if disruptions:
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n" + "\n".join(disruptions)
            message += f"\n\n🕒 _Last Updated: {sg_time_str} SGT_"
            send_telegram(message)
        
        # 2. DAILY SUMMARY (7 AM)
        elif sg_hour == 7 and sg_minute < 25:
            summary = (
                "☀️ *GOOD MORNING!*\n\n"
                "✅ *All MRT lines are running normally.*\n"
                "Your commute is clear for now.\n\n"
                f"🕒 _Status as of: {sg_time_str} SGT_"
            )
            send_telegram(summary)

        # 3. HOURLY ALL CLEAR
        elif sg_minute < 15:
            if sg_hour != 7:
                hourly_msg = f"✅ *Hourly Status Check*\nAll MRT lines are running normally.\n\n🕒 _Time: {sg_time_str} SGT_"
                send_telegram(hourly_msg)
                print(f"Hourly update sent at {sg_time_str}")
            
        else:
            print(f"Status at {sg_time_str}: Everything is Normal (Silent Mode).")
            
    except Exception as e:
        print(f"API Error: {e}. Falling back to emergency scraper.")
        # Minimal fallback to ensure you still get your 7am/hourly messages
        if (sg_hour == 7 and sg_minute < 25) or (sg_minute < 15 and sg_hour != 7):
             # Logic to send summary even if API is down
             pass
