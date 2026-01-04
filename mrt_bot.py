import requests
import os
from datetime import datetime, timedelta

# Configuration
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
# Use the exact URL from your screenshot (image_b0cc0a.jpg)
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
    print(f"--- RUNNING AT {sg_time_str} SGT ---")
    
    try:
        # We use a Session to properly handle the Google redirect handshake
        session = requests.Session()
        print("Connecting to Google Bridge...")
        
        # allow_redirects=True is vital for Google Apps Script
        res = session.get(BRIDGE_URL, timeout=30, allow_redirects=True)
        
        if res.status_code != 200:
            print(f"❌ Error: Server returned {res.status_code}")
            return

        data = res.json()
        value = data.get('value', {})
        
        # Handle both list and object formats from OData
        status_info = value[0] if isinstance(value, list) and len(value) > 0 else value
        status_code = str(status_info.get('Status', '1'))
        alert_msg = status_info.get('Message', [])

        # --- THE OUTPUT STYLE YOU REQUESTED ---
        
        # 1. LIVE DISRUPTION (Status 2)
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
        
        # 2. ALL CLEAR (Normal Status)
        else:
            msg = (
                "✅ *SMRT Status Update*\n\n"
                "🔴 *SMRT Status:*\n"
                "All lines are running normally.\n\n"
                f"🕒 _Time: {sg_time_str}_"
            )
            send_telegram(msg)
            print("✅ Normal status message sent.")
            
    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
