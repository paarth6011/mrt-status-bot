import requests
import os
from datetime import datetime, timedelta

# Configuration
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
# Your updated Google Bridge URL
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbx1LjBYCyTH7jbnzpDL6cICi784bLMDbQkl2IzXKXaWj2dWGW45BIbspObRNvtRindwTQ/exec"

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(api_url, data=payload, timeout=15)
    except Exception as e:
        print(f"Telegram Failed: {e}")

def check_mrt_status():
    # Calculate Singapore Time (UTC+8)
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour = now_sg.hour
    sg_minute = now_sg.minute
    
    print(f"--- RUNNING AT {sg_time_str} SGT ---")
    
    try:
        # The Google Script now handles the "memory" of the messages
        res = requests.get(BRIDGE_URL, timeout=30)
        data = res.json()
        value = data.get('value', {})
        alert_msg = value.get('Message', [])

        # 1. FAULT DETECTION (Pings only if the Google Script sends a NEW/DIFFERENT message)
        if alert_msg:
            details = ""
            for alert in alert_msg:
                line = alert.get('Line', 'MRT')
                content = alert.get('Content', '')
                details += f"*{line}*: {content}\n"
            
            if details:
                send_telegram(f"⚠️ *NEW TRAIN NOTICE*\n\n{details}\n🕒 _Last Updated: {sg_time_str}_")
                print("🚨 New disruption detected and sent.")
                return 

        # 2. DAILY SUMMARY (Once a day at 7:00 AM)
        if sg_hour == 7 and sg_minute < 10:
            send_telegram(f"☀️ *DAILY MRT STATUS*\n\nAll lines normal.\n\n🕒 _Checked at {sg_time_str}_")
            print("☀️ Daily 7AM summary sent.")
            
        else:
            print("No new changes detected and not the 7AM window. Staying silent.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
