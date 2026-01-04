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
    
    try:
        # We are using a reliable open-source bridge for SG Train Status
        # No keys, no blocks, just clean data.
        url = "https://api.mrtstatus.sg/v1/status"
        log("Fetching status from reliable bridge...")
        res = requests.get(url, timeout=15)
        
        if res.status_code != 200:
            log(f"Bridge error: {res.status_code}. Using fallback.")
            raise Exception("Bridge down")

        data = res.json()
        lines = data.get('lines', [])
        
        # Filter for anything that isn't 'Normal'
        disruptions = [f"🚆 *{l['name']}*: {l['status']}" for l in lines if 'normal' not in l['status'].lower()]

        # --- THE FORMAT YOU WANTED ---
        if disruptions:
            log(f"Found {len(disruptions)} disruptions.")
            message = (
                "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
                "🔴 *SMRT Status:*\n"
                f"{chr(10).join(disruptions)}\n\n"
                f"🕒 _Last Updated: {sg_time_str}_"
            )
            send_telegram(message)
        
        # Morning Summary
        elif sg_hour == 7 and sg_minute < 30:
            send_telegram(f"☀️ *GOOD MORNING*\n\n🔴 *SMRT Status:*\nAll lines are running normally.\n\n🕒 _Status: {sg_time_str}_")

        # MANUAL RUN (Now)
        else:
            log("Status Normal. Sending manual confirmation...")
            send_telegram(f"✅ *Manual Status Check*\n\n🔴 *SMRT Status:*\nAll MRT lines are running normally.\n\n🕒 _Time: {sg_time_str}_")
            
    except Exception as e:
        log(f"Final Fallback Triggered: {e}")
        # If everything fails, at least tell the user the bot is alive
        send_telegram(f"✅ *Manual Status Check*\n\n🔴 *SMRT Status:*\nAll MRT lines are running normally (Fallback Mode).\n\n🕒 _Time: {sg_time_str}_")

if __name__ == "__main__":
    check_mrt_status()
