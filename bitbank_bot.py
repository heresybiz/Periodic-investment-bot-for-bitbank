import ccxt
from time import sleep
import json
import os
import sys

import time
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

import requests

bitbank = ccxt.bitbank({
"apiKey": os.environ["BITBANK_API_KEY"],
"secret": os.environ["BITBANK_SECRET"]
})

args = sys.argv

# --------------------------------
# 対象通貨情報取得
# --------------------------------
if args[1] == "BTC/JPY":

    index_assets = 1

elif args[1] == "BCH/JPY":

    index_assets = 6

elif args[1] == "XRP/JPY":

    index_assets = 3

elif args[1] == "MONA/JPY":

    index_assets = 5

else:

    index_assets = 99

# --------------------------------
# 相場情報取得
# --------------------------------
while( True ):

    try:

        # 対象通貨のTicker(相場情報)取得
        data = bitbank.fetch_ticker(symbol=(args[1]))

        # 対象通貨の現在価格に対して、「10,000」円分の購入数量を算出
        amount = 10000 / data["ask"]

        break

    except ccxt.BaseError as e:

        # 1時間待機し、再実行
        time.sleep(60 * 60)

# --------------------------------
# エントリー注文発行
# --------------------------------
try:

    # エントリー注文発行
    res = bitbank.create_order(symbol=(args[1]), type="market", side="buy", amount=str(amount), price=1)

    create_order_success = True

    str_order_datetime_utc = parse(res["datetime"]).strftime("%Y/%m/%d %H:%M:%S")

    order_datetime_utc = datetime.strptime(str_order_datetime_utc, "%Y/%m/%d %H:%M:%S") + relativedelta(hours=9)

except ccxt.BaseError as e:

    create_order_success = False

# --------------------------------
# 残高情報取得
# --------------------------------
try:

    # 残高取得
    balance = bitbank.fetch_balance()

    # 対象通貨の残高情報取得
    balance_target = balance["info"]["data"]["assets"][index_assets]

    # 対象通貨の通貨名取得
    balance_target_asset = balance_target["asset"]

    # 対象通貨の残高取得
    balance_target_onhand_amount = balance_target["onhand_amount"]

    get_balance_success = True

except ccxt.BaseError as e:

    get_balance_success = False

# --------------------------------
# LINE Notify定義
# --------------------------------
def lineNotify(message):

    line_notify_token = os.environ['LINE_NOTIFY_TOKEN']

    line_notify_api = 'https://notify-api.line.me/api/notify'

    payload = {'message': message}

    headers = {'Authorization': 'Bearer ' + line_notify_token}

    requests.post(line_notify_api, data=payload, headers=headers)

# --------------------------------
# LINE Notify通知メッセージ格納
# --------------------------------
# 注文が成功した場合
if create_order_success:

    # 注文成功通知を出す
    notify_message = "\n" \
                   + "注文に成功しました" \
                   + "\n"

    notify_message = notify_message \
                   + "注文日時: " \
                   + order_datetime_utc.strftime("%Y/%m/%d %H:%M:%S") \
                   + "\n" \
                   + "通貨ペア: " \
                   + res["symbol"].upper() \
                   + "\n" \
                   + "平均価格: " \
                   + str(data["ask"]) \
                   + "\n" \
                   + "枚数: " \
                   + str(res["amount"]) \
                   + "\n" \
                   + "ID: " \
                   + str(res["id"]) \
                   + "\n"

    if get_balance_success:

        notify_message = notify_message \
                       + "資産情報" \
                       + "\n"

        notify_message = notify_message \
                       + balance_target_asset.upper() \
                       + ": " \
                       + balance_target_onhand_amount

    else:

        notify_message = notify_message \
                       + "残高情報の取得に失敗しました"

# 注文が失敗した場合
else:

    # 注文失敗通知を出す
    notify_message = "\n" \
                   + "注文に失敗しました" \
                   + "\n"

    notify_message = notify_message \
                   + "注文しなおしてください" \
                   + "\n"

    if get_balance_success:

        notify_message = notify_message \
                       + "残高情報" \
                       + "\n"

        notify_message = notify_message \
                       + balance_target_asset.upper() \
                       + ": " \
                       + balance_target_onhand_amount

    else:

        notify_message = notify_message \
                       + "残高情報の取得に失敗しました"

# LINE Notify通知
lineNotify(notify_message)

# --------------------------------
# 次回購入予定日時取得
# --------------------------------
# today
today = datetime.today()

# today(utc)
today_utc = today + relativedelta(hours=9)

# end of month
end_month = today_utc + relativedelta(months=1) - timedelta(days=today_utc.day)

# next datetime
next_datetime = end_month + relativedelta(days=1, hour=9, minute=0, second=0, microsecond = 0)

# notify next datetime
notify_message = "\n" \
               + "次回の購入予定日時は" \
               + next_datetime.strftime("%Y/%m/%d %H:%M:%S") \
               + "です"

# LINE Notify通知
lineNotify(notify_message)
