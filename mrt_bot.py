import requests
import os
from datetime import datetime, timedelta

# Configuration
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbyPT-j7jck8F4aXGkghArOnhDqlPNENzNB2IsMWaJ42soLquJgA4E3Oo0YbFZF2OyVm/exec"

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
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour, sg_minute = now_sg.hour, now_sg.minute

    print(f"--- RUNNING AT {sg_time_str} SGT ---")
    
    try:
        # Fetch from your Google Apps Script Bridge
        res = requests.get(BRIDGE_URL, timeout=25)
        data = res.json()
        
        value = data.get('value', {})
        status_info = value[0] if isinstance(value, list) and len(value) > 0 else value
        
        status_code = str(status_info.get('Status', '1'))
        alert_msg = status_info.get('Message', [])

        # 1. DISRUPTION DETECTED
        if status_code == "2":
            details = ""
            for alert in alert_msg:
                details += f"*{alert.get('Line')}*: {alert.get('Content')}\n"
            
            msg = (
                "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
                "🔴 *SMRT Status:*\n"
                f"{details}\n"
                f"🕒 _Last Updated: {sg_time_str}_"
            )
            send_telegram(msg)
        
        # 2. MORNING SUMMARY (7 AM)
        elif sg_hour == 7 and sg_minute < 30:
            msg = (
                "☀️ *GOOD MORNING*\n\n"
                "🔴 *SMRT Status:*\n"
                "All lines are running normally.\n\n"
                f"🕒 _Status as of {sg_time_str}_"
            )
            send_telegram(msg)

        # 3. MANUAL TEST / HOURLY CHECK
        else:
            msg = (
                "✅ *Manual Status Check*\n\n"
                "🔴 *SMRT Status:*\n"
                "All MRT lines are running normally.\n\n"
                f"🕒 _Time: {sg_time_str}_"
            )
            send_telegram(msg)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
