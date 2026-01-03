import requests
import os
import time

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Using Markdown to ensure the message looks professional
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=15)
    time.sleep(2)

def check_mrt_status():
    print("🚀 Sending a FAKE disruption alert for testing...")
    
    # MANUALLY CREATING A FAKE ALERT FOR THIS TEST
    smrt_info = "North-South Line: Expect 15 mins additional travel time from Jurong East to Woodlands due to a track fault at Marsiling station. Free regular buses are available between affected stations."
    sbs_info = "Normal Service"

    # This logic mimics a real detection
    message = "⚠️ *LIVE TRAIN SERVICE UPDATE*\n\n"
    message += f"🔴 *SMRT Status:*\n_{smrt_info}_\n\n"
    message += f"🟣 *SBS Status:*\n_{sbs_info}_\n"
    message += "\n🕒 _Check official sources for latest shuttle bus info._"
    message += "\n📍 [View Official Rail Map](https://www.lta.gov.sg/content/ltagov/en/getting_around/public_transport/rail_network.html)"
    
    send_telegram(message)
    print("✅ Fake alert sent to Telegram.")

if __name__ == "__main__":
    check_mrt_status()
