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
        # Connect to Google Bridge
        session = requests.Session()
        res = session.get(BRIDGE_URL, timeout=30, allow_redirects=True)
    
        if res.status_code != 200:
            print(f"❌ Error: Server returned {res.status_code}")
            return

        data = res.json()
        value = data.get('value', {})
        status_info = value[0] if isinstance(value, list) and len(value) > 0 else value
        alert_msg = status_info.get('Message', [])

        # 1. LIVE NOTICE LOGIC (Checks every 5-15 mins)
        if alert_msg and len(alert_msg) > 0:
            details = ""
            for alert in alert_msg:
                content = alert.get('Content', '')
                
                # FILTER: Ignore the specific planned Circle Line work spam
                if "tunnel strengthening works" in content.lower():
                    continue
                
                if content:
                    line = alert.get('Line', 'MRT')
                    details += f"*{line}*: {content}\n"
            
            # Send if there is an ACTUAL new disruption or notice
            if details:
                msg = (
                    "⚠️ *TRAIN SERVICE NOTICE*\n\n"
                    "🔴 *SMRT Status:*\n"
                    f"{details}\n"
                    f"🕒 _Last Updated: {sg_time_str}_"
                )
                send_telegram(msg)
                print("🚨 Live notice sent.")
                return # Skip scheduled updates if a notice was sent

        # 2. MORNING SUMMARY (Window for GitHub delays: 7:00 - 7:09 AM)
        if sg_hour == 7 and sg_minute < 10:
            msg = (
                "☀️ *GOOD MORNING*\n\n"
                "🔴 *SMRT Status:*\n"
                "All lines are running normally.\n\n"
                f"🕒 _Status as of {sg_time_str}_"
            )
            send_telegram(msg)
            print("☀️ Morning summary sent.")

        # 3. HOURLY HEARTBEAT (Window for GitHub delays: First 10 mins of every hour)
        elif sg_minute < 10:
            msg = (
                "✅ *SMRT Status Update*\n\n"
                "🔴 *SMRT Status:*\n"
                "All lines are running normally.\n\n"
                f"🕒 _Time: {sg_time_str}_"
            )
            send_telegram(msg)
            print("✅ Normal status message sent.")
            
        else:
            print("Skipping message: Not in a notification window and no new disruption.")
            
    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
