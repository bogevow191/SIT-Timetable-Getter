import requests
import os

def send_telegram_message(bot_token, chat_id, message):
    """
    Send a text message via Telegram bot
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Message sent successfully!")
            return True
        else:
            print(f"Failed to send message: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def send_telegram_csv(bot_token, chat_id, csv_file_path):
    """
    Send a CSV file via Telegram bot
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    try:
        with open(csv_file_path, 'rb') as file:
            files = {'document': file}
            data = {'chat_id': chat_id}
            
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                print("CSV file sent successfully!")
                return True
            else:
                print(f"Failed to send CSV: {response.text}")
                return False
    except Exception as e:
        print(f"Error sending CSV: {e}")
        return False

def send_telegram_photo(bot_token, chat_id, photo_path, caption=""):
    """
    Send a photo via Telegram bot
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                print("Photo sent successfully!")
                return True
            else:
                print(f"Failed to send photo: {response.text}")
                return False
    except Exception as e:
        print(f"Error sending photo: {e}")
        return False