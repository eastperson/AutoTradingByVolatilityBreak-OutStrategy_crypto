from slacker import Slacker
import requests

auth_token = 'xoxb-1886651932615-2253766631622-ePtPj9v8nzFt8NwGxVi072YO'

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)

import pyupbit

access = "pbxCPbQ9SokGoJrsJlcXYkm2j8dBCNQLYMuxdFxL"          # 본인 값으로 변경
secret = "bPnk06xTLhigOx4d812PdOSIqSr5cYK5QDlxrP3R"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-XRP"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회

curBalance = '현재 자금 조회 : ' + str(upbit.get_balance("KRW"))
post_message(auth_token,'#crypto',curBalance)