import requests
import os
import sys
from datetime import datetime, timedelta

def log(msg):
    print(msg, flush=True)

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LTA_KEY = os.getenv("LTA_KEY")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(api_url, data=payload, timeout=15)
        log(f"Telegram Sent: {r.status_code}")
    except Exception as e:
        log(f"Telegram Failed: {e}")

def check_mrt_status():
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour, sg_minute = now_sg.hour, now_sg.minute

    log(f"--- BOT RUN START: {sg_time_str} SGT ---")
    
    # Official LTA endpoint
    url = "http://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
    headers = {'AccountKey': LTA_KEY, 'accept': 'application/json'}
    
    try:
        log("Fetching official LTA data...")
        res = requests.get(url, headers=headers, timeout=20)
        data = res.json()
        
        status_data = data.get('value', {})
        # OData sometimes returns a list; handle both
        if isinstance(status_data, list) and len(status_data) > 0:
            status_data = status_data[0]
            
        status_code = str(status_data.get('Status', '1'))
        alert_msg = status_data.get('Message', [])

        # --- THE OUTPUT STYLE YOU REQUESTED ---
        if status_code == "2":
            log("Disruption detected!")
            details = ""
            for alert in alert_msg:
                details += f"{alert.get('Line', 'Line')}: {alert.get('Content', 'Service Delay')}\n"
            
            message = (
                "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
                "🔴 *SMRT Status:*\n"
                f"{details}\n"
                f"🕒 _Last Updated: {sg_time_str}_"
            )
            send_telegram(message)
        
        # 1. Morning Summary (7 AM)
        elif sg_hour == 7 and sg_minute < 30:
            message = (
                "☀️ *GOOD MORNING*\n\n"
                "✅ *SMRT Status:*\n"
                "All lines are running normally.\n\n"
                f"🕒 _Status: {sg_time_str}_"
            )
            send_telegram(message)

        # 2. TEST/MANUAL RUN (Ensures you see a message NOW)
        else:
            log("No disruption. Sending confirmation message...")
            message = (
                "✅ *Manual Status Check*\n\n"
                "🔴 *SMRT Status:*\n"
                "All MRT lines are running normally.\n\n"
                f"🕒 _Time: {sg_time_str}_"
            )
            send_telegram(message)
            
    except Exception as e:
        log(f"❌ Error: {e}")
        send_telegram(f"🤖 *Bot Alert*\nConnection to LTA failed.\n🕒 _Time: {sg_time_str}_")

if __name__ == "__main__":
    check_mrt_status()
    log("--- BOT RUN FINISHED ---")
