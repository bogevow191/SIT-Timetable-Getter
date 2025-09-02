# SIT Timetable to Telegram

This Python script retrieves your weekly timetable from the (SIT) student portal and sends it to a designated Telegram chat. It also provides an image of the weekly schedule once a week for your convenience.

### Features
* **Daily Timetable Update:** Fetches and sends the next working day's timetable to a Telegram chat.
* **Weekly Timetable Export:** Generates an image of the weekly timetable on sunday and sends it to a Telegram chat once a week.

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
    git clone https://github.com/bogevow191/SIT-Timetable-Getter.git
    cd SIT-Timetable-Getter
    ```

2.  **Install the required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```
    ```
    playwright install
    ```
    *(Note: The script uses `Playwright`)

3.  **Set up the Telegram bot:**
    * Create a new bot using BotFather in Telegram.
    * Get the bot api token.
    * Add the bot to your channel or group.
    * Make sure the bot is an administrator in the channel/group.
    * Get the channel or group id. (you can get it by simply selecting the group/channel on web.telegram.org https://web.telegram.org/a/#<CHATID>)

4.  **Configure environment variables or a configuration file:**
    You will need to set up the following credentials and details in `main.py`. It's recommended to use a `.env` file following the `.env.example` template to manage these securely.
    * `USERNAME`: Your SIT student email address.
    * `PASSWORD`: Your SIT student portal password.
    * `TELEGRAM_BOT_TOKEN`: The API token from your Telegram bot.
    * `TELEGRAM_CHANNEL_ID`: The ID of the Telegram channel or group.

5.   **(Optional) Configure cron job:**
    * Set up a cron job to run the script daily at a specific time.
    * Edit your crontab file using `crontab -e` and add a line like:
      ```
      0 20 * * 0,1,2,3,4 /usr/bin/python3 /path/to/script/main.py
      ```
      This example runs the script every day at 8:00 PM, on Monday, Tuesday, Wednesday, Thursday and Sunday. (when the day is sunday, it will also send a image of the weekly timetable)
---

### Usage
Run the script from your terminal:
```bash
python main.py
```

Disclaimer
This script is intended for personal use and convenience. It is not affiliated with or endorsed by the Singapore Institute of Technology. Use this tool at your own risk. The developer is not responsible for any misuse, account issues, or potential violations of university policies.
