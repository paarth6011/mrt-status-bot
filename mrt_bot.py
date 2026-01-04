import requests
import os
import time
from datetime import datetime, timedelta

# Environment Variables from GitHub Secrets
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(api_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=15)
        time.sleep(1)
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_mrt_status():
    # Calculate Singapore Time (UTC +8)
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour = now_sg.hour
    sg_minute = now_sg.minute

    print(f"Requesting official LTA DataMall at {sg_time_str} SGT...")
    
    try:
        # Official LTA Public Endpoint for Train Service Alerts
        url = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
        
        # We perform a standard GET request
        response = requests.get(url, timeout=15)
        data = response.json()
        
        # LTA 'Status' meaning: 1 = Normal, 2 = Disruption
        status_data = data.get('value', {})
        status_code = status_data.get('Status', 1)
        alert_messages = status_data.get('Message', []) 

        print(f"LTA Data received. Status Code: {status_code}")

        # --- BOT LOGIC FLOW ---

        # 1. THE DISRUPTION ALERT (High Priority)
        # If Status is 2, there is an active delay or breakdown
        if status_code == 2:
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
            for alert in alert_messages:
                line = alert.get('Line', 'MRT')
                content = alert.get('Content', 'Service Delay')
                message += f"🚆 *{line}*: {content}\n"
            message += f"\n🕒 _Last Updated: {sg_time_str} SGT_"
            send_telegram(message)
        
        # 2. THE DAILY SUMMARY (7:00 AM SGT)
        # Only triggers during the first run of the 7 AM hour
        elif sg_hour == 7 and sg_minute < 25:
            summary = (
                "☀️ *GOOD MORNING!*\n\n"
                "✅ *All MRT lines are running normally.*\n"
                "Your commute is clear for now.\n\n"
                f"🕒 _Status as of: {sg_time_str} SGT_"
            )
            send_telegram(summary)
            print("Daily summary sent.")

        # 3. THE HOURLY "ALL CLEAR"
        # Sends at the top of every hour if Status is Normal (1)
        elif sg_minute < 15:
            if sg_hour != 7: # Skip 7 AM as the Good Morning message covers it
                hourly_msg = f"✅ *Hourly Status Check*\nAll MRT lines are running normally.\n\n🕒 _Time: {sg_time_str} SGT_"
                send_telegram(hourly_msg)
                print(f"Hourly update sent at {sg_time_str}")
            
        else:
            print(f"Status at {sg_time_str}: Everything is Normal (Silent Mode).")
            
    except Exception as e:
        print(f"LTA DataMall Error: {e}")
        # If the API is completely down, we alert the logs so you know
        print("Check if LTA DataMall is reachable or requires an AccountKey.")

if __name__ == "__main__":
    check_mrt_status()
