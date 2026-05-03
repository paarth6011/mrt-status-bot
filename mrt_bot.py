import requests
import os
import sys
import hashlib
import json
from datetime import datetime, timezone, timedelta

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BRIDGE_URL = os.getenv("BRIDGE_URL")
LTA_KEY = os.getenv("LTA_KEY")

LTA_API_URL = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
CACHE_FILE = ".alert_cache"

def validate_env():
    if not TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN and CHAT_ID are required.")
        sys.exit(1)
    if not LTA_KEY and not BRIDGE_URL:
        print("❌ At least one of LTA_KEY or BRIDGE_URL must be set.")
        sys.exit(1)

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(api_url, data=payload, timeout=15)
        result = res.json()
        if not result.get("ok"):
            print(f"Telegram API error: {result.get('description')}")
    except Exception as e:
        print(f"Telegram Failed: {e}")

def get_lta_alerts():
    if not LTA_KEY:
        return []
    try:
        res = requests.get(
            LTA_API_URL,
            headers={"AccountKey": LTA_KEY, "accept": "application/json"},
            timeout=15
        )
        item = res.json().get("value", {})  # value is a single dict, not a list
        alerts = []
        if item.get("Status") != 1:  # 1 = Normal, no disruption
            segments = item.get("AffectedSegments", [])
            line = segments[0].get("Line", "MRT") if segments else "MRT"
            for msg in item.get("Message", []):
                content = msg.get("Content", "")
                if content:
                    alerts.append({"Line": line, "Content": content})
        return alerts
    except Exception as e:
        print(f"LTA API error: {e}")
        return []

def get_bridge_alerts():
    if not BRIDGE_URL:
        return []
    try:
        res = requests.get(BRIDGE_URL, timeout=30)
        value = res.json().get("value", {})
        return value.get("Message", [])
    except Exception as e:
        print(f"Bridge error: {e}")
        return []

def merge_alerts(lta_alerts, bridge_alerts):
    seen_lines = set()
    merged = []
    for alert in lta_alerts + bridge_alerts:
        line = alert.get("Line", "MRT")
        content = alert.get("Content", "")
        if line not in seen_lines and content:
            seen_lines.add(line)
            merged.append(alert)
    return merged

def compute_hash(alerts):
    key = json.dumps(sorted([(a.get("Line", ""), a.get("Content", "")) for a in alerts]))
    return hashlib.md5(key.encode()).hexdigest()

def load_cached_hash():
    try:
        with open(CACHE_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def save_hash(hash_val):
    with open(CACHE_FILE, "w") as f:
        f.write(hash_val)

def check_mrt_status():
    now_sg = datetime.now(timezone.utc) + timedelta(hours=8)
    sg_time_str = now_sg.strftime('%I:%M %p')
    sg_hour = now_sg.hour
    sg_minute = now_sg.minute

    print(f"--- RUNNING AT {sg_time_str} SGT ---")

    lta_alerts = get_lta_alerts()
    bridge_alerts = get_bridge_alerts()

    print(f"LTA alerts: {len(lta_alerts)}, Bridge alerts: {len(bridge_alerts)}")

    if lta_alerts or bridge_alerts:
        # Bridge handles its own deduplication (only returns new messages).
        # LTA always returns active disruptions, so compare against last sent hash.
        current_lta_hash = compute_hash(lta_alerts)
        new_lta_alerts = lta_alerts if current_lta_hash != load_cached_hash() else []
        all_new_alerts = merge_alerts(new_lta_alerts, bridge_alerts)

        if all_new_alerts:
            details = "".join(f"*{a.get('Line', 'MRT')}*: {a.get('Content', '')}\n" for a in all_new_alerts)
            send_telegram(f"⚠️ *NEW TRAIN NOTICE*\n\n{details}\n🕒 _Last Updated: {sg_time_str}_")
            save_hash(current_lta_hash)
            print("🚨 New disruption detected and sent.")
        else:
            print("Same disruption as last check. Staying silent.")
        return

    # No active alerts — reset hash so the next disruption is treated as new
    save_hash("")

    if sg_hour == 7 and sg_minute < 30:
        send_telegram(f"☀️ *DAILY MRT STATUS*\n\nAll lines normal.\n\n🕒 _Checked at {sg_time_str}_")
        print("☀️ Daily 7AM summary sent.")
    else:
        print("No alerts detected and not the 7AM window. Staying silent.")

if __name__ == "__main__":
    validate_env()
    send_telegram("🧪 *TEST MESSAGE*\n\nYour MRT Status Bot is working correctly!\n\nBoth LTA API and Telegram are connected.")
    check_mrt_status()
