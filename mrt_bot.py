import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LTA_KEY = os.getenv("LTA_KEY")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": message})

def test_lta_connection():
    # TEST A: Send a "Starting Test" message to your phone
    send_telegram("🔍 Starting LTA Connection Test...")

    # TEST B: Check Bus Arrival (usually more stable for new keys)
    bus_url = "https://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode=60121"
    headers = {"AccountKey": LTA_KEY, "accept": "application/json"}
    
    try:
        response = requests.get(bus_url, headers=headers, timeout=15)
        print(f"LTA Bus API Code: {response.status_code}")
        
        if response.status_code == 200:
            send_telegram("✅ LTA Key is WORKING for Bus Data. (Wait 24h for Train Data).")
        else:
            send_telegram(f"❌ LTA Key failed for Bus too. Error: {response.status_code}")
            print(f"Full Error: {response.text}")
            
    except Exception as e:
        send_telegram(f"⚠️ Script Error: {str(e)}")

if __name__ == "__main__":
    test_lta_connection()
