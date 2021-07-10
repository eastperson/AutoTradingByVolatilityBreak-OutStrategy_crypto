import pyupbit
import numpy as np

# OHLV(open, high, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터
# 원화시장의 BTC의 7일동안의 OHLCV 값을 불러온다.
df = pyupbit.get_ohlcv("KRW-BTC",count=7)

# 변동폭 * k 계산, (고가 - 저가) * k값
# range 컬럼의 변동폭 * k 값을 잡는다.
df['range'] = (df['high'] - df['low']) * 0.5

# target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
# target 매수가를 알려준다.
df['target'] = df['open'] + df['range'].shift(1)

# ror(수익율), np.where(조건문, 참일때 값, 거짓일 때 값)
# target 매수값보다 높으면 매도를 진행한다. 따라서 종가 / 목표가가 되어 나온 값이 수익률이다.
# 거짓일 때는 매도를 진행하지 않아 1이 된다.
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'],
                     1)

# 누적 곲 계산(cumprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()

# Draw Down 계산 (누적 최대 값과 현재 hrp 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

# MDD 계산
print("MDD(%): ", df['dd'].max())
df.to_excel("dd.xlsx")