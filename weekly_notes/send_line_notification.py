import os
import requests
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

LINE_TOKEN = os.getenv("LINE_TOKEN")


def send_line_message(msg):
    # APIエンドポイントのURL
    url = "https://notify-api.line.me/api/notify"
    # HTTPリクエストヘッダーの設定
    headers = {"Authorization": "Bearer " + LINE_TOKEN}
    # ペイロードの設定
    payload = {"message": msg}
    # POSTリクエストの使用
    r = requests.post(url, headers=headers, params=payload)
    if r.status_code == requests.codes.ok:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Status code: {r.status_code}")


def send_log_via_line(log_file_path: str):
    """ 実行結果のログファイルをLINEで送信 """
    with open(log_file_path, 'r') as f:
        log_content = f.read()
    message = f"Weekly Note Automation Log:\n\n{log_content}"
    send_line_message(message)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python send_line_notification.py <log_file_path>")
        sys.exit(1)

    log_file_path = sys.argv[1]

    # ログ内容をLINEで送信
    send_log_via_line(log_file_path)
