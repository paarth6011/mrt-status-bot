import requests
import os

# These pull the hidden secrets you saved in GitHub
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LTA_KEY = os.getenv("LTA_KEY")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(api_url, data=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

def check_mrt():
    # Official LTA Train Service Alert API endpoint
    url = "http://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
    headers = {"AccountKey": LTA_KEY, "accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        # If the API is working, we check the 'Status' field
        # Status 1 = Normal, Status 2 = Disruption
        data = response.json()
        value = data.get('value', {})
        status = value.get('Status', 1) 
        
        if status != 1:
            # If there's a delay, LTA provides a specific message
            disruption_msg = value.get('Message', '🚨 MRT Disruption Detected!')
            send_telegram(f"📢 LTA OFFICIAL ALERT: {disruption_msg}")
            print("Disruption detected. Message sent.")
        else:
            print("System confirmed: Status is Normal.")
            
    except Exception as e:
        print(f"LTA API Error: {e}")

if __name__ == "__main__":
    check_mrt()
