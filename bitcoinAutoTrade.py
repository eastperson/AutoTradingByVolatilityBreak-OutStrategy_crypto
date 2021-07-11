import time
import pyupbit
import datetime
import requests
import schedule
from fbprophet import Prophet

auth_token = ''

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)

access = ""
secret = ""

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    # 다음날 시가에 변동폭을 줘서 목표값을 설정한다.
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
predict_price("KRW-BTC")

def post_message_daily(ticker):
        target_price = get_target_price(ticker, k_value)
        # 15일 이동평균선 계산
        ma15 = get_ma15(ticker)
        # 현재 시가
        current_price = get_current_price(ticker)

        flag = ""

        post_message(auth_token,"#crypto", "-----------------------------------------------------------------")
        post_message(auth_token,"#crypto", "k 값 : " + str(k_value))
        post_message(auth_token,"#crypto", "현재 원화 잔액 : " + str(upbit.get_balance("KRW")))
        post_message(auth_token,"#crypto", "현재 비트코인 잔액 : " + str(get_balance("BTC")))
        post_message(auth_token,"#crypto", "BTC 현재 가격 : " + str(current_price))
        if current_price < target_price :
            flag = ":red_circle:"
        else :
            flag = ":large_blue_circle:"

        post_message(auth_token,"#crypto", "BTC 타겟 가격 : " + str(target_price) + " " + flag)
        if current_price < ma15 :
            flag = ":red_circle:"
        else :
            flag = ":large_blue_circle:"       
        post_message(auth_token,"#crypto", "BTC 15일 이동 평균선 : " + str(ma15) + " " + flag)
        if predicted_close_price < current_price :
            flag = ":red_circle:"
        else :
            flag = ":large_blue_circle:" 
        post_message(auth_token,"#crypto", "BTC 당일 예상 종가 : " + str(predicted_close_price) + " " + flag)
        post_message(auth_token,"#crypto", "-----------------------------------------------------------------")

# 로그인
upbit = pyupbit.Upbit(access, secret)
k_value = 0.5
print("autotrade start")
post_message(auth_token,"#crypto", ":eight_pointed_black_star::eight_pointed_black_star::eight_pointed_black_star: 자동 매매가 시작합니다. :eight_pointed_black_star::eight_pointed_black_star::eight_pointed_black_star:")
post_message(auth_token,"#crypto", "k 값 : " + str(k_value))
post_message(auth_token,"#crypto", "현재 자금 : " + str(upbit.get_balance("KRW")))
post_message_daily("KRW-BTC")

schedule.every().hour.do(lambda: predict_price("KRW-BTC"))
schedule.every(360).minutes.do(lambda: post_message_daily("KRW-BTC"))


# 자동매매 시작
while True:
    try:
        # 현재시간
        now = datetime.datetime.now()
        # 시작시간 업비트 API 기준 일봉 시작 시간 09:00
        start_time = get_start_time("KRW-BTC")
        # 마감시간 업비트 API 기준 일봉 마감 시간 09:00 + 1일
        end_time = start_time + datetime.timedelta(days=1)

        schedule.run_pending()
        
        # 마감시간 - 10초까지 돌아간다.
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            # 변동성 돌파 전략으로 매수 목표가 조회
            target_price = get_target_price("KRW-BTC", k_value)
            # 15일 이동평균선 계산
            ma15 = get_ma15("KRW-BTC")
            # 현재 시가
            current_price = get_current_price("KRW-BTC")
            # 현재 가격이 목표값보다 높다면
            if target_price < current_price and ma15 < current_price and current_price < predicted_close_price:
                # 내 원화 잔고를 조회하고
                krw = get_balance("KRW")
                # 잔고가 최소 거래 금액인 5000원보다 높다면
                if krw > 5000:
                    # 코인을 산다. 수수료 0.05%를 고려한다.
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    post_message_daily("KRW-BTC")
                    post_message(auth_token,"#crypto", ":tada: BTC buy : " + str(buy_result))
        # 9시 10초전부터는 비트코인을 전량 매도한다.
        else:
            # 현재 BTC의 잔고를 가져와서 
            btc = get_balance("BTC")
            # 현재 비트코인 잔고가 0.00008 이상이면 판매를 한다.
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                post_message(auth_token,"#crypto", "현재 잔고 : " + str(upbit.get_balance("KRW")))
                post_message(auth_token,"#crypto", "BTC sell : " +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(auth_token,"#crypto", ':red_circle:에러발생:red_circle: \n' + str(e))
        time.sleep(1)