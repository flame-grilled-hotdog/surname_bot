import requests
from bs4 import BeautifulSoup
import tweepy
import random
import schedule
import time

def main():
    pagenum = 24

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

    return surname, population, origin

if __name__ == "__main__":
    main()

# Twitter APIの認証
#auth = tweepy.OAuthHandler("API_KEY", "API_SECRET")
#auth.set_access_token("ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")
#api = tweepy.API(auth)

# ランダムな苗字をツイートする関数
#def tweet_surname():
#    rank = random.randint(5000, 10000)
#    surname, population, origin = get_surname_data(rank)
#    tweet = f"{rank}位: {surname}\n人口: {population}\n由来: {origin}"
#    api.update_status(tweet)

# 定期的にツイートするスケジュールを設定
#schedule.every().hours.do(main)

#while True:
#    schedule.run_pending()
#    time.sleep(1)
