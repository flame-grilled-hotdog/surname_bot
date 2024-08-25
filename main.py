import requests
from bs4 import BeautifulSoup
import tweepy
import random
import schedule
import time
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import tweepy
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler

# FastAPIのインスタンス作成
app = FastAPI()

# Twitter APIの認証情報
API_KEY = "Th1eN6F2u0amik9SAoxGH8KP9"
API_SECRET = "E45UQI6kX07FTghvnLs6eUPAjHVMzb5MEjqcX9gWJy4tZ1aZD4"
CALLBACK_URL = "https://surname-bot.onrender.com/callback"  # Redirect URL
ACCESS_TOKEN = "1826294471832809472-pDDHTSHoxnYGLAfDhKFYJL9ch8i8uH"
ACCESS_TOKEN_SECRET = "Pa6TIxdGdK59F2aonhb1LZe79F2O5ZibOVAHSnuLyM6yk"
CLIENT_ID = "TnJ3aldrWHBLT1VkTVBTNm9TUXc6MTpjaQ"
CLIENT_SECRET = "bLfu_Mf8Lnq7iUc5Vzk-DvdnlLCel6km3HoyTfqxaAg6Bqh7C5"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAIHzvQEAAAAAg6gQiT61eMYsW1hsrkmMy4ee%2BaA%3DKvDOk2Eawyyjlly0k2eJ25JUZKdUIpWiXZO9JIoCZvOOTwFQD6"

# グローバル変数でTwitterクライアントを保持
client = None

# 定期ツイート関数
def tweet_scheduled_message():
    print("ddddd")
    global client
    print("eeeee")
    if client is None:
        print("Twitterクライアントが初期化されていません。")
        return
    print("fffff")
    try:
        message = "これは定期的に送信される自動ツイートです！"
        print("ggggg")
        client.create_tweet(text=message)
        print("hhhhh")
        print("ツイートが送信されました！")
    except Exception as e:
        print(f"ツイートエラー: {e}")

# APSchedulerのスケジューラー設定
scheduler = BlockingScheduler()

# Tweepyを初期化
oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id=CLIENT_ID,
    redirect_uri=CALLBACK_URL,
    scope=["tweet.read", "tweet.write"],
    # Client Secret is only necessary if using a confidential client
    client_secret=CLIENT_SECRET
)

# GETメソッドでルートURLにアクセスされたときの処理
@app.get("/")
async def home():
    print("0000")

    # 認証URLを取得
    redirect_url = oauth2_user_handler.get_authorization_url()
    print(redirect_url)
    print("BBB")
    return RedirectResponse(redirect_url)


@app.get("/callback")
async def callback(request: Request):
    print("A")
    full_url = str(request.url)
    print("B")
    # 認証コードを取得
    print("REQUEST DEBUG START")
    print(full_url)
    print("REQUEST DEBUG END")
    access_token = oauth2_user_handler.fetch_token(full_url)
    print(access_token)
    access_token = access_token['access_token']
    print(access_token)
    client = tweepy.Client(bearer_token=access_token,consumer_key=API_KEY,consumer_secret=API_SECRET,access_token=ACCESS_TOKEN,access_token_secret=ACCESS_TOKEN_SECRET)
    print("Twitterクライアントが初期化されました。")
    # スケジューラーにジョブを追加（60分ごとに実行）
    print("aaaaa")
    scheduler.add_job(tweet_scheduled_message, 'interval', minutes=1)
    print("bbbbb")
    scheduler.start()
    print("ccccc")

    return {"message": "Twitter認証が完了しました。自動ツイートが開始されます。"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
