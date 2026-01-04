import requests
import os
from datetime import datetime, timedelta

# Environment Variables
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
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour, sg_minute = now_sg.hour, now_sg.minute

    print(f"Connecting to Official LTA DataMall at {sg_time_str} SGT...")
    
    # Updated URL: The 'ltaodataservice' part is often sensitive to capitalization or slight path changes
    url = "http://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
    
    headers = {
        'AccountKey': LTA_KEY,
        'accept': 'application/json'
    }
    
    try:
        # Note: We use http instead of https as some LTA endpoints prefer it for OData
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"LTA Server returned error code: {response.status_code}")
            # If 404 persists, we try the alternative https path
            if response.status_code == 404:
                url = "http://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlert"
                response = requests.get(url, headers=headers, timeout=20)
            
        data = response.json()
        status_data = data.get('value', {})
        
        # If the 'value' is a list (common for OData), we take the first item
        if isinstance(status_data, list) and len(status_data) > 0:
            status_data = status_data[0]
            
        status_code = status_data.get('Status', 1)
        alert_msg = status_data.get('Message', [])

        print(f"LTA Data received. Status Code: {status_code}")

        # 1. LIVE DISRUPTION ALERT
        if str(status_code) == "2":
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
            if isinstance(alert_msg, list):
                for alert in alert_msg:
                    message += f"🚆 *{alert.get('Line', 'MRT')}*: {alert.get('Content', 'Service Delay')}\n"
            send_telegram(message + f"\n🕒 _Updated: {sg_time_str}_")
        
        # 2. DAILY SUMMARY (7 AM)
        elif sg_hour == 7 and sg_minute < 25:
            send_telegram(f"☀️ *GOOD MORNING!*\n\n✅ *All lines running normally.*\n🕒 _Status: {sg_time_str}_")

        # 3. HOURLY ALL CLEAR
        elif sg_minute < 15 and sg_hour != 7:
            send_telegram(f"✅ *Hourly Status Check*\nAll MRT lines running normally.\n🕒 _Time: {sg_time_str}_")
            
    except Exception as e:
        print(f"LTA Connection Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
