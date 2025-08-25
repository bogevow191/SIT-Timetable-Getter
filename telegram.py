import requests
import os

def send_telegram_message(token: str, chat_id: str, message: str) -> bool:
    """
    Sends a text message to a specified chat via the Telegram Bot API.

    Args:
        token: The unique authentication token for your Telegram bot.
        chat_id: The unique identifier for the target chat or channel.
        message: The text content to be sent.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML' # Optional: for formatting like <b>bold</b> or <i>italic</i>
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        print("Message sent successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")
        return False


def send_telegram_csv(token: str, chat_id: str, file_path: str) -> bool:
    """
    Sends a CSV file to a specified chat via the Telegram Bot API.

    Args:
        token: The unique authentication token for your Telegram bot.
        chat_id: The unique identifier for the target chat or channel.
        file_path: The full path to the CSV file to be sent.

    Returns:
        True if the file was sent successfully, False otherwise.
    """
    url = f"https://api.telegram.org/bot{token}/sendDocument"

    try:
        # Open the file in binary mode
        with open(file_path, 'rb') as f:
            # Prepare the payload for the file upload
            files = {'document': f}
            data = {'chat_id': chat_id}
            
            # Make the POST request
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        
        print(f"Successfully sent file: {os.path.basename(file_path)}")
        return True
        
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Failed to send file: {e}")
        return False