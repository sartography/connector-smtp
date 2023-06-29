import json

from email.message import EmailMessage
from smtplib import SMTP

class SendEmail:
    def __init__(self,
        smtp_host: str,
        smtp_port: int,
        email_subject: str,
        email_body: str,
        email_to: str,
        email_from: str,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.email_subject = email_subject
        self.email_body = email_body
        self.email_to = email_to
        self.email_from = email_from

    def execute(self, config, task_data):
        message = EmailMessage()
        message.set_content(self.email_body)
        message["Subject"] = self.email_subject
        message["From"] = self.email_from
        message["To"] = self.email_to

        response = {}

        try:
            with SMTP(self.smtp_host, self.smtp_port) as smtp:
                smtp.send_message(message)
        except Exception as e:
            response["error"] = str(e)

        return {
            "response": json.dumps(response),
            "status": 200,
            "mimetype": "application/json",
        }
        
