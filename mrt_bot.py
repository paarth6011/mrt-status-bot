import requests
import os
import time
from datetime import datetime, timedelta

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

    print(f"Requesting official LTA data at {sg_time_str} SGT...")
    
    try:
        # Direct request to LTA's official train status feed
        # This bypasses the need for scraping websites
        response = requests.get("https://pax.mytransport.sg/api/train_status", timeout=15)
        data = response.json()
        
        # LTA data structure: Usually a list of lines with status codes
        # 1 = Normal, 2 = Delay, 3 = Disruption
        lines = data.get('Value', [])
        print(f"LTA Data received. Found {len(lines)} train lines.")

        disruptions = []
        for line in lines:
            name = line.get('Line', 'Unknown')
            status = line.get('Status', '1')
            msg = line.get('Message', '')

            # If status is not '1' (Normal), we alert
            if str(status) != "1":
                disruptions.append(f"🚆 *{name}*: {msg if msg else 'Service Delay'}")

        # --- BOT LOGIC FLOW ---

        # 1. THE DISRUPTION ALERT
        if disruptions:
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
            message += "\n".join(disruptions)
            message += f"\n\n🕒 _Last Updated: {sg_time_str} SGT_"
            send_telegram(message)
        
        # 2. THE DAILY SUMMARY (7:00 AM SGT)
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
        elif sg_minute < 15:
            if sg_hour != 7:
                hourly_msg = f"✅ *Hourly Status Check*\nAll MRT lines are running normally.\n\n🕒 _Time: {sg_time_str} SGT_"
                send_telegram(hourly_msg)
                print(f"Hourly update sent at {sg_time_str}")
            
        else:
            print(f"Status at {sg_time_str}: Everything is Normal (Silent Mode).")
            
    except Exception as e:
        # Fallback if LTA API is down
        print(f"LTA API Error: {e}")
        print("Falling back to silent mode.")

if __name__ == "__main__":
    check_mrt_status()
