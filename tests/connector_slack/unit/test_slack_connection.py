from unittest.mock import patch, MagicMock

from src.connector_slack.commands.post_message import PostMessage


def test_successful_post():
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
        assert response['status'] == 200
        assert response['mimetype'] == "application/json"
        assert response['response'] == success_response


def test_connection_error():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 404
        poster = PostMessage('xxx', 'my_channel', 'hello world!')
        response = poster.execute({}, {})
        assert response['status'] == 404
        assert response['mimetype'] == "application/json"
        assert response['response'] == {"error": "Unreadable (non JSON) response from Slack"}


def test_error_from_slack():
    example_error = {'ok': False, 'error': 'invalid_arguments', 'warning': 'missing_charset',
                     'response_metadata': {'messages': ['[ERROR] missing required field: channel'],
                                           'warnings': ['missing_charset']}}
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.headers = {"Content-Type": 'application/json; charset=utf-8'}
        mock_post.return_value.json = MagicMock(return_value=example_error)
        poster = PostMessage('xxx', 'my_channel', 'hello world!')
        response = poster.execute({}, {})
        assert response['status'] == 400
        assert response['mimetype'] == "application/json"
        assert response['response'] == {'error': '[ERROR] missing required field: channel'}
