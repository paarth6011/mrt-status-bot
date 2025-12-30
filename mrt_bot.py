import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LTA_KEY = os.getenv("LTA_KEY")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Basic error handling for Telegram
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)

def check_mrt():
    # EXACT CASE SENSITIVE URL
    url = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
    
    headers = {
        "AccountKey": LTA_KEY,
        "accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        # Added timeout to prevent the script from hanging
        response = requests.get(url, headers=headers, timeout=15)
        print(f"LTA Response Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # The API returns a dictionary with a 'value' key
            value = data.get('value', {})
            
            # Status 1 is Normal, anything else is a disruption
            status = value.get('Status', 1)
            
            if status != 1:
                message = value.get('Message', '🚨 MRT Disruption Detected!')
                send_telegram(f"📢 LTA ALERT: {message}")
            else:
                print("LTA confirms: Status is Normal.")
        
        elif response.status_code == 401:
            print("Error 401: Unauthorized. Check your LTA_KEY secret in GitHub.")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Script Error: {e}")

if __name__ == "__main__":
    check_mrt()
