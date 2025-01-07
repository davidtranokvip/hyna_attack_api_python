import yagmail
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.email = os.getenv('EMAIL_USERNAME')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.sender = {"Hyna": self.email}

        self.yag = yagmail.SMTP({ self.email: "Hyna" }, self.password)

    def send_email(self, to, subject, content):
        try:
            self.yag.send(to=to, subject=subject, contents=content)
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False