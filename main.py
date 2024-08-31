import os
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
from apscheduler.triggers.cron import CronTrigger
import urllib.parse
from dotenv import load_dotenv
import datetime
import unicodedata
import csv

# FastAPIのインスタンス作成
app = FastAPI()

# Twitter APIの認証情報
load_dotenv('.env')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
CALLBACK_URL = os.getenv('CALLBACK_URL')  # Redirect URL
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

# グローバル変数でTwitterクライアントを保持
client = None

##### 名字データ取得関数（通常） #####
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
    # 1～500の範囲内でランダムな整数を生成
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

    encoded_name = urllib.parse.quote(surname)
    surname_url_encode = f"https://myoji-yurai.net/searchResult.htm?myojiKanji={encoded_name}"

    reading_selector = f"#content > div:nth-child({n4}) > p"
    reading = soup.select_one(reading_selector).get_text(strip=True)
    del_str = '【読み】'
    reading = reading.replace(del_str,'')

    # 各項目を整形
    rank = f"【ランク】{rank}"
    surname = f"【苗字】{surname}（{reading}）"
    population = f"【人口】{population}"
    origin = f"【由来】{origin}"
    surname_url_encode = f"{surname_url_encode}" 

    #文字数チェック
    lencheckitem = [rank, surname, population, surname_url_encode]
    origin_strlen = 0
    except_origin_strlen = 0
    for i in range(4):
        except_origin_strlen += get_east_asian_width_count(lencheckitem[i])
        i += 1
    strlen = except_origin_strlen + get_east_asian_width_count(origin)
    print(strlen)
    if strlen > 280:
        print("文字数超過のため由来の文章を削ります。")

        #文字数調整
        max_length = 280 - except_origin_strlen
        truncated_text = truncate_text_to_length(origin, max_length)
        origin = truncated_text
    
    # 結果を出力
    print(rank)
    print(surname)
    print(population)
    print(origin)
    print(surname_url_encode)

    return rank, surname, population, origin, surname_url_encode

##### 名字データ取得関数（管理人厳選） #####
def get_selected_surname_data():

    ###CSVファイルを読み込み###
    csv_file = 'selected_surname_data.csv'
    selected_surname_list = []

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
    
        for row in reader:
            # 1行目のデータをリストに格納
            selected_surname_list.extend(row)

    ###苗字ページへアクセス###
    surname = random.choice(selected_surname_list)
    surname_url = f"https://myoji-yurai.net/searchResult.htm?myojiKanji={surname}"
    response = requests.get(surname_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    ###ランク・人口を取得###
    n2 = 1
    for i in range(20):
        selector = f"#content > div:nth-child({i}) > p"
        element = soup.select_one(selector)
        if element is None:
            continue
        if '【全国順位】' in element.get_text():
            n2 = i
            break
        i += 1

    rank_population_selector = f"#content > div:nth-child({n2}) > p"
    rank_population = soup.select_one(rank_population_selector).get_text(strip=True)

    rank = re.search(r'】\s*((\d{1,3}(,\d{3})*|\d+)位)', rank_population)
    rank = rank.group(1)
    del_str = ','
    rank = rank.replace(del_str,'')

    population = re.search(r'((およそ\d{1,3}(,\d{3})*|\d+)人)', rank_population)
    population = population.group(1)

    ###由来を取得###
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

    ###読み方を取得###
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

    ### URLを取得 ###
    encoded_name = urllib.parse.quote(surname)
    surname_url_encode = f"https://myoji-yurai.net/searchResult.htm?myojiKanji={encoded_name}"

    reading_selector = f"#content > div:nth-child({n4}) > p"
    reading = soup.select_one(reading_selector).get_text(strip=True)
    del_str = '【読み】'
    reading = reading.replace(del_str,'')

    ###ツイート用に各項目を整形###
    rank = f"★管理人厳選苗字\n【ランク】{rank}"
    surname = f"【苗字】{surname}（{reading}）"
    population = f"【人口】{population}"
    origin = f"【由来】{origin}"
    surname_url_encode = f"{surname_url_encode}" 

    #文字数チェック
    lencheckitem = [rank, surname, population, surname_url_encode]
    origin_strlen = 0
    except_origin_strlen = 0
    for i in range(4):
        except_origin_strlen += get_east_asian_width_count(lencheckitem[i])
        i += 1
    strlen = except_origin_strlen + get_east_asian_width_count(origin)
    print(strlen)
    if strlen > 280:
        print("文字数超過")

        #文字数調整
        max_length = 280 - except_origin_strlen
        truncated_text = truncate_text_to_length(origin, max_length)
        origin = truncated_text

    # 結果を出力
    print(rank)
    print(surname)
    print(population)
    print(origin)
    print(surname_url_encode)

    return rank, surname, reading, population, origin, surname_url_encode

# 文字数カウント関数
def get_east_asian_width_count(text):
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 2
        else:
            count += 1
    return count

# 文章短縮関数
def truncate_text_to_length(origin, max_length):
    # 句点「。」で文章を区切る
    sentences = origin.split('。')
    
    # 最後の要素が空なら削除（「。」で終わる場合の処理）
    if sentences[-1] == '':
        sentences.pop()
    
    # 文字数を確認しながら文章を削除
    while get_east_asian_width_count('。'.join(sentences)) > max_length:
        sentences.pop()  # 最後の文章を削除
    
    # 削った後の文章を再結合し、末尾に「。」を追加
    truncated_text = '。'.join(sentences) + '。'
    
    return truncated_text

# 定期ツイート関数
def tweet_scheduled_message():
    print("ツイート生成を開始します。")
    global client
    if client is None:
        print("Twitterクライアントが初期化されていません。")
        return
    # 現在の時間を取得
    current_time = datetime.datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute

    # XX時00分の投稿の場合、管理人厳選苗字をツイートする。
    if 20 <= current_minute <= 30:
        rank, surname, population, origin, surname_url_encode = get_selected_surname_data()
    else:
        pagenum = random.randint(24, 79)
        rank, surname, population, origin, surname_url_encode = get_surname_data(pagenum)

    try:
        message = f"{rank}\n{surname}\n{population}\n{origin}\n{surname_url_encode}"
        client.create_tweet(text=message)
        print("ツイートが送信されました！")
    except Exception as e:
        print(f"ツイートエラー: {e}")


# アクセストークン取得関数
def accesstoken_scheduled_fetch(full_url):
    print("アクセストークン取得を開始します。")
    access_token = oauth2_user_handler.fetch_token(full_url)
    print(access_token)
    access_token = access_token['access_token']
    print(access_token)
    global client
    client = tweepy.Client(bearer_token=access_token,consumer_key=API_KEY,consumer_secret=API_SECRET,access_token=ACCESS_TOKEN,access_token_secret=ACCESS_TOKEN_SECRET)
    print("Twitterクライアントが初期化されました。")

# APSchedulerのスケジューラー設定
tweet_scheduler = BackgroundScheduler()
accesstoken_fetch_scheduler = BackgroundScheduler()

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
    # 認証URLを取得
    redirect_url = oauth2_user_handler.get_authorization_url()
    print(redirect_url)
    return RedirectResponse(redirect_url)


@app.get("/callback")
async def callback(request: Request):
    full_url = str(request.url)
    accesstoken_scheduled_fetch(full_url)

    # スケジューラーにジョブを追加（ツイート：8-24時の間で20分ごとに実行　アクセストークン取得：100分ごとに取得）
    trigger = CronTrigger(minute='0,20,40', hour='23,0-14')
    tweet_scheduler.add_job(tweet_scheduled_message, trigger)
    tweet_scheduler.start()
    accesstoken_fetch_scheduler.add_job(accesstoken_scheduled_fetch, 'interval', minutes=100, args=[full_url])
    accesstoken_fetch_scheduler.start()
    print(datetime.datetime.now())

    return {"message": "Twitter認証が完了しました。自動ツイートが開始されます。"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
