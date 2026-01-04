import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(api_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=15)
        time.sleep(2)
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_mrt_status():
    # Calculate Singapore Time (UTC +8)
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour = now_sg.hour
    sg_minute = now_sg.minute

    print(f"Checking SGTrains for live alerts at {sg_time_str} SGT...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # Scrape SGTrains (Covers all lines: SMRT, SBS, LRT)
        res = requests.get("https://www.sgtrains.com/guide-status.html", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # SGTrains usually groups lines into a status table or list
        lines = soup.select('.status-item') 
        disruptions = []

        for line in lines:
            name = line.select_one('.line-name').get_text(strip=True) if line.select_one('.line-name') else "Unknown Line"
            status = line.select_one('.status-text').get_text(strip=True) if line.select_one('.status-text') else "Normal"
            
            # If status is NOT normal, add it to our alert list
            if "normal" not in status.lower():
                disruptions.append(f"🚆 *{name}*: {status}")

        # --- BOT LOGIC FLOW ---

        # 1. THE DISRUPTION ALERT (High Priority)
        # Sends immediately if any line is not "Normal"
        if disruptions:
            message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
            message += "\n".join(disruptions)
            message += f"\n\n🕒 _Last Updated: {sg_time_str} SGT_"
            send_telegram(message)
        
        # 2. THE DAILY SUMMARY (7:00 AM SGT)
        # Sends once a day during the 7 AM hour
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
        # Sends at the top of every hour (except 7 AM to avoid double-posting)
        elif sg_minute < 15:
            # This gate ensures you only get one message per hour
            hourly_msg = f"✅ *Hourly Status Check*\nAll MRT lines are running normally.\n\n🕒 _Time: {sg_time_str} SGT_"
            send_telegram(hourly_msg)
            print(f"Hourly update sent at {sg_time_str}")
            
        else:
            # Silent mode: script runs in background but doesn't message Telegram
            print(f"Status at {sg_time_str}: Everything is Normal (Silent Mode).")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
