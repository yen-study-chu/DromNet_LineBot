from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction,
    URIAction, QuickReply, QuickReplyButton, RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, RichMenuResponse
)
import os
from config import config

app = Flask(__name__)

#
# =========== 載入開發時環境 ===========
# if app.config["ENV"] == "production":
#     app.config.from_object(config['pro'])
# else:
#     app.config.from_object(config['dev'])
# line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])
# handler = WebhookHandler(app.config['CHANNEL_SECRET'])


# =========== 載入上線時環境 ===========
line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))

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
    # print(event)
    if event.message.text == "開始使用":
        buttons_template_message = TemplateSendMessage(
            alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
            template=ButtonsTemplate(
                # thumbnail_image_url='https://example.com/image.jpg',
                title='請選擇你目前碰到的問題 !!!',
                text='嗨！我是中華大學宿網會小機器人！下面是我目前提供的問答唷！',
                actions=[
                    # PostbackAction(
                    #     label='postback',
                    #     display_text='postback text',
                    #     data='action=buy&itemid=1'
                    # ),
                    MessageAction(
                        label='網路連線',
                        text='網路故障'
                    ),
                    MessageAction(
                        label='網路故障',
                        text='網路故障'
                    ),
                    MessageAction(
                        label='宿網會值班時間',
                        text='宿網會值班時間'
                    ),
                    # URIAction(
                    #     label='uri',
                    #     uri='http://example.com/'
                    # )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    else:
        text_message = TextSendMessage(text='請點擊下方，按鈕開始。',
                                       quick_reply=QuickReply(items=[
                                           QuickReplyButton(action=MessageAction(label="開始使用", text="開始使用"))
                                       ]))
    line_bot_api.reply_message(event.reply_token, text_message)

    return 'OK2'


if __name__ == "__main__":
    app.run(port="8000", debug=True)
