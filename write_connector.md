# Writing a Connector

Connectors are API endpoints that can easily be used within [SpiffArena](https://github.com/sartography/spiff-arena) to allow your workflows to communicate with external systems via `Service Tasks`.
In this tutorial we will walk through the steps required to create a new SMTP Connector, integrate it with a `Connector Proxy` and finally test within `SpiffArena`.
While the code will implement an SMTP Connector, the principles can be applied to create a Connector for other external systems.

## Anatomy of a Connector

Since we will be leveraging [SpiffWorkflow Proxy Blueprint](https://github.com/sartography/spiffworkflow-proxy), our Connector must respect the conventions that are used for discoverability and routing.
The convention comes in two parts - the directory/file structure on disk and the Connector class structure.

### Directory/File structure

A Connector project looks like:

```
src/connector_NAME:
total 8
drwxrwxr-x 3 jon jon 4096 Jun 29 15:26 commands
-rw-rw-r-- 1 jon jon    0 Jun 29 13:05 __init__.py

src/connector_NAME/commands:
total 12
-rw-rw-r-- 1 jon jon    0 Jun 29 13:47 __init__.py
-rw-rw-r-- 1 jon jon 1463 Jun 29 15:26 myCommand.py
```

Connectors can have multiple commands.
The `HTTP Connector` for example has `getRequest.py` and `postRequest.py`.

### Class structure

Each Connector command file contains a class structured like the following:

```
class MyCommand:
    def __init__(self,
        some_str_param: str,
        some_int_param: int,
        some_optional_str_param: Optional[str] = None,
    ):
        ...

    def execute(self, config, task_data):
        ...
	
        response = {"result": 42}

        return {
            "response": json.dumps(response),
            "status": 200,
            "mimetype": "application/json",
        }
```

The parameters defined in the constructor will be exposed in the diagram editor of SpiffArena.
The executre method will be called when a `Service Task` is executed within a running diagram.

## Creating the SMTP Connector

### Directory Setup

Our new SMTP Connector is going to start life with one `SendEmail` command.
In a new git repository initialize poetry and create the folder structures:

```
src/connector_smtp:
total 8
drwxrwxr-x 3 jon jon 4096 Jun 29 15:26 commands
-rw-rw-r-- 1 jon jon    0 Jun 29 13:05 __init__.py

src/connector_smtp/commands:
total 12
-rw-rw-r-- 1 jon jon    0 Jun 29 13:47 __init__.py
-rw-rw-r-- 1 jon jon 1463 Jun 29 15:26 sendEmail.py
```

Don't forget the `__init__.py` files or your Connector will not be discovered properly.
Your pyproject.toml file should look something like:

```
[tool.poetry]
name = "connector-smtp"
version = "0.1.0"
description = "Make SMTP Requests available to SpiffWorkflow Service Tasks"
authors = ["My Name <my.name@yahoo.com>"]
readme = "README.md"
packages = [{include = "connector_smtp", from = "src" }]

[tool.poetry.dependencies]
python = "^3.9"


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Implement the class

Our `SendEmail` Connector is going to start quite simple.
We will take all configuration parameters required to send the email from a running workflow.
This keeps the Connector stateless and greatly simplifies the code.

Our `SendEmail` Connector looks like:

```
import json

from email.message import EmailMessage
from smtplib import SMTP
from typing import Optional

class SendEmail:
    def __init__(self,
        smtp_host: str,
        smtp_port: int,
        email_subject: str,
        email_body: str,
        email_to: str,
        email_from: str,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
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
        should_login = self.smtp_user and self.smtp_password

        try:
            with SMTP(self.smtp_host, self.smtp_port) as smtp:
                if should_login:
                    smtp.login(self.smtp_user, self.smtp_password)
                smtp.send_message(message)
        except Exception as e:
            response["error"] = str(e)

        return {
            "response": json.dumps(response),
            "status": 200,
            "mimetype": "application/json",
        }
```

Any exception will be returned to the workflow along with a 200 response.
This allows the BPMN author the opportunity to inspect the result and take appropriate actions in their diagram.