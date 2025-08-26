# SIT Timetable to Telegram

This Python script retrieves your weekly timetable from the (SIT) student portal and sends it to a designated Telegram chat. It also provides a CSV file of the weekly schedule for your convenience.

### Features
* **Daily Timetable Update:** Fetches and sends the next working day's timetable to a Telegram chat.
* **Weekly CSV Export:** Generates a CSV file (`weekly_schedule_timetable.csv`) containing the full weekly schedule.

---

### Prerequisites
* A **SIT student account** for accessing the timetable.
* A **Telegram Bot Token** from BotFather.
* A **Telegram Channel or Group** where the bot will send messages.
* The bot must be an **administrator** in the designated Telegram channel/group to send messages.

---

### Setup and Configuration
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/bogevow191/Timetable-Getter.git
    cd Timetable-Getter
    ```

2.  **Install the required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```
    ```
    playwright install
    ```
    *(Note: The script uses `Playwright`)

3.  **Configure environment variables or a configuration file:**
    You will need to set up the following credentials and details in `main.py`. It's recommended to use a `.env` file to manage these securely.
    * `USERNAME`: Your SIT student email address.
    * `PASSWORD`: Your SIT student portal password.
    * `TELEGRAM_BOT_TOKEN`: The API token from your Telegram bot.
    * `TELEGRAM_CHANNEL_ID`: The ID of the Telegram channel or group.

---

### Usage
Run the script from your terminal:
```bash
python main.py
```

Disclaimer
This script is intended for personal use and convenience. It is not affiliated with or endorsed by the Singapore Institute of Technology. Use this tool at your own risk. The developer is not responsible for any misuse, account issues, or potential violations of university policies.
