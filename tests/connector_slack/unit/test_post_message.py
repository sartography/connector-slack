import json
from unittest.mock import MagicMock
from unittest.mock import patch

from connector_slack.commands.post_message import PostMessage


class TestPostMessage:
    def test_successful_post(self) -> None:
        success_response = {
            "ok": True,
            "channel": "C123456",
            "ts": "1503435956.000247",
            "message": {
                "text": "Here's a message for you",
                "username": "ecto1",
                "bot_id": "B123456",
                "attachments": [
                    {
                        "text": "This is an attachment",
                        "id": 1,
                        "fallback": "This is an attachment's fallback"
                    }
                ],
                "type": "message",
                "subtype": "bot_message",
                "ts": "1503435956.000247"
            }
        }
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.headers = {"Content-Type": 'application/json; charset=utf-8'}
            mock_post.return_value.json = MagicMock(return_value=success_response)
            poster = PostMessage('xxx', 'my_channel', 'hello world!')
            response = poster.execute({}, {})
            assert response['command_response'] == {
                "body": json.dumps(success_response),
                "mimetype": "application/json",
                "http_status": 200
            }


    def test_connection_error(self) -> None:
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 404
            poster = PostMessage('xxx', 'my_channel', 'hello world!')
            response = poster.execute({}, {})
            assert response['command_response'] == {
                "body": '{}',
                "mimetype": "application/json",
                "http_status": 404
            }
            assert response["error"] is not None
            assert "error_code" in response["error"]
            assert response["error"]["error_code"] == "SlackMessageFailed"
            assert response["error"]["message"] == "Unreadable (non JSON) response from Slack"

    def test_error_from_slack(self) -> None:
        example_error = {'ok': False, 'error': 'invalid_arguments', 'warning': 'missing_charset',
                        'response_metadata': {'messages': ['[ERROR] missing required field: channel'],
                                            'warnings': ['missing_charset']}}
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.headers = {"Content-Type": 'application/json; charset=utf-8'}
            mock_post.return_value.json = MagicMock(return_value=example_error)
            poster = PostMessage('xxx', 'my_channel', 'hello world!')
            response = poster.execute({}, {})
            assert response['command_response'] == {
                "body": '{}',
                "mimetype": "application/json",
                "http_status": 400
            }
            assert response["error"] is not None
            assert "error_code" in response["error"]
            assert response["error"]["error_code"] == "SlackMessageFailed"
            assert response["error"]["message"] == "[ERROR] missing required field: channel"
