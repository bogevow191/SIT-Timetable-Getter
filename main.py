from timetableFinder import get_timetable
import datetime
import pandas as pd
import os
from telegram import send_telegram_csv, send_telegram_message
import platform

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Login credentials
USERNAME = ""  # Replace with actual username
PASSWORD = ""  # Replace with actual password

# Telegram credentials
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHANNEL_ID = ""

# start_date = datetime.date(2025, 8, 29)
start_date = datetime.datetime.now()
format_str = "%#d %b" if platform.system() == "Windows" else "%-d %b"
next_working_day_str = (start_date + datetime.timedelta(days=3 if start_date.weekday() == 4 else (2 if start_date.weekday() == 5 else (1 if start_date.weekday() == 6 else 1)))).strftime(format_str)

# # Or use with custom credentials and settings
df = get_timetable(
    username=USERNAME,
    password=PASSWORD,
    headless=True,  # Run in headless mode
    output_filename="my_timetable"
)
# df = pd.read_csv("weekly_schedule_timetable.csv")

lessons = []
for col in df.columns:
    if next_working_day_str in col:
        for row in df[col].dropna():
            # Check if row is not empty and contains the expected format
            if row and isinstance(row, str) and '|' in row:
                parts = row.split('|')
                # Ensure we have exactly 5 parts
                if len(parts) == 5:
                    modCode, modName, modType, modTime, modRoom = parts
                    lessons.append({
                        "modCode": modCode,
                        "modName": modName,
                        "modType": modType,
                        "modTime": modTime,
                        "modRoom": modRoom
                    })
                    print("-----------------")
                else:
                    print(f"Skipping row with unexpected format: {row}")
            else:
                print(f"Skipping empty or invalid row: {repr(row)}")
print(lessons)
message = """
Today's timetable:
"""
for lesson in lessons:
    message += f"""
{lesson["modCode"]}\n{lesson["modName"]}\n{lesson["modType"]}\n{lesson["modTime"]}\n{lesson["modRoom"]}\n
    """

send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, message)
send_telegram_csv(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, os.path.join(SCRIPT_DIR, "weekly_schedule_timetable.csv"))