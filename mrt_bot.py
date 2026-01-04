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
    # Calculate Singapore Time (UTC+8)
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour = now_sg.hour
    sg_minute = now_sg.minute
    
    print(f"--- RUNNING AT {sg_time_str} SGT ---")
    
    try:
        # Connect to Google Bridge to bypass DNS blocks
        session = requests.Session()
        print("Connecting to Google Bridge...")
        res = session.get(BRIDGE_URL, timeout=30, allow_redirects=True)
    
        if res.status_code != 200:
            print(f"❌ Error: Server returned {res.status_code}")
            return

        data = res.json()
        value = data.get('value', {})
        
        # Parse LTA OData structure
        status_info = value[0] if isinstance(value, list) and len(value) > 0 else value
        status_code = str(status_info.get('Status', '1'))
        alert_msg = status_info.get('Message', [])

        # 1. LIVE DISRUPTION (Priority: Runs every 15 mins if Status is 2)
        if status_code == "2":
            details = ""
            if isinstance(alert_msg, list):
                for alert in alert_msg:
                    line = alert.get('Line', 'MRT')
                    content = alert.get('Content', 'Service Delay')
                    details += f"*{line}*: {content}\n"
            
            msg = (
                "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
                "🔴 *SMRT Status:*\n"
                f"{details}\n"
                f"🕒 _Last Updated: {sg_time_str}_"
            )
            send_telegram(msg)
            print("🚨 Disruption message sent.")
        
        # 2. MORNING SUMMARY (Only at 07:00 AM)
        elif sg_hour == 7 and sg_minute == 0:
            msg = (
                "☀️ *GOOD MORNING*\n\n"
                "🔴 *SMRT Status:*\n"
                "All lines are running normally.\n\n"
                f"🕒 _Status as of {sg_time_str}_"
            )
            send_telegram(msg)
            print("☀️ Morning summary sent.")

        # 3. HOURLY HEARTBEAT (Only at :00 of every other hour)
        elif sg_minute < 15:
            msg = (
                "✅ *SMRT Status Update*\n\n"
                "🔴 *SMRT Status:*\n"
                "All lines are running normally.\n\n"
                f"🕒 _Time: {sg_time_str}_"
            )
            send_telegram(msg)
            print("✅ Normal status message sent.")
        
        else:
            print("Skipping message: Not at the top of the hour and no disruption found.")
            
    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
