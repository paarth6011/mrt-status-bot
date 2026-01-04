import requests
import os
from datetime import datetime, timedelta

# Environment Variables
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
# The Bridge URL you just generated
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
    # Calculate Singapore Time (UTC +8)
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour, sg_minute = now_sg.hour, now_sg.minute

    print(f"--- FETCHING DATA VIA GOOGLE BRIDGE AT {sg_time_str} ---")
    
    try:
        # GitHub will resolve script.google.com perfectly
        res = requests.get(BRIDGE_URL, timeout=25)
        data = res.json()
        
        # Handle the official LTA DataMall structure
        value = data.get('value', {})
        if isinstance(value, list) and len(value) > 0:
            status_info = value[0]
        else:
            status_info = value
            
        status_code = str(status_info.get('Status', '1'))
        alert_msg = status_info.get('Message', [])

        # --- THE EXACT STYLE YOU REQUESTED ---

        # 1. LIVE DISRUPTION ALERT (Status 2 = Disruption)
        if status_code == "2":
            details = ""
            if isinstance(alert_msg, list):
                for alert in alert_msg:
                    line = alert.get('Line', 'MRT')
                    content = alert.get('Content', 'Service Delay')
                    details += f"{line}: {content}\n"
            
            message = (
                "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
                "🔴 *SMRT Status:*\n"
                f"{details}\n"
                f"🕒 _Last Updated: {sg_time_str}_"
            )
            send_telegram(message)
        
        # 2. DAILY SUMMARY (7 AM SGT)
        elif sg_hour == 7 and sg_minute < 30:
            message = (
                "☀️ *GOOD MORNING*\n\n"
                "🔴 *SMRT Status:*\n"
                "All lines are running normally. No disruptions reported.\n\n"
                f"🕒 _Status as of {sg_time_str}_"
            )
            send_telegram(message)

        # 3. MANUAL TEST / HOURLY CHECK
        # Forces a message if run manually or at the top of the hour
        else:
            status_text = "All MRT lines are running normally."
            message = (
                "✅ *Manual Status Check*\n\n"
                "🔴 *SMRT Status:*\n"
                f"{status_text}\n\n"
                f"🕒 _Time: {sg_time_str}_"
            )
            send_telegram(message)
