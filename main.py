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
    print("CCC")
    client = tweepy.Client(access_token)
    print("DDD")
    client.create_tweet(text="this is test post")

'''
    # 認証トークンを取得
    print(request)
    oauth_token = request.args.get('oauth_token',default=' ',type=str)
    oauth_verifier = request.args.get('oauth_verifier',default=' ',type=str)
    #URLから oauth_token を取り出して、auth.request_token[‘oauth_token’] にセット
    auth.request_token['oauth_token'] = oauth_token
    #URLから、oauth_verifierを取り出して、oauth_token_secretにセット
    auth.request_token['oauth_token_secret'] = oauth_verifier
    #ここの処理は調べきれてません
    auth.get_access_token(oauth_verifier)
    #アクセストークンと、アクセルトークンシークレットをセット（通常のtweepyでツイートする処理と同様）
    auth.set_access_token(auth.access_token,auth.access_token_secret)
    api = tweepy.API(auth)
    api.update_status("テスト")

    print("End")
    return {"message": "Tweet posted successfully!"}
'''

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)

'''
# GETメソッドでルートURLにアクセスされたときの処理
#@app.get("/")
#async def root():
    # Twitter APIの認証
#    auth = tweepy.OAuthHandler("pQyY2hN379B5zNRKKmT6lfPOW", "7pZCSypQL6XvZ86PIDt9P0KM3x01Qh26Z2yvojCzDtQH9y6DZf")
#    auth.set_access_token("1826294471832809472-dq3DLNHPqZlYNrM15FyMeP9TyQCvTf", "Vrsz3N3fYGiTGjdvpRegE1lDkz5gJAzeUuwVhu3MVr0kp")
#    api = tweepy.API(auth)

    

    #パラメータ名を省略したい場合
    #client = tweepy.Client(None, ck, cs, at, ats)

    pagenum = random.randint(24, 79)
    rank, surname, population, origin, surname_url = get_surname_data(pagenum)
    client.create_tweet(text=f"苗字：{surname}\n順位：{rank}\n人口:{population}\n由来:{origin}\nURL:{surname_url}")

def get_surname_data(pagenum):
    #pagenum = 24

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
    # n2に最大値を代入する
    #n2 = 1
    #while True:
    #    selector = f"#content > div.post > table:nth-child({random_table_num}) > tbody > tr:nth-child({n2}) > td:nth-child(1)"
    #    element = soup.select_one(selector)
    #    print(element)
    #    if element is None:
    #        break
        
    #    n2 += 1
    while True:
    # 1～n2の範囲内でランダムな整数を生成
        random_row_num = random.randint(1, 500)
        selector = f"#content > div.post > table:nth-child({random_table_num}) > tbody > tr:nth-child({random_row_num}) > td:nth-child(1)"
        element = soup.select_one(selector)
        if element is not None:
            break
    #デバッグ用
    #random_table_num = 22
    #print(random_table_num)
    #デバッグ用
    #random_row_num = 114
    #print(random_row_num)
    
    # 各データを取得
    rank_selector = f"#content > div.post > table:nth-child({random_table_num}) > tbody > tr:nth-child({random_row_num}) > td:nth-child(1)"
    rank = soup.select_one(rank_selector).get_text(strip=True)
    
    surname_selector = f"#content > div.post > table:nth-child({random_table_num}) > tbody > tr:nth-child({random_row_num}) > td:nth-child(2)"
    surname = soup.select_one(surname_selector).get_text(strip=True)
    
    population_selector = f"#content > div.post > table:nth-child({random_table_num}) > tbody > tr:nth-child({random_row_num}) > td:nth-child(3)"
    population = soup.select_one(population_selector).get_text(strip=True)
    
    # 結果を出力
    print(f"ランク: {rank}")
    print(f"苗字: {surname}")
    print(f"人口: {population}")


    #苗字ページに飛んで、由来を取得
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
    print(f"由来: {origin}")
    print(f"URL: {surname_url}")

    return rank, surname, population, origin, surname_url
'''