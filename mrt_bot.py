import requests
import os
from datetime import datetime, timedelta

# Environment Variables
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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
    sg_hour, sg_minute = now_sg.hour, now_sg.minute

    print(f"Checking stable Transit API at {sg_time_str} SGT...")
    
    try:
        # Using a reliable community API that bridges LTA data
        # This is a public, bot-friendly JSON endpoint
        res = requests.get("https://train-status.sgmrt.com/api/v1/status", timeout=15)
        
        if res.status_code != 200:
            print(f"API Error: {res.status_code}")
            return

        data = res.json()
        lines = data.get('lines', []) # Get all MRT lines
        print(f"Success! Found {len(lines)} train lines.")

        disruptions = []
        for line in lines:
            name = line.get('name', 'Unknown')
            status = line.get('status', 'Normal')
            
            # If status is NOT 'Normal Service', capture it
            if "normal" not in status.lower():
                disruptions.append(f"🚆 *{name}*: {status}")

        # --- BOT LOGIC ---

        # 1. LIVE DISRUPTION ALERT
        if disruptions:
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
            message += "\n".join(disruptions)
            send_telegram(message + f"\n\n🕒 _Updated: {sg_time_str}_")
        
        # 2. DAILY SUMMARY (7 AM)
        elif sg_hour == 7 and sg_minute < 25:
            send_telegram(f"☀️ *GOOD MORNING!*\n\n✅ *All MRT lines are running normally.*\n🕒 _Status: {sg_time_str}_")

        # 3. HOURLY ALL CLEAR
        elif sg_minute < 15 and sg_hour != 7:
            send_telegram(f"✅ *Hourly Status Check*\nAll MRT lines are running normally.\n🕒 _Time: {sg_time_str}_")
            
        else:
            print(f"Everything Normal at {sg_time_str}. Silent Mode.")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
