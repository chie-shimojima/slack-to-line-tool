# Slack to LINE 通知ツール

## 概要
Slackチャンネルのメッセージを取得し、要約してLINEに送信するツールです。  
重要な情報をLINEで受け取り、Slackの見逃し防止に役立つプロトタイプとして作成しました。

## 使用技術
- Python
- Slack API
- LINE Messaging API
- requests
- python-dotenv

## 主な機能
- Slackチャンネルのメッセージ取得
- 新着メッセージの抽出
- メッセージの簡易要約
- LINEへの通知送信

## ファイル構成
- `app.py` : メイン処理
- `requirements.txt` : 必要ライブラリ
- `.env.example` : 環境変数の記入例

## 実行方法
```bash
pip install -r requirements.txt
python app.py
