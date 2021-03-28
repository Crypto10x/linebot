from os import environ

from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, PostbackEvent,
)
from web3 import Web3, HTTPProvider

load_dotenv()

web3 = Web3(
    provider=HTTPProvider('https://rinkeby.infura.io/v3/bc2b4342c53e460d99a232dac871013e')
)

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = environ.get('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = environ.get('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    if event.postback.data == "CHECK_BALANCE":
        balance_wei = web3.eth.get_balance("0xecAb0F7Fd7E171202844d85de5011dd1608E83Fd")
        balance_eth = web3.fromWei(balance_wei, 'ether')
        txt = str(balance_eth) + " ETH"
        msg = TextSendMessage(text=txt)
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=msg
        )


if __name__ == "__main__":
    port = environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port)
