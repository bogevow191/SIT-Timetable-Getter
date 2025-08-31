from timetableFinder import get_timetable
import datetime
import pandas as pd
import os
from telegram import send_telegram_csv, send_telegram_message, send_telegram_photo
from timetable_image_generator import create_simple_timetable_image
import platform
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load credentials from environment variables
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

# Validate that all required environment variables are set
if not all([USERNAME, PASSWORD, TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID]):
    print("Error: Missing required environment variables. Please check your .env file.")
    exit(1)

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

# Check if DataFrame was successfully retrieved
if df is None:
    print("Failed to retrieve timetable data. Exiting.")
    exit(1)

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
                    lesson = {
                        "modCode": modCode,
                        "modName": modName,
                        "modType": modType,
                        "modTime": modTime,
                        "modRoom": modRoom
                    }
                    # Check if this lesson is already in the list
                    if lesson not in lessons:
                        lessons.append(lesson)
                        print("-----------------")
                    else:
                        print(f"Duplicate lesson skipped: {modCode} - {modTime}")
                else:
                    print(f"Skipping row with unexpected format: {row}")
            else:
                print(f"Skipping empty or invalid row: {repr(row)}")

# Remove duplicates using a more robust method
unique_lessons = []
seen = set()
for lesson in lessons:
    lesson_id = f"{lesson['modCode']}|{lesson['modTime']}|{lesson['modRoom']}"
    if lesson_id not in seen:
        seen.add(lesson_id)
        unique_lessons.append(lesson)
    else:
        print(f"Removing duplicate: {lesson['modCode']} at {lesson['modTime']}")

lessons = unique_lessons
print(f"Final lessons count: {len(lessons)}")
print(lessons)

# Generate and send timetable image only if today is Sunday
if datetime.datetime.now().weekday() == 6:  # Sunday is 6 in Python's weekday()
    csv_path = os.path.join(SCRIPT_DIR, "weekly_schedule_timetable.csv")
    image_path = os.path.join(SCRIPT_DIR, "timetable_image.png")

    try:
        print("Generating timetable image...")
        create_simple_timetable_image(csv_path, image_path)
        print(f"Timetable image saved to: {image_path}")
        
        # Send image via Telegram
        print("Sending timetable image via Telegram...")
        send_telegram_photo(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, image_path, 
                           caption="📅 Weekly Timetable")
        print("Timetable image sent successfully!")
        
    except Exception as e:
        print(f"Error generating or sending timetable image: {e}")
else:
    print("Today is not Sunday. Skipping timetable image generation.")
    
message = """
Today's timetable:
"""
for lesson in lessons:
    message += f"""
{lesson["modCode"]}\n{lesson["modName"]}\n{lesson["modType"]}\n{lesson["modTime"]}\n{lesson["modRoom"]}\n
"""
    
send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, message)