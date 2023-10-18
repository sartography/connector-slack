"""Send message to a slack channel."""
import json
from typing import Any

import requests  # type: ignore
from spiffworkflow_connector_command.command_interface import CommandErrorDict
from spiffworkflow_connector_command.command_interface import CommandResponseDict
from spiffworkflow_connector_command.command_interface import ConnectorCommand
from spiffworkflow_connector_command.command_interface import ConnectorProxyResponseDict


class PostMessage(ConnectorCommand):
    """Send a message to slack."""

    SLACK_URL = "https://slack.com/api/chat.postMessage"

    def __init__(self, token: str, channel: str, message: str):
        """
        :param token: The authentication token to use.
        :param channel: The channel where the message should be posted.
        :param text: The content to post (should be markdown format)
        :return: Json Data structure containing a http status code (hopefully '200' for success..)
            and a response string.
        """
        self.token = token
        self.channel = channel
        self.message = message

    def execute(self, _config: Any, _task_data: Any) -> ConnectorProxyResponseDict:

        headers = {"Authorization": f"Bearer {self.token}",
                   "Content-type": "application/json"}
        body = {"channel": self.channel,
                "text": self.message
                }

        command_response = {}
        status = 0
        error: CommandErrorDict | None = None

        try:
            response = requests.post(self.SLACK_URL, headers=headers, json=body, timeout=3000)
            if 'application/json' in response.headers.get('Content-Type', ''):
                response_json = response.json()
                if response_json['ok'] is True:
                    command_response = response.json()
                    status = response.status_code
                else:
                    message = ". ".join(response_json.get('response_metadata',{}).get("messages", []))
                    if not message:
                        message = response_json['error']
                    status_code = response.status_code
                    if status_code == 200:
                        status_code = 400  # Don't return a 200 on a failure.
                    status = status_code
                    error = {"error_code": "SlackMessageFailed","message": message}
            else:
                error = {"error_code": "SlackMessageFailed", "message": "Unreadable (non JSON) response from Slack"}
                status = response.status_code
        except Exception as exception:
            error = {"error_code": exception.__class__.__name__, "message": str(exception)}
            status = 500

        return_response: CommandResponseDict = {
            "body": json.dumps(command_response),
            "mimetype": "application/json",
            "http_status": status,
        }
        result: ConnectorProxyResponseDict = {
            "command_response": return_response,
            "error": error,
            "command_response_version": 2,

        }

        return result
