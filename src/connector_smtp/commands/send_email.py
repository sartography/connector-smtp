from email.message import EmailMessage
from smtplib import SMTP
from typing import Any

from spiffworkflow_connector_command.command_interface import CommandErrorDict
from spiffworkflow_connector_command.command_interface import CommandResultDictV2
from spiffworkflow_connector_command.command_interface import ConnectorCommand
from spiffworkflow_connector_command.command_interface import ConnectorProxyResponseDict


class SendEmail(ConnectorCommand):
    def __init__(self,
        smtp_host: str,
        smtp_port: int,
        email_subject: str,
        email_body: str,
        email_to: str,
        email_from: str,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.email_subject = email_subject
        self.email_body = email_body
        self.email_to = email_to
        self.email_from = email_from

    def execute(self, _config: Any, _task_data: Any) -> CommandResultDictV2:
        message = EmailMessage()
        message.set_content(self.email_body)
        message["Subject"] = self.email_subject
        message["From"] = self.email_from
        message["To"] = self.email_to
        logs = []

        error: CommandErrorDict | None = None

        try:
            logs.append('will send')
            with SMTP(self.smtp_host, self.smtp_port) as smtp:
                if self.smtp_user and self.smtp_password:
                    logs.append('will login')
                    smtp.login(self.smtp_user, self.smtp_password)
                    logs.append('did login')
                smtp.send_message(message)
                logs.append('did send')
        except Exception as exception:
            logs.append(f'did error: {str(exception)}')
            error = {"error_code": exception.__class__.__name__, "message": str(exception)}

        return_response: ConnectorProxyResponseDict = {
            "command_response": {},
            "spiff__logs": logs,
            "error": error,
        }
        result: CommandResultDictV2 = {
            "response": return_response,
            "status": 200,
            "mimetype": "application/json",
        }

        return result
