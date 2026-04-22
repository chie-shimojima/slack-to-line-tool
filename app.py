import os
from datetime import datetime
from typing import List, Dict

import requests
from dotenv import load_dotenv


SLACK_HISTORY_URL = "https://slack.com/api/conversations.history"
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


def load_config() -> Dict[str, str]:
    """
    .env から設定値を読み込む。
    必須項目が不足している場合は分かりやすく例外を出す。
    """
    load_dotenv()

    config = {
        "slack_bot_token": os.getenv("SLACK_BOT_TOKEN", ""),
        "slack_channel_id": os.getenv("SLACK_CHANNEL_ID", ""),
        "slack_fetch_limit": os.getenv("SLACK_FETCH_LIMIT", "20"),
        "line_channel_access_token": os.getenv("LINE_CHANNEL_ACCESS_TOKEN", ""),
        "line_to_user_id": os.getenv("LINE_TO_USER_ID", ""),
    }

    required_keys = [
        "slack_bot_token",
        "slack_channel_id",
        "line_channel_access_token",
        "line_to_user_id",
    ]

    missing = [key for key in required_keys if not config[key]]
    if missing:
        raise ValueError(
            "環境変数が不足しています: "
            + ", ".join(missing)
            + "。.env を確認してください。"
        )

    return config


def fetch_slack_messages(
    slack_bot_token: str, slack_channel_id: str, limit: int
) -> List[Dict]:
    """
    Slack API から指定チャンネルの最新メッセージを取得する。
    """
    headers = {"Authorization": f"Bearer {slack_bot_token}"}
    params = {"channel": slack_channel_id, "limit": limit}

    response = requests.get(
        SLACK_HISTORY_URL,
        headers=headers,
        params=params,
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    if not data.get("ok"):
        error_message = data.get("error", "unknown_error")
        raise RuntimeError(f"Slack API エラー: {error_message}")

    messages = data.get("messages", [])

    # bot投稿やシステム投稿など text が空のものは除外
    text_messages = [msg for msg in messages if msg.get("text")]

    # 新しい順で返ってくるため、読みやすいように古い順に並べる
    text_messages.reverse()
    return text_messages


def build_simple_summary(messages: List[Dict], max_items: int = 5) -> str:
    """
    取得メッセージを簡易要約する。
    将来的に AI 要約へ差し替えやすいように関数を分けている。
    """
    if not messages:
        return "今日のSlackメッセージは見つかりませんでした。"

    lines = ["【Slack要約】"]

    for msg in messages[-max_items:]:
        text = msg.get("text", "").replace("\n", " ").strip()
        short_text = text[:100] + ("..." if len(text) > 100 else "")
        lines.append(f"・{short_text}")

    lines.append("")
    lines.append(f"取得時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "\n".join(lines)


def send_line_message(
    line_channel_access_token: str, line_to_user_id: str, summary_text: str
) -> None:
    """
    LINE Messaging API でプッシュ送信する。
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {line_channel_access_token}",
    }
    payload = {
        "to": line_to_user_id,
        "messages": [{"type": "text", "text": summary_text}],
    }

    response = requests.post(
        LINE_PUSH_URL,
        headers=headers,
        json=payload,
        timeout=20,
    )
    response.raise_for_status()


def main() -> None:
    """
    実行の入口。
    設定読み込み -> Slack取得 -> 要約 -> LINE送信 の順に実行する。
    """
    try:
        config = load_config()
        limit = int(config["slack_fetch_limit"])

        messages = fetch_slack_messages(
            slack_bot_token=config["slack_bot_token"],
            slack_channel_id=config["slack_channel_id"],
            limit=limit,
        )

        summary = build_simple_summary(messages)
        print("作成した要約:\n")
        print(summary)

        send_line_message(
            line_channel_access_token=config["line_channel_access_token"],
            line_to_user_id=config["line_to_user_id"],
            summary_text=summary,
        )
        print("\nLINE送信に成功しました。")

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
