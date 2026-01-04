import requests
import os
import time
from datetime import datetime, timedelta

# Environment Variables
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

    print(f"Connecting to SG MRT API at {sg_time_str} SGT...")
    
    try:
        # Using the community-standard SG MRT status API
        # This is more reliable for GitHub Actions than the raw LTA DataMall
        res = requests.get("https://api.sgmrt.com/v1/status", timeout=15)
        data = res.json()
        
        # The API returns a list of lines under the 'lines' key
        lines = data.get('lines', [])
        print(f"Success! API returned {len(lines)} train lines.")

        disruptions = []
        for line in lines:
            name = line.get('name', 'Unknown')
            status = line.get('status', 'Normal')
            
            # If the status text is NOT 'Normal Service', we treat it as a disruption
            if "normal" not in status.lower():
                disruptions.append(f"🚆 *{name}*: {status}")

        # --- BOT LOGIC FLOW ---

        # 1. LIVE DISRUPTION ALERT
        if disruptions:
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
            message += "\n".join(disruptions)
            message += f"\n\n🕒 _Last Updated: {sg_time_str} SGT_"
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

        # 3. HOURLY "ALL CLEAR" (Top of every hour)
        elif sg_minute < 15:
            if sg_hour != 7: # Skip 7 AM as the Good Morning message covers it
                hourly_msg = f"✅ *Hourly Status Check*\nAll MRT lines are running normally.\n\n🕒 _Time: {sg_time_str} SGT_"
                send_telegram(hourly_msg)
                print(f"Hourly update sent at {sg_time_str}")
            
        else:
            print(f"Status at {sg_time_str}: Everything is Normal (Silent Mode).")
            
    except Exception as e:
        print(f"API Connection Error: {e}")
        # Fallback: Still send scheduled messages if API is briefly down
        if (sg_hour == 7 and sg_minute < 25) or (sg_minute < 15 and sg_hour != 7):
            fallback_msg = f"✅ *Scheduled Status:* No major disruptions reported.\n🕒 _Time: {sg_time_str} SGT_"
            send_telegram(fallback_msg)

if __name__ == "__main__":
    check_mrt_status()
