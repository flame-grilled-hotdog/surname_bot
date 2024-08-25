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

#情報取得関数
def get_surname_data(pagenum):

    # WebページのURLを指定
    ranking_url = f"https://myoji-yurai.net/prefectureRanking.htm?prefecture=%E5%85%A8%E5%9B%BD&page={pagenum}"
    response = requests.get(ranking_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 「人数」が含まれるテキストを持つテーブルのインデックスを探す
    table_list = []
    for i in range(50):
        selector = f"#content > div.post > table:nth-child({i}) > thead > tr > th:nth-child(1)"
        element = soup.select_one(selector)
        if element is None:
            continue
        if "順位" in element.get_text():
            table_list.append(i)
        
        i += 1
    # table_listの要素数の範囲内でランダムな整数を生成
    random_table_num = random.choice(table_list)

    while True:
    # 1～n2の範囲内でランダムな整数を生成
        random_row_num = random.randint(1, 500)
        selector = f"#content > div.post > table:nth-child({random_table_num}) > tbody > tr:nth-child({random_row_num}) > td:nth-child(1)"
        element = soup.select_one(selector)
        if element is not None:
            break
    
    # 各データを取得
    rank_selector = f"#content > div.post > table:nth-child({random_table_num}) > tbody > tr:nth-child({random_row_num}) > td:nth-child(1)"
    rank = soup.select_one(rank_selector).get_text(strip=True)
    
    surname_selector = f"#content > div.post > table:nth-child({random_table_num}) > tbody > tr:nth-child({random_row_num}) > td:nth-child(2)"
    surname = soup.select_one(surname_selector).get_text(strip=True)
    
    population_selector = f"#content > div.post > table:nth-child({random_table_num}) > tbody > tr:nth-child({random_row_num}) > td:nth-child(3)"
    population = soup.select_one(population_selector).get_text(strip=True)


    #苗字ページに飛んで、由来・読み方を取得
    surname_url = f"https://myoji-yurai.net/searchResult.htm?myojiKanji={surname}"
    response = requests.get(surname_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    n3 = 1
    for i in range(50):
        selector = f"#content > div:nth-child({i}) > div.box > h4"
        element = soup.select_one(selector)
        if element is None:
            continue
        if '由来解説' in element.get_text():
            n3 = i
            break
        i += 1

    origin_selector = f"#content > div:nth-child({n3}) > div.box > div"
    origin = soup.select_one(origin_selector).get_text(strip=True)
    del_str = 'この名字について情報をお持ちの方は「みんなの名字の由来」に投稿いただくか(※無料会員登録が必要です)、「名字の情報を送る」よりお寄せください。'
    origin = origin.replace(del_str,'')

    n4 = 1
    for i in range(15):
        selector = f"#content > div:nth-child({i}) > p"
        element = soup.select_one(selector)
        if element is None:
            continue
        if '読み' in element.get_text():
            n4 = i
            break
        i += 1

    reading_selector = f"#content > div:nth-child({n4}) > p"
    reading = soup.select_one(reading_selector).get_text(strip=True)
    del_str = '【読み】'
    reading = reading.replace(del_str,'')

    return rank, surname, reading, population, origin, surname_url

# 定期ツイート関数
def tweet_scheduled_message():
    print("ddddd")
    global client
    print("eeeee")
    if client is None:
        print("Twitterクライアントが初期化されていません。")
        return
    print("fffff")
    pagenum = random.randint(24, 79)
    rank, surname, reading, population, origin, surname_url = get_surname_data(pagenum)
    try:
        message = f"ランク: {rank}\n苗字: {surname}（{reading}）\n人口: {population}\n由来: {origin}\nURL: {surname_url}\n"
        print("ggggg")
        client.create_tweet(text=message)
        print("hhhhh")
        print("ツイートが送信されました！")
    except Exception as e:
        print(f"ツイートエラー: {e}")

# APSchedulerのスケジューラー設定
scheduler = BackgroundScheduler()

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
    global client
    client = tweepy.Client(bearer_token=access_token,consumer_key=API_KEY,consumer_secret=API_SECRET,access_token=ACCESS_TOKEN,access_token_secret=ACCESS_TOKEN_SECRET)
    print("Twitterクライアントが初期化されました。")
    # スケジューラーにジョブを追加（60分ごとに実行）
    print("aaaaa")
    scheduler.add_job(tweet_scheduled_message, 'interval', minutes=5)
    print("bbbbb")
    scheduler.start()
    print("ccccc")

    return {"message": "Twitter認証が完了しました。自動ツイートが開始されます。"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
