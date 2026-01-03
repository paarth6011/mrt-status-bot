import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": message})

def check_smrt_status():
    # SMRT's official status page
    url = "https://www.smrt.com.sg/Travel/Service-Indicator"
    
    try:
        # Step 1: Tell Telegram we are checking
        print("Checking SMRT website...")
        
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This looks for the status container on their site
        # Note: We look for keywords that indicate trouble
        page_text = soup.get_text().lower()
        
        trouble_keywords = ["delay", "disruption", "no train service", "track fault"]
        
        found_issues = [word for word in trouble_keywords if word in page_text]
        
        if found_issues:
            issue_list = ", ".join(found_issues)
            send_telegram(f"🚨 SMRT WEBSITE ALERT: Detected keywords: {issue_list}. Check here: {url}")
        else:
            print("No disruption keywords found on the SMRT page.")
            # Optional: Uncomment below to get a 'System OK' message
            # send_telegram("✅ SMRT Status: Normal service reported on website.")

    except Exception as e:
        print(f"Error checking SMRT: {e}")

if __name__ == "__main__":
    check_smrt_status()
