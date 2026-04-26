# 🚇 MRT Status Monitor Bot

An automated Telegram bot that monitors Singapore's Mass Rapid Transit (MRT) network for service disruptions and sends real-time alerts. Built entirely serverless using Python and GitHub Actions.

## ✨ Features

* **Real-Time Disruption Alerts:** Pings a designated Telegram chat immediately if a new fault, delay, or disruption is detected on any MRT line.
* **Daily Status Summaries:** Sends an automated "All Clear" summary every morning at 7:00 AM SGT to confirm the network is running normally before the morning commute.
* **Smart Polling:** Uses a custom Google Apps Script bridge to act as a memory state, ensuring the bot only sends alerts for *new* updates and prevents spamming.
* **Serverless Architecture:** Requires no active server hosting. The script is executed on a CRON schedule via GitHub Actions.

## 🛠️ Tech Stack

* **Language:** Python 3.9
* **Automation:** GitHub Actions (CI/CD & CRON Scheduling)
* **APIs:** Telegram Bot API
* **Backend/State Management:** Google Apps Script

## ⚙️ How It Works

1. **The Trigger:** A GitHub Action workflow (`monitor.yml`) wakes up the Python script every 5 minutes during peak hours (and every 15 minutes during off-peak).
2. **The Fetch:** The script hits a Google Apps Script endpoint, which parses the latest transit data.
3. **The Logic:** The Python script compares the current network status against the previous state. 
4. **The Alert:** If a new disruption is found, or if it is exactly 7:00 AM, a formatted Markdown payload is sent to the Telegram API to alert the user.

## 🔒 Security & Configuration

To maintain security, all sensitive keys and URLs are hidden using **GitHub Repository Secrets** and injected as Environment Variables during the workflow run.

Environment variables required to run this bot:
* `BOT_TOKEN`: The unique API token provided by BotFather.
* `CHAT_ID`: The target Telegram user or group ID.
* `BRIDGE_URL`: The endpoint URL for the Google Apps Script.

## 🚀 Future Improvements
* Add support for specific line tracking (e.g., only subscribe to East-West Line updates).
* Implement interactive Telegram commands (e.g., `/status`) using a webhook architecture.

---
*Created by Paarth*
