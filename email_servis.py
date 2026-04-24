import smtplib
import aiohttp  
from email.message import EmailMessage


from dotenv import load_dotenv
import os

load_dotenv()

FROM_EMAIL = os.getenv("EMAIL_FROM")
FROM_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def send_welcome_email(to_email: str):
    message = EmailMessage()
    message['Subject'] = 'Welcome to our Blog Post API'
    message['From'] = FROM_EMAIL
    message['To'] = to_email
    message.set_content('Thank you for registering with our Blog Post API! We are excited to have you on board.')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(FROM_EMAIL, FROM_PASSWORD)
            smtp.send_message(message)
        print(f"Welcome email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send welcome email to {to_email}: {e}")  



async def send_telegram_message(chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with aiohttp.ClientSession() as session:
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    print(f"Telegram message sent to chat_id {chat_id}")
                else:
                    print(f"Failed to send Telegram message to chat_id {chat_id}: {response.status}")
        except Exception as e:
            print(f"Error sending Telegram message to chat_id {chat_id}: {e}")
