import time
import datetime
import asyncio
import holidays
from typing import Optional

from nikkei_submission import login_and_nikkei_submission

# お客様データイテレーターの定義
def generate_customer_data():
    """
    お客様データを順番に出力するジェネレーター関数。
    データは辞書リストとして管理され、各辞書は 'email' と 'password' キーを持ちます。
    """
    customers = [
        {"email": "ic.to.9h76szl5@gmail.com", "password": "Tomohiro8714"},
        {"email": "yo.ru.db9uwxqi@gmail.com", "password": "ohau5FRdtD43"},
        {"email": "yu.su.rctmu7wd@gmail.com", "passwprd":"HogeHoge1"}
        # 必要に応じてお客様データを追加してください
    ]
    for customer in customers:
        yield customer


def is_market_open(now: datetime.datetime) -> bool:
    """
    現在の日付が株式市場が開いている日（平日かつ祝日であり、さらに21時以降の場合）であれば True を返す。
    """
    jp_holidays = holidays.JP()
    return (now.weekday() < 5 and 
            now.date() not in jp_holidays and 
            now.hour >= 21)


async def run_monitor():
    """
    株式市場が開いている平日の夜9時になったかをチェックし、条件が成立したら他の処理を呼び出す（ここではprint()で代用）。
    """
    print("マーケット監視を開始します...")
    last_executed_date = None
    while True:
        now = datetime.datetime.now()
        if is_market_open(now) and last_executed_date != now.date():
            print("条件成立：株式市場が開いている日の21時以降です。実行します！")
            customers_iterator = generate_customer_data()
            for customer in customers_iterator:
                print(customer)
                login_and_nikkei_submission(customer["email"],customer["password"],get_csv=True)
            
            last_executed_date = now.date()
                
        # 15分毎にチェック（15分＝900秒）
        await asyncio.sleep(900)  # 15分待機に変更する場合はこちらを使用
        #await asyncio.sleep(5)  # テスト実行用に5秒待機



# テスト実行するためのコード
if __name__ == '__main__':
    asyncio.run(run_monitor())