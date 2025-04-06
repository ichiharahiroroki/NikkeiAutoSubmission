from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import os
from dotenv import load_dotenv

load_dotenv()

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
    
    # ※正しいメールアドレスとパスワードに置き換えてください
    email_input.send_keys(os.getenv("EMAIL"))
    password_input.send_keys(os.getenv("PASSWORD"))

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
        
        # 7. ランキングテーブルからデータを取得し、CSVファイルに保存する
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
    else:
        print("ログイン失敗")
finally:
    # ドライバーを終了
    driver.quit()