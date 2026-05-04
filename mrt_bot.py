import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

import requests

# --- Configuration ---
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BRIDGE_URL = os.getenv("BRIDGE_URL")
LTA_KEY = os.getenv("LTA_KEY")

LTA_API_URL = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
CACHE_FILE = ".alert_cache"
DAILY_CACHE_FILE = ".daily_sent_date"
LTA_STATUS_NORMAL = 1


def validate_env() -> None:
    missing_core = [k for k, v in {"BOT_TOKEN": TOKEN, "CHAT_ID": CHAT_ID}.items() if not v]
    if missing_core:
        print(f"❌ Missing required environment variables: {', '.join(missing_core)}")
        sys.exit(1)
    if not LTA_KEY and not BRIDGE_URL:
        print("❌ At least one of LTA_KEY or BRIDGE_URL must be set.")
        sys.exit(1)


def escape_markdown(text: str) -> str:
    """Escape special characters in external API content for Telegram Markdown mode."""
    for char in ("*", "_", "`", "["):
        text = text.replace(char, f"\\{char}")
    return text


def send_telegram(message: str) -> None:
    # URL is built locally so the token is never stored in a module-level variable
    # that could appear in tracebacks or error logs.
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        res = requests.post(
            url,
            data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": True},
            timeout=15,
        )
        result = res.json()
        if not result.get("ok"):
            print(f"Telegram API error: {result.get('description')}")
    except requests.exceptions.Timeout:
        print("Telegram request failed: timed out")
    except requests.exceptions.ConnectionError:
        print("Telegram request failed: connection error")
    except Exception:
        print("Telegram request failed")


def get_lta_alerts() -> list[dict]:
    if not LTA_KEY:
        return []
    try:
        res = requests.get(
            LTA_API_URL,
            headers={"AccountKey": LTA_KEY, "accept": "application/json"},
            timeout=15,
        )
        res.raise_for_status()
        data = res.json().get("value", {})
        if data.get("Status") == LTA_STATUS_NORMAL:
            return []
        segments = data.get("AffectedSegments", [])
        line = segments[0].get("Line", "MRT") if segments else "MRT"
        return [
            {"Line": line, "Content": msg["Content"]}
            for msg in data.get("Message", [])
            if msg.get("Content")
        ]
    except requests.exceptions.HTTPError as e:
        print(f"LTA API HTTP error: {e.response.status_code}")
        return []
    except Exception as e:
        print(f"LTA API error: {e}")
        return []


def get_bridge_alerts() -> list[dict]:
    if not BRIDGE_URL:
        return []
    try:
        res = requests.get(BRIDGE_URL, timeout=30)
        res.raise_for_status()
        messages = res.json().get("value", {}).get("Message", [])
        if not isinstance(messages, list):
            print("Bridge returned unexpected Message format")
            return []
        return messages
    except requests.exceptions.HTTPError as e:
        print(f"Bridge HTTP error: {e.response.status_code}")
        return []
    except Exception as e:
        print(f"Bridge error: {e}")
        return []


def merge_alerts(lta_alerts: list[dict], bridge_alerts: list[dict]) -> list[dict]:
    """Merge alerts from both sources, deduplicating by line name."""
    seen_lines: set[str] = set()
    merged = []
    for alert in lta_alerts + bridge_alerts:
        line = alert.get("Line", "MRT")
        if line not in seen_lines and alert.get("Content"):
            seen_lines.add(line)
            merged.append(alert)
    return merged


def compute_hash(alerts: list[dict]) -> str:
    pairs = sorted((a.get("Line", ""), a.get("Content", "")) for a in alerts)
    return hashlib.sha256(json.dumps(pairs).encode()).hexdigest()


def load_cached_hash() -> str:
    try:
        with open(CACHE_FILE) as f:
            return f.read().strip()
    except OSError:
        return ""


def save_hash(hash_val: str) -> None:
    # Atomic write: write to a temp file then rename to avoid partial writes on crash.
    cache_dir = os.path.dirname(os.path.abspath(CACHE_FILE))
    try:
        with tempfile.NamedTemporaryFile("w", dir=cache_dir, delete=False, suffix=".tmp") as f:
            f.write(hash_val)
            tmp_path = f.name
        os.replace(tmp_path, CACHE_FILE)
    except OSError as e:
        print(f"Failed to save alert cache: {e}")


def load_last_daily_date() -> str:
    try:
        with open(DAILY_CACHE_FILE) as f:
            return f.read().strip()
    except OSError:
        return ""


def save_daily_date(date_str: str) -> None:
    cache_dir = os.path.dirname(os.path.abspath(DAILY_CACHE_FILE))
    try:
        with tempfile.NamedTemporaryFile("w", dir=cache_dir, delete=False, suffix=".tmp") as f:
            f.write(date_str)
            tmp_path = f.name
        os.replace(tmp_path, DAILY_CACHE_FILE)
    except OSError as e:
        print(f"Failed to save daily cache: {e}")


def format_alert_message(alerts: list[dict], sg_time_str: str) -> str:
    details = "".join(
        f"*{escape_markdown(a.get('Line', 'MRT'))}*: {escape_markdown(a.get('Content', ''))}\n"
        for a in alerts
    )
    return f"⚠️ *NEW TRAIN NOTICE*\n\n{details}\n🕒 _Last Updated: {sg_time_str}_"


def check_mrt_status() -> None:
    now_sg = datetime.now(timezone.utc) + timedelta(hours=8)
    sg_time_str = now_sg.strftime("%I:%M %p")

    print(f"--- RUNNING AT {sg_time_str} SGT ---")

    lta_alerts = get_lta_alerts()
    bridge_alerts = get_bridge_alerts()

    print(f"LTA alerts: {len(lta_alerts)}, Bridge alerts: {len(bridge_alerts)}")

    if lta_alerts or bridge_alerts:
        current_lta_hash = compute_hash(lta_alerts)
        # Bridge handles its own deduplication; only suppress LTA alerts if unchanged.
        new_lta_alerts = lta_alerts if current_lta_hash != load_cached_hash() else []
        new_alerts = merge_alerts(new_lta_alerts, bridge_alerts)

        if new_alerts:
            send_telegram(format_alert_message(new_alerts, sg_time_str))
            save_hash(current_lta_hash)
            print("🚨 New disruption detected and sent.")
        else:
            print("Same disruption as last check. Staying silent.")
        return

    # No active alerts — reset hash so the next disruption fires as new.
    save_hash("")

    today_str = now_sg.strftime("%Y-%m-%d")
    if now_sg.hour == 7 and today_str != load_last_daily_date():
        send_telegram(f"☀️ *DAILY MRT STATUS*\n\nAll lines normal.\n\n🕒 _Checked at {sg_time_str}_")
        save_daily_date(today_str)
        print("☀️ Daily 7AM summary sent.")
    else:
        print("No alerts detected and not the 7AM window. Staying silent.")


if __name__ == "__main__":
    validate_env()
    check_mrt_status()
