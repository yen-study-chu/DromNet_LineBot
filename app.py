from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction,
    URIAction, QuickReply, QuickReplyButton, RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, RichMenuResponse,
    ConfirmTemplate
)
import os

app = Flask(__name__)

# =========== 載入開發時環境 ===========
# from config import config
#
# if app.config["ENV"] == "production":
#     app.config.from_object(config['pro'])
# else:
#     app.config.from_object(config['dev'])
# line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])
# handler = WebhookHandler(app.config['CHANNEL_SECRET'])


# =========== 載入上線時環境 ===========z
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
    # options: 網路連線教學, 網路故障報修
    if event.message.text == "連線教學":
        buttons_template_message = TemplateSendMessage(
            alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
            template=ButtonsTemplate(
                # thumbnail_image_url='https://example.com/image.jpg',
                title='請選擇你目前碰到的問題 !!!',
                text='嗨！我是中華大學宿網會小機器人！下面是我目前提供的問答唷！',
                actions=[
                    MessageAction(
                        label='網路連線教學',
                        text='網路連線教學'
                    ),
                    MessageAction(
                        label='網路故障報修',
                        text='網路故障報修'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # options: 我知道網路帳號, 我不知道網路帳號, 重新開始
    elif event.message.text == "網路連線教學":
        buttons_template_message = TemplateSendMessage(
            alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
            template=ButtonsTemplate(
                title='請問是否知道網路帳號？',
                text='請選擇下面的選項。',
                actions=[
                    MessageAction(
                        label='是',
                        text='我知道網路帳號'
                    ),
                    MessageAction(
                        label='否',
                        text='我不知道網路帳號'
                    ),
                    MessageAction(
                        label='重新開始',
                        text='重新開始'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # options: Windows, macOS, 網路連線教學
    elif event.message.text == "我知道網路帳號":
        buttons_template_message = TemplateSendMessage(
            alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
            template=ButtonsTemplate(
                title='請問您的電腦系統為何？',
                text='請選擇下面的選項。',
                actions=[
                    MessageAction(
                        label='Windows',
                        text='Windows'
                    ),
                    MessageAction(
                        label='Apple macOS',
                        text='macOS'
                    ),
                    MessageAction(
                        label='上一步',
                        text='網路連線教學'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # options: 男宿, 女宿
    elif event.message.text == "我不知道網路帳號" or event.message.text == "查詢網路帳號密碼":
        buttons_template_message = TemplateSendMessage(
            alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
            template=ButtonsTemplate(
                title='請問你是住男宿還是女宿呢？',
                text='請選擇下面的選項。',
                actions=[
                    MessageAction(
                        label='男宿',
                        text='男宿'
                    ),
                    MessageAction(
                        label='女宿',
                        text='女宿'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # options: Windows 7, Windows 8, Windows 10
    elif event.message.text == "Windows":
        buttons_template_message = TemplateSendMessage(
            alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
            template=ButtonsTemplate(
                title='請問是 Windows 的哪個版本呢？',
                text='請選擇下面的選項。',
                actions=[
                    MessageAction(
                        label='Windows 7',
                        text='Windows 7'
                    ),
                    MessageAction(
                        label='Windows 8',
                        text='Windows 8'
                    ),
                    MessageAction(
                        label='Windows 10',
                        text='Windows 10'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # options: 網路帳號密碼查詢, 報修與協助
    elif event.message.text == "Windows 7":
        # TODO userId 取法, github issue https://github.com/line/line-bot-sdk-python/issues/139
        user = event.source.user_id
        text = "網路設定步驟如下：\n開啟【控制台】>【網路和網際網路】>【設定新的連線與網路】>【選擇連線到網際網路】>【下一步】>【寬頻(PPPOE)】 > 輸入使用者帳號及密碼。"
        line_bot_api.push_message(to=user,
                                  messages=TextSendMessage(text))
        confirm_template_message = TemplateSendMessage(
            alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
            template=ConfirmTemplate(
                text='目前有跟上前一封訊息嗎？',
                actions=[
                    MessageAction(
                        label='是',
                        text='網路帳號密碼查詢'
                    ),
                    MessageAction(
                        label='否',
                        text='報修與協助'
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
    # options: 網路帳號密碼查詢, 報修與協助
    elif event.message.text == "Windows 8":
        user = event.source.user_id
        text = "網路設定步驟如下：\n開啟【網路和共用中心】>【設定新的連線與網路】>【選擇連線到網際網路】>【下一步】>【寬頻(PPPOE)】> 輸入使用者帳號及密碼。"
        line_bot_api.push_message(to=user,
                                  messages=TextSendMessage(text))
        confirm_template_message = TemplateSendMessage(
            alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
            template=ConfirmTemplate(
                text='目前有跟上前一封訊息嗎？',
                actions=[
                    MessageAction(
                        label='是',
                        text='網路帳號密碼查詢'
                    ),
                    MessageAction(
                        label='否',
                        text='報修與協助'
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
    # options: 網路帳號密碼查詢, 報修與協助
    elif event.message.text == "Windows 10":
        user = event.source.user_id
        text = "網路設定步驟如下：\n開啟【控制台】>【網路和網際網路】>【網路和共用】>【設定新的連線與網路】>【選擇連線到網際網路】>【下一步】>【寬頻(PPPOE)】> 輸入使用者帳號及密碼。"
        line_bot_api.push_message(to=user,
                                  messages=TextSendMessage(text))
        confirm_template_message = TemplateSendMessage(
            alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
            template=ConfirmTemplate(
                text='目前有跟上前一封訊息嗎？',
                actions=[
                    MessageAction(
                        label='是',
                        text='網路帳號密碼查詢'
                    ),
                    MessageAction(
                        label='否',
                        text='報修與協助'
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
    # options: 網路帳號密碼查詢, 報修與協助
    elif event.message.text == "macOS":
        user = event.source.user_id
        text = "網路設定步驟如下：\n【系統偏好設定】>【網路】>【點及左側底部「加入」並選擇 PPPoE】>【按一下「乙太網路」彈出式選單】> 輸入使用者帳號及密碼。"
        line_bot_api.push_message(to=user,
                                  messages=TextSendMessage(text))
        confirm_template_message = TemplateSendMessage(
            alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
            template=ConfirmTemplate(
                text='目前有跟上前一封訊息嗎？',
                actions=[
                    MessageAction(
                        label='是',
                        text='網路帳號密碼查詢'
                    ),
                    MessageAction(
                        label='否',
                        text='報修與協助'
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
    elif event.message.text == "是，我知道網路帳號。":
        pass
    elif event.message.text == "是，我知道網路帳號。":
        pass
    elif event.message.text == "是，我知道網路帳號。":
        pass
    elif event.message.text == "是，我知道網路帳號。":
        pass
    # elif event.message.text == "":
    #     confirm_template_message = TemplateSendMessage(
    #         alt_text='歡迎使用中華大學宿網會的簡易小機器人, 請點擊下方按鈕進行下一步。',
    #         template=ConfirmTemplate(
    #             text='請問有解決你的連線問題嗎？',
    #             actions=[
    #                 MessageAction(
    #                     label='是',
    #                     text='網路設定已經完成'
    #                 ),
    #                 MessageAction(
    #                     label='否',
    #                     text='網路設定尚未成功'
    #                 ),
    #             ]
    #         )
    #     )
    #     line_bot_api.reply_message(event.reply_token, confirm_template_message)
    else:
        text_message = TextSendMessage(text='請點擊下方，按鈕開始。',
                                       quick_reply=QuickReply(items=[
                                           QuickReplyButton(action=MessageAction(label="連線教學", text="連線教學")),
                                           QuickReplyButton(action=MessageAction(label="報修與協助", text="報修與協助")),
                                           QuickReplyButton(action=MessageAction(label="連線帳號及密碼", text="連線帳號及密碼"))
                                       ]))
        line_bot_api.reply_message(event.reply_token, text_message)
    return 'OK2'


if __name__ == "__main__":
    app.run()
    # app.run(port="8000", debug=True)
