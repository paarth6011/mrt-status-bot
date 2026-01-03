import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)

def check_mrt_status():
    # URL 1: SMRT (North-South, East-West, Circle, Thomson-East Coast)
    smrt_url = "https://www.smrt.com.sg/Travel/Service-Indicator"
    # URL 2: SBS Transit (North-East, Downtown, LRTs)
    sbs_url = "https://www.sbstransit.com.sg"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # Check SMRT
        smrt_res = requests.get(smrt_url, headers=headers, timeout=15)
        smrt_soup = BeautifulSoup(smrt_res.text, 'html.parser')
        # SMRT uses specific 'status-item' classes for their lines
        smrt_text = smrt_soup.get_text().lower()
        
        # Check SBS
        sbs_res = requests.get(sbs_url, headers=headers, timeout=15)
        sbs_soup = BeautifulSoup(sbs_res.text, 'html.parser')
        sbs_text = sbs_soup.get_text().lower()

        # Keywords that mean trouble
        alerts = ["delay", "disruption", "no service", "track fault", "longer travel time"]
        
        found = []
        for word in alerts:
            if word in smrt_text: found.append(f"SMRT: {word}")
            if word in sbs_text: found.append(f"SBS: {word}")

        if found:
            send_telegram(f"🚨 MRT ALERT DETECTED:\n" + "\n".join(found))
        else:
            print("All lines confirmed Normal.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mrt_status()
