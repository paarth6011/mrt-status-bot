import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LTA_KEY = os.getenv("LTA_KEY")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": message})

def check_mrt():
    # UPDATED URL: Using the Base Train Service Alerts endpoint
    url = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
    headers = {
        "AccountKey": LTA_KEY,
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"LTA Response Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # The API returns a 'value' object containing 'Status' and 'Message'
            status_data = data.get('value', {})
            
            # Status 1 means Normal Service
            if status_data.get('Status') != 1:
                alert_msg = status_data.get('Message', '🚨 MRT Disruption Detected!')
                send_telegram(f"📢 LTA OFFICIAL ALERT: {alert_msg}")
            else:
                print("LTA confirms: All lines are Normal.")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Script Error: {e}")

if __name__ == "__main__":
    check_mrt()
