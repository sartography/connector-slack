"""Send message to a slack channel."""
import json

import requests

class PostMessage:
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

    def execute(self, config, task_data):

        headers = {"Authorization": f"Bearer {self.token}",
                   "Content-type": "application/json"}
        body = {"channel": self.channel,
                "text": self.message
                }
        try:
            response = requests.post(self.SLACK_URL, headers=headers, json=body)
            if 'application/json' in response.headers.get('Content-Type', ''):
                response_json = response.json()
                if response_json['ok'] == True:
                    return {
                        "response": response.json(),
                        "status": response.status_code,
                        "mimetype": "application/json",
                    }
                else:
                    message = ". ".join(response_json.get('response_metadata',{}).get("messages", []))
                    if not message:
                        message = response_json['error']
                    status_code = response.status_code
                    if status_code == 200:
                        status_code = 400  # Don't return a 200 on a failure.
                    return {
                        "response": {"error": message},
                        "status": status_code,
                        "mimetype": "application/json",
                    }
            else:
                return {
                    "response": {"error": "Unreadable (non JSON) response from Slack"},
                    "status": response.status_code,
                    "mimetype": "application/json",
                }
        except Exception as e:
            return {
                "response": f'{"error": {e}}',
                "status": 500,
                "mimetype": "application/json",
            }

