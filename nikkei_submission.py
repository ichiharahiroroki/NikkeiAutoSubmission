from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

def login_and_nikkei_submission(email, password, predict_agerage_price=None, get_csv=False):
    """
    メールアドレスとパスワードを引数に取り、ログイン処理、ページ遷移、ランキングテーブルの取得、
    日経平均終値の取得および forecastVote への入力処理を実行する。
    """
    # ヘッドレスモードでFirefoxを起動するためのオプションを設定
    options = Options()
    options.headless = True

    # FirefoxのWebDriverを作成
    # ※ geckodriverがPATHに入っていない場合は、executable_pathにパスを指定してください
    driver = webdriver.Firefox(options=options)

    try:
        # 1. ログインページを開く
        login_url = os.getenv("LOGIN_URL")
        driver.get(login_url)
        time.sleep(2)  # ページが読み込まれるのを待つ

        # 2. ログインフォームの各要素を取得し、ログイン情報を入力
        email_input = driver.find_element(By.ID, "accountid")
        password_input = driver.find_element(By.ID, "password")
        
        # 関数の引数で渡されたメールアドレスとパスワードを入力
        email_input.send_keys(email)
        password_input.send_keys(password)

        # 3. ログインボタンは初期状態でdisabledになっているため、disabled属性を除去してクリック可能にする
        login_button = driver.find_element(By.ID, "login")
        driver.execute_script("arguments[0].removeAttribute('disabled');", login_button)
        
        # 4. ログインボタンをクリック
        login_button.click()
        time.sleep(2)  # ログイン後のページ遷移を待つ

        # 5. ログイン成功の判定（例として、ページ内に「ログアウト」が存在するか確認）
        page_source = driver.page_source
        if "ログアウト" in page_source:
            print("ログイン成功")
            
            # 6. id="forecast" の範囲内にあるリンク（href="/forecast.php"）をクリックしてページ遷移
            forecast_section = driver.find_element(By.ID, "forecast")
            forecast_link = forecast_section.find_element(By.XPATH, ".//a[@href='/forecast.php']")
            forecast_link.click()
            time.sleep(2)  # ページ遷移を待機
            
            # 7. CSVデータ取得（get_csv が True の場合のみ実行）
            if get_csv:
                import csv
                import datetime
                from bs4 import BeautifulSoup
                # 本日の日付を"YYYYMMDD"形式で取得
                today_str = datetime.datetime.now().strftime("%Y%m%d")
                filename = f"ranking_data_{today_str}.csv"

                # ページソースからBeautifulSoupオブジェクトを作成
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # クラス名 "ranking" の<table>を取得
                ranking_table = soup.find("table", class_="ranking")
                if ranking_table:
                    tbody = ranking_table.find("tbody")
                    rows = tbody.find_all("tr")
                    ranking_data = []
                    header = []
                    for row in rows:
                        # spacerクラスを持つ行が見つかったら、それ以降の行は無視する
                        if row.get('class') and 'spacer' in row.get('class'):
                            break
                        ths = row.find_all("th")
                        if ths:
                            header = [th.get_text(strip=True) for th in ths]
                        else:
                            tds = row.find_all("td")
                            if tds:
                                ranking_data.append([td.get_text(strip=True) for td in tds])
                    if header and ranking_data:
                        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(header)
                            writer.writerows(ranking_data)
                        print(f"ランキングデータを {filename} に保存しました。")
                    else:
                        print("ランキングテーブルのデータが見つかりませんでした。")
                else:
                    print("ランキングテーブルが見つかりませんでした。")
            
            # 8. 日経平均終値の取得と forecastVote の入力処理
            try:
                if predict_agerage_price is not None:
                    # ユーザーから与えられた値を使う（float型）
                    value = round(float(predict_agerage_price), 2)
                    yen_value = int(value)
                    sen_value = int(round((value - yen_value) * 100))
                else:
                    # "div.closingPrice" 内の "div.value" から終値を取得
                    closing_price_text = driver.find_element(By.CSS_SELECTOR, "div.closingPrice div.value").text
                    closing_price_clean = closing_price_text.replace(",", "")
                    parts = closing_price_clean.split(".")
                    if len(parts) == 2:
                        yen_value, sen_value = parts[0], parts[1]
                    else:
                        yen_value, sen_value = parts[0], "0"
                print(f"入力する日経平均終値: 円: {yen_value}, 銭: {sen_value}")
                
                # forecastVote セクション内の入力欄を取得し、値を入力する
                yen_input = driver.find_element(By.CSS_SELECTOR, "p.forecastVote input.yen")
                sen_input = driver.find_element(By.CSS_SELECTOR, "p.forecastVote input.sen")
                
                # すでに値が入力されているかチェック
                if yen_input.get_attribute("value") == "" and sen_input.get_attribute("value") == "":
                    yen_input.clear()
                    sen_input.clear()
                    yen_input.send_keys(str(yen_value))
                    sen_input.send_keys(str(sen_value))
                    
                    # 投票ボタンの押下処理
                    submit_button = driver.find_element(By.CSS_SELECTOR, "p.forecastVote input.submit")
                    submit_button.click()
                else:
                    print(f"フォームに既に値が入力されているため、投票処理はスキップします。: 円 {yen_value}, 銭: {sen_value}")
                
            except Exception as e:
                print(f"日経平均終値の取得または forecastVote への入力でエラーが発生しました: {e}")
        else:
            print(f"ログイン失敗: {email}")
    finally:
        # ドライバーを終了
        time.sleep(10)#テスト実行時だけ
        driver.quit()

if __name__ == '__main__':
    # 環境変数からログインURLなどは読み込んでいるので、メールアドレスとパスワードは
    # 環境変数か直接ここに記述してください。
    # 以下は環境変数から取得する例です。
    login_and_nikkei_submission(os.getenv("EMAIL"), os.getenv("PASSWORD"),predict_agerage_price=35000)