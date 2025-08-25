# Timetable-Crawler

SIT Timetable Telegram Bot
This Python script retrieves your weekly timetable from the Singapore Institute of Technology (SIT) student portal and sends it to a designated Telegram chat. It also provides a CSV file of the weekly schedule for your convenience.

Features
Daily Timetable Update: Fetches and sends the next working day's timetable to a Telegram chat.

Weekly CSV Export: Generates a CSV file (timetable.csv) containing the full weekly schedule.

Prerequisites
A SIT student account for accessing the timetable.

A Telegram Bot Token from BotFather.

A Telegram Channel or Group where the bot will send messages.

The bot must be an administrator in the designated Telegram channel/group to send messages.

Setup and Configuration
Clone the repository:

Bash

git clone [your-repo-link]
cd [your-repo-name]
Install the required Python libraries:

Bash

pip install -r requirements.txt
Note: The script uses libraries like Selenium or Playwright for web scraping, and python-telegram-bot for Telegram integration.

Configure environment variables or a configuration file:
You will need to set up the following credentials and details. It's recommended to use a .env file to manage these securely.

SIT_USERNAME: Your SIT student email address.

SIT_PASSWORD: Your SIT student portal password.

TELEGRAM_BOT_TOKEN: The API token from your Telegram bot.

TELEGRAM_CHAT_ID: The ID of the Telegram channel or group.

Usage
Run the script from your terminal:

Bash

python main.py
Note: You can automate this script to run daily using a task scheduler like Cron on Linux or Task Scheduler on Windows.

Disclaimer
This script is intended for personal use and convenience. It is not affiliated with or endorsed by the Singapore Institute of Technology. Use this tool at your own risk. The developer is not responsible for any misuse, account issues, or potential violations of university policies.
