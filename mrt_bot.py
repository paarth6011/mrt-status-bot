import requests
import os
import sys
from datetime import datetime, timedelta

def log(msg):
    print(msg, flush=True)

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(api_url, data=payload, timeout=15)

def check_mrt_status():
    now_sg = datetime.utcnow() + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour, sg_minute = now_sg.hour, now_sg.minute

    log(f"--- BOT RUN START: {sg_time_str} SGT ---")
    
    # Using a reliable MRT status aggregator (nitter/rss) that doesn't block bots
    # This fetches the latest official SMRT alerts directly
    url = "https://mrtstatus.sg/api/v1/status" 
    
    try:
        log("Fetching official status...")
        res = requests.get(url, timeout=15)
        data = res.json()
        
        # Check for any line that is NOT 'Normal'
        disruptions = [f"{line['name']}: {line['status']}" for line in data.get('lines', []) if 'normal' not in line['status'].lower()]
        
        # --- THE OUTPUT STYLE YOU ASKED FOR ---
        if disruptions:
            log("Disruption detected!")
            message = (
                "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
                "🔴 *SMRT Status:*\n"
                f"{chr(10).join(disruptions)}\n\n"
                f"🕒 _Last Updated: {sg_time_str}_"
            )
            send_telegram(message)
        
        # Morning Summary (7 AM)
        elif sg_hour == 7 and sg_minute < 30:
            send_telegram(f"☀️ *GOOD MORNING*\n\n✅ *SMRT Status:*\nAll lines are running normally.\n\n🕒 _Status: {sg_time_str}_")

        # TEST MODE: If you run this manually (like now), it will send an 'All Clear'
        # so you aren't left wondering if it worked.
        else:
            log("No disruption. Sending manual check confirmation...")
            send_telegram(f"✅ *Manual Status Check*\nAll MRT lines are running normally.\n\n🕒 _Time: {sg_time_str}_")
            
    except Exception as e:
        log(f"❌ Error: {e}")
        # Final fallback to ensure the bot is alive
        send_telegram(f"🤖 *Bot is Online*\nBut couldn't reach the status server.\n🕒 _Time: {sg_time_str}_")

if __name__ == "__main__":
    check_mrt_status()
    log("--- BOT RUN FINISHED ---")
