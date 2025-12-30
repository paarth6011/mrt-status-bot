import requests
import os

# GitHub Secrets
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LTA_KEY = os.getenv("LTA_KEY")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Basic error handling: if this fails, it won't crash the whole bot
    try:
        requests.post(api_url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_mrt():
    # This is the most stable official endpoint for train alerts
    url = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
    
    headers = {
        "AccountKey": LTA_KEY,
        "accept": "application/json",
        "User-Agent": "Mozilla/5.0" # Prevents some 404/403 blocks
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"LTA Response Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # LTA returns a 'value' object
            value = data.get('value', {})
            status = value.get('Status', 1) 
            
            if status != 1:
                # If there is a disruption, send the official message
                msg = value.get('Message', '🚨 MRT Disruption Detected!')
                send_telegram(f"📢 LTA ALERT: {msg}")
            else:
                print("LTA confirms: Status is Normal.")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Script Error: {e}")

if __name__ == "__main__":
    check_mrt()
