import requests
import os

# These pull from your GitHub Secrets
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LTA_KEY = os.getenv("LTA_KEY")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": message})

def check_mrt():
    # FIXED: Using https instead of http
    url = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
    headers = {"AccountKey": LTA_KEY, "accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        
        # DEBUG: This prints the status code (e.g., 200, 401, 403)
        print(f"LTA Server Response Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # If the API returns data, check the MRT status
            value = data.get('value', {})
            status = value.get('Status', 1)
            
            if status != 1:
                msg = value.get('Message', '🚨 MRT Disruption Detected!')
                send_telegram(f"📢 LTA ALERT: {msg}")
            else:
                print("Status is Normal.")
        else:
            # This prints the actual error message from LTA
            print(f"Server rejected request: {response.text}")
            
    except Exception as e:
        print(f"Script Error: {e}")

if __name__ == "__main__":
    check_mrt()
