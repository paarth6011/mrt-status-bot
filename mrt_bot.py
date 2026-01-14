import requests
import os
from datetime import datetime, timedelta

# Configuration
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbyPT-j7jck8F4aXGkghArOnhDqlPNENzNB2IsMWaJ42soLquJgA4E3Oo0YbFZF2OyVm/exec"

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": True}
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
        session = requests.Session()
        res = session.get(BRIDGE_URL, timeout=30, allow_redirects=True)
        data = res.json()
        
        value = data.get('value', {})
        status_info = value[0] if isinstance(value, list) and len(value) > 0 else value
        
        # Pull the message content directly
        alert_msg = status_info.get('Message', [])
        
        # 1. NEW LOGIC: If there is ANY text in the message field, alert immediately
        if alert_msg and len(alert_msg) > 0:
            details = ""
            for alert in alert_msg:
                line = alert.get('Line', 'MRT')
                content = alert.get('Content', '')
                if content:
                    details += f"*{line}*: {content}\n"
            
            if details:
                msg = (
                    "⚠️ *TRAIN SERVICE NOTICE*\n\n"
                    "🔴 *SMRT Status:*\n"
                    f"{details}\n"
                    f"🕒 _Last Updated: {sg_time_str}_"
                )
                send_telegram(msg)
                print("🚨 Live notice sent.")
                return # Skip normal updates if an alert was sent

        # 2. MORNING SUMMARY (Only at 7:00 AM)
        # 2. MORNING SUMMARY (Window between 7:00 and 7:09 AM)
        if sg_hour == 7 and sg_minute < 10:
            msg = f"☀️ *GOOD MORNING*\n\n🔴 *SMRT Status:*\nAll lines normal.\n\n🕒 _Status: {sg_time_str}_"
            send_telegram(msg)
            print("☀️ Morning summary sent.")

        # 3. HOURLY HEARTBEAT (Window for the first 30 mins of every hour)
        elif sg_minute < 30:
            msg = f"✅ *SMRT Status Update*\n\n🔴 *SMRT Status:*\nAll lines normal.\n\n🕒 _Time: {sg_time_str}_"
            send_telegram(msg)
            print("✅ Normal status message sent.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
