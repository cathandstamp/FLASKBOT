from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
import requests
import pprint
from bs4 import BeautifulSoup


###ここから追加
import pya3rt

app = Flask(__name__)

#環境変数取得
# LINE Developersで設定されているアクセストークンとChannel Secretをを取得し、設定します。
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


## 1 ##
#Webhookからのリクエストをチェックします。
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得します。
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得します。
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body# 署名を検証し、問題なければhandleに定義されている関数を呼び出す。
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:# 署名検証で失敗した場合、例外を出す。
        abort(400)
        # handleの処理を終えればOK
    return 'OK'

## 2 ##
###############################################
#LINEのメッセージの取得と返信内容の設定(オウム返し)
###############################################

#LINEでMessageEvent（普通のメッセージを送信された場合）が起こった場合に、
#def以下の関数を実行します。
#reply_messageの第一引数のevent.reply_tokenは、イベントの応答に用いるトークンです。 
#第二引数には、linebot.modelsに定義されている返信用のTextSendMessageオブジェクトを渡しています。

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    push_text = event.message.text
    ai_message = talk_ai(push_text)


    if push_text == "熊本天気":
       
        reply_text = "気象庁のHPを確認します"   
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))

        url = 'https://tenki.jp/forecast/9/46/8610/43100/'
        res = requests.get(url)

        soup = BeautifulSoup(res.text, "html.parser")
        #print(soup)

        found = soup.find_all('p',class_='weather-telop')
        found2 = soup.find_all('h3',class_='left-style')

        
        textA = found2[0].text + found[0].text +'\n'+found2[1].text + found[1].text
        textA = '熊本の天気\n'+textA

        reply_text =  textA
        """
        url = 'https://tenki.jp/forecast/9/46/8610/43100/'
        res = requests.get(url)

        soup = BeautifulSoup(res.text, "html.parser")
        #print(soup)

        found = soup.find('p',class_='weather-telop')
        found2 = soup.find('h3',class_='left-style')

        textA = found2.text + found.text

        reply_text =  textA
        """


    elif push_text == "自己紹介":
        reply_text = "猫の手も借りたいそんな、私にはAIchatが搭載されています。\n色んな会話をして下さい。"   

    elif push_text == "ごまはかわいい":
        reply_text = "はい、その通りです。動画を撮り、家族で共有すべきだと思います。コロナのせいで、皆にあいにくいいま動画コンテンツは利用するべきです。"   
      
        
    elif push_text == "転職したい":
        reply_text = "Let's　Action"   
        


    else:
        reply_text = ai_message   

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))



def talk_ai(word):
    apikey = "DZZO7R4UhHZIvhcASPfHOiGoeFVcD1gj"
    client = pya3rt.TalkClient(apikey)
    reply_message = client.talk(word)
    return reply_message['results'][0]['reply']

# ポート番号の設定
if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



