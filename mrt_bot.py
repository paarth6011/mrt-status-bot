import requests
import os

# GitHub Secrets
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LTA_KEY = os.getenv("LTA_KEY")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(api_url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_mrt():
    # Official endpoint for train alerts
    url = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
    headers = {
        "AccountKey": LTA_KEY,
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"LTA Response Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            value = data.get('value', {})
            status = value.get('Status', 1) 
            
            # FOR TESTING: Sending a heartbeat even if status is Normal
            send_telegram(f"✅ Bot is Online. LTA Status: {'Normal' if status == 1 else 'Disruption'}")
            
            if status != 1:
                msg = value.get('Message', '🚨 MRT Disruption Detected!')
                send_telegram(f"📢 LTA ALERT: {msg}")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Script Error: {e}")

if __name__ == "__main__":
    check_mrt()
