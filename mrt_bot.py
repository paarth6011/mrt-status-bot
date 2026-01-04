import requests
import os
from datetime import datetime, timedelta

# Environment Variables (LTA_KEY is the one you just got)
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LTA_KEY = os.getenv("LTA_KEY") 

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(api_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=15)
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_mrt_status():
    # Calculate Singapore Time (UTC +8)
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour = now_sg.hour
    sg_minute = now_sg.minute

    print(f"Connecting to Official LTA DataMall at {sg_time_str} SGT...")
    
    # Official headers required by LTA
    headers = {
        'AccountKey': LTA_KEY,
        'accept': 'application/json'
    }
    url = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        
        # LTA status: 1 = Normal, 2 = Disruption
        status_data = data.get('value', {})
        status_code = status_data.get('Status', 1)
        alert_msg = status_data.get('Message', [])

        print(f"LTA Data received. Status Code: {status_code}")

        # --- BOT LOGIC FLOW ---

        # 1. LIVE DISRUPTION ALERT
        if status_code == 2:
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
            for alert in alert_msg:
                line = alert.get('Line', 'MRT')
                content = alert.get('Content', 'Service Delay')
                message += f"🚆 *{line}*: {content}\n"
            message += f"\n🕒 _Last Updated: {sg_time_str} SGT_"
            send_telegram(message)
            print("Disruption alert sent.")
        
        # 2. DAILY SUMMARY (7:00 AM SGT)
        elif sg_hour == 7 and sg_minute < 25:
            summary = (
                "☀️ *GOOD MORNING!*\n\n"
                "✅ *All MRT lines are running normally.*\n"
                "Your commute is clear for now.\n\n"
                f"🕒 _Status as of: {sg_time_str} SGT_"
            )
            send_telegram(summary)
            print("Daily summary sent.")

        # 3. HOURLY "ALL CLEAR"
        elif sg_minute < 15:
            if sg_hour != 7:
                hourly_msg = f"✅ *Hourly Status Check*\nAll MRT lines are running normally.\n\n🕒 _Time: {sg_time_str} SGT_"
                send_telegram(hourly_msg)
                print(f"Hourly update sent at {sg_time_str}")
            
        else:
            print(f"Status at {sg_time_str}: Everything is Normal (Silent Mode).")
            
    except Exception as e:
        print(f"LTA Connection Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
