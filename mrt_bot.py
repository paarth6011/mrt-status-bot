import requests
from bs4 import BeautifulSoup
import os

# These pull the hidden secrets you just saved in GitHub
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://www.mytransport.sg/trainstatus"

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": message})

def check_mrt():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This looks for the status image you identified in the CSS earlier
        img_tag = soup.find('img', class_='mrt-status-img')
        
        if img_tag:
            src = img_tag.get('src')
            # If the image name is NOT 'Normal.png', send an alert!
            if "Normal.png" not in src:
                status_name = src.split('/')[-1]
                send_telegram(f"🚨 MRT ALERT: Status image changed to '{status_name}'. Check: {URL}")
            else:
                send_telegram("✅ MRT Monitor Heartbeat: System is online and checking.")
        else:
            print("Could not find status image. Site layout may have changed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt()
