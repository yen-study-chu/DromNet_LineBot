from flask import Flask, request, abort, render_template, send_file
from urllib.parse import urlparse

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    TemplateSendMessage,
    MessageAction,
    QuickReply,
    QuickReplyButton,
    ConfirmTemplate,
)
from linebot.models.actions import URIAction
from linebot.models.template import CarouselColumn, CarouselTemplate

import utils
import io
import os

app = Flask(__name__)

# =========== 載入開發時環境 ===========
# from config import config

# if app.config["ENV"] == "production":
#     app.config.from_object(config["pro"])
# else:
#     app.config.from_object(config["dev"])
# line_bot_api = LineBotApi(app.config["CHANNEL_ACCESS_TOKEN"])
# handler = WebhookHandler(app.config["CHANNEL_SECRET"])

# =========== 載入上線時環境 ===========
line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


@app.route("/", methods=["GET"])
def index():
    # 一定要建立一個資料夾叫做：/templates，如果沒有設定，會優先指向 templates 資料夾。
    return render_template(
        "index.html",
    )


@app.route("/static/<path:filepath>/", methods=["GET"])
def img(filepath=None):
    if filepath is None:
        return render_template("404.html")
    else:
        with open(f"app/static/{filepath}", "rb") as bites:
            return send_file(io.BytesIO(bites.read()), mimetype="image/png")


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    host = f"https://{urlparse(request.base_url).hostname}"
    user = event.source.user_id
    # Step 1
    if event.message.text == "新生":
        carousel_template_message = TemplateSendMessage(
            alt_text="歡迎使用中華大學宿網會的簡易小機器人, 請至手機查看訊息。",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/new/s1.jpeg",
                        title="第一步：購買一條網路線",
                        text="規格：RJ-45 接口。\n長度：建議先到床位測量使用範圍。\n需要將網路線插入床位的壁孔才能使用。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/new/s1.jpeg",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/new/s2.jpeg",
                        title="第二步：檢查電腦有無網路孔",
                        text="有網路孔請回答下面視窗，\n無網路孔請往右滑向第三步。\n學校宿舍內無 WIFI，教室則有公共 WIFI。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/new/s2.jpeg",
                            )
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/new/s3.jpeg",
                        title="第三步：電腦無網路孔需購買轉接頭",
                        text="轉接頭名稱：「RJ-45 轉 USB」",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/new/s3.jpeg",
                            )
                        ],
                    ),
                ]
            ),
        )

        confirm_template_message = utils.ConfirmWindow(
            context="上面步驟已完成，你是屬於？", success_string="男生宿舍", error_string="女生宿舍"
        )

        line_bot_api.push_message(user, carousel_template_message)
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
    # # Step 2 "一宿五樓", "二宿", "三宿"
    elif event.message.text == "男生宿舍":
        buttons_template_message = utils.ButtonWindow(
            title="請選擇你的宿舍及樓層：",
            context="請選擇下面的選項：",
            number=3,
            label_list=["一宿五樓", "二宿", "三宿"],
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # # Step 2 "一宿", "四宿"
    elif event.message.text == "女生宿舍":
        buttons_template_message = utils.ButtonWindow(
            title="請選擇妳的宿舍：",
            context="請選擇下面的選項：",
            number=2,
            label_list=["一宿", "四宿"],
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # # # Step 3 "一宿五樓"
    elif event.message.text == "一宿五樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/1-5.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="透過上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # # # Step 3 "一宿"
    elif event.message.text == "一宿":
        buttons_template_message = utils.ButtonWindow(
            title="請選擇妳的樓層：",
            context="請選擇下面的選項：",
            number=3,
            label_list=["一宿二樓", "一宿三樓", "一宿四樓"],
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # # # Step 3 "二宿"
    elif event.message.text == "二宿":
        buttons_template_message_1 = utils.ButtonWindow(
            title="請選擇你的樓層：",
            context="請選擇下面的選項：",
            number=4,
            label_list=["二宿二樓", "二宿三樓", "二宿四樓", "二宿五樓"],
        )
        buttons_template_message_2 = utils.ButtonWindow(
            title="請選擇你的樓層：",
            context="請選擇下面的選項：",
            number=3,
            label_list=["二宿六樓", "二宿七樓", "二宿八樓"],
        )
        line_bot_api.push_message(user, buttons_template_message_1)
        line_bot_api.reply_message(event.reply_token, buttons_template_message_2)
    # # # Step 3 "三宿"
    elif event.message.text == "三宿":
        buttons_template_message_1 = utils.ButtonWindow(
            title="請選擇你的樓層：",
            context="請選擇下面的選項：",
            number=3,
            label_list=["三宿一樓", "三宿二樓", "三宿三樓"],
        )
        buttons_template_message_2 = utils.ButtonWindow(
            title="請選擇你的樓層：",
            context="請選擇下面的選項：",
            number=3,
            label_list=["三宿四樓", "三宿五樓", "三宿六樓"],
        )
        line_bot_api.push_message(user, buttons_template_message_1)
        line_bot_api.reply_message(event.reply_token, buttons_template_message_2)
    # # # Step 3 "四宿"
    elif event.message.text == "四宿":
        buttons_template_message_1 = utils.ButtonWindow(
            title="請選擇妳的樓層：",
            context="請選擇下面的選項：",
            number=3,
            label_list=["四宿一樓", "四宿二樓", "四宿三樓"],
        )
        buttons_template_message_2 = utils.ButtonWindow(
            title="請選擇妳的樓層：",
            context="請選擇下面的選項：",
            number=3,
            label_list=["四宿四樓", "四宿五樓", "四宿六樓"],
        )
        line_bot_api.push_message(user, buttons_template_message_1)
        line_bot_api.reply_message(event.reply_token, buttons_template_message_2)

    elif event.message.text == "一宿二樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/1-2.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "一宿三樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/1-3.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "一宿四樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/1-4.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "二宿二樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/2-2.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "二宿三樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/2-3.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "二宿四樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/2-4.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "二宿五樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/2-5.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "二宿六樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/2-6.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "二宿七樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/2-7.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "二宿八樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/2-8.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "三宿一樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/3-1.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "三宿二樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/3-2.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "三宿三樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/3-3.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "三宿四樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/3-4.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "三宿五樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/3-5.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "三宿六樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/3-6.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "四宿一樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/4-1.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "四宿二樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/4-2.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "四宿三樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/4-3.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "四宿四樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/4-4.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "四宿五樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/4-5.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif event.message.text == "四宿六樓":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/hinet/4-6.jpeg"
        )
        alert_message = TextSendMessage(
            text=f"請找到同寢室的「HN 帳號」，\n並在後面加上「@hinet.net」\n{utils.Separate(10)} \n範例：1501房為 72186749，\n那帳號就是「72186749@hinet.net」，\n密碼全校宿舍皆為：「123456」。"
        )
        buttons_template_message = utils.ButtonWindow(
            title="請根據上則訊息尋找連線帳號密碼：",
            context="請選擇下列選項。",
            number=3,
            label_list=["連線教學", "網路報修", "重新選擇宿舍"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, alert_message)
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif (
        event.message.text == "查詢網路帳號密碼"
        or event.message.text == "不知道帳號密碼"
        or event.message.text == "重新選擇宿舍"
    ):
        confirm_template_message = utils.ConfirmWindow(
            context="請問您是屬於？", success_string="男生宿舍", error_string="女生宿舍"
        )
        line_bot_api.reply_message(event.reply_token, confirm_template_message)

    # options: Windows, macOS, 連線教學
    elif event.message.text == "連線教學":
        buttons_template_message = utils.ButtonWindow(
            title="請問您的電腦系統為何？",
            context="請選擇下面的選項。",
            number=2,
            label_list=["Windows", "macOS"],
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # options: Windows 7, Windows 8, Windows 10
    elif event.message.text == "Windows":
        buttons_template_message = utils.ButtonWindow(
            title="請問是 Windows 的哪個版本呢？",
            context="請選擇下面的選項。",
            number=3,
            label_list=["Windows 7", "Windows 8", "Windows 10"],
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # options: 網路帳號密碼查詢,
    elif event.message.text == "Windows 7" or event.message.text == "Windows 8":
        # TODO userId 取法, github issue https://github.com/line/line-bot-sdk-python/issues/139
        user = event.source.user_id
        text = "網路設定步驟如下：\n開啟【控制台】>【網路和網際網路】的【檢視網際狀態及工作】>【設定新的連線與網路】>【選擇連線到網際網路】>【下一步】>【寬頻(PPPOE)】 > 輸入使用者帳號及密碼。"
        carousel_template_message = TemplateSendMessage(
            alt_text="歡迎使用中華大學宿網會的簡易小機器人, 請至手機查看訊息。",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/7_0.png",
                        title="Win7：進入控制台",
                        text="如上圖所示，\n點擊「Windows按鍵」後左鍵點擊「控制台」。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/7_0.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/7_1.png",
                        title="第一步：檢視網際狀態及工作",
                        text="如上圖所示。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/7_1.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/7_2.png",
                        title="第二步：設定新的網路連線",
                        text="如上圖所示，直接設定新連線。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/7_2.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/7_3.png",
                        title="第四步：點擊連線到網際網路",
                        text="如上圖所示，點擊「連線到網際網路」，點選下一步。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/7_3.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/7_4.png",
                        title="第五步：選擇寬頻連線(PPPOE)",
                        text="如上圖所示，點擊寬頻(PPPOE)。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/7_4.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/7_5.png",
                        title="第六步：輸入連線的HN帳號及密碼",
                        text="如上圖所示，輸入HN帳號及密碼，若忘記可以到下面點選「不知道帳號密碼」。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/7_5.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/7_6.png",
                        title="第七步：確認畫面及測試",
                        text="如上圖所示，出現了「連線已經可以使用」，可以將瀏覽器打開，測試是否能上網。不能請點選「我需要協助」。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/7_6.png",
                            ),
                        ],
                    ),
                ]
            ),
        )
        if event.message.text == "Windows 8":
            text += "\nWindows 8 進入控制台方式，可以參考：\nhttps://dotblogs.com.tw/chou/2012/06/13/72763\n進入控制台請跳至下方第一步。"
        confirm_template_message = utils.ButtonWindow(
            title="請問有解決你的問題嗎？",
            context="請選擇下面的選項。",
            number=3,
            label_list=["不知道帳號密碼", "我需要協助", "已完成"],
        )
        line_bot_api.push_message(to=user, messages=carousel_template_message)
        line_bot_api.push_message(to=user, messages=TextSendMessage(text))
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
    # options: 網路帳號密碼查詢,
    elif event.message.text == "Windows 10":
        user = event.source.user_id
        carousel_template_message = TemplateSendMessage(
            alt_text="歡迎使用中華大學宿網會的簡易小機器人, 請至手機查看訊息。",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/10_0.png",
                        title="第一步：進入連線設定頁面",
                        text="如上圖所示，\n右鍵點擊「網路圖示」，選取「開啟網路和網際網路設定」。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/10_0.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/10_1.png",
                        title="第二步：使用網路線接上電腦",
                        text="如上圖所示，\n插上網路線後，點擊撥號。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/10_1.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/10_2.png",
                        title="第三步：設定新連線",
                        text="如上圖所示，直接設定新連線。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/10_2.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/10_3.png",
                        title="第四步：點擊連線到網際網路",
                        text="如上圖所示，點擊「連線到網際網路」。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/10_3.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/10_4.png",
                        title="第五步：選擇寬頻連線(PPPOE)",
                        text="如上圖所示，點擊寬頻(PPPOE)。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/10_4.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/10_5.png",
                        title="第六步：輸入連線的HN帳號及密碼",
                        text="如上圖所示，輸入HN帳號及密碼，若忘記可以到下面點選「不知道帳號密碼」。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/10_5.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/win/10_6.png",
                        title="第七步：確認畫面及測試",
                        text="如上圖所示，出現了「您已連線到網際網路」，可以將瀏覽器打開，測試是否能上網。不能請點選「我需要協助」。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/win/10_6.png",
                            ),
                        ],
                    ),
                ]
            ),
        )
        text = "網路設定步驟如下：\n右鍵點擊【網路圖示】> 左鍵點擊【開啟網路和網際網路設定】>【撥號】>【設定新的連線】>【連線到網際網路】>【寬頻(PPPOE)】> 【輸入連線的HN帳號及密碼】。"
        confirm_template_message = utils.ButtonWindow(
            title="請問有解決你的問題嗎？",
            context="請選擇下面的選項。",
            number=3,
            label_list=["不知道帳號密碼", "我需要協助", "已完成"],
        )
        line_bot_api.push_message(user, carousel_template_message)
        line_bot_api.push_message(to=user, messages=TextSendMessage(text))
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
    # options: 網路帳號密碼查詢,
    elif event.message.text == "macOS":
        user = event.source.user_id
        carousel_template_message = TemplateSendMessage(
            alt_text="歡迎使用中華大學宿網會的簡易小機器人, 請至手機查看訊息。",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/mac/m1.png",
                        title="第一步：點擊網路偏好服務",
                        text="如上圖所示，\n滑鼠移至 WIFI 圖示左鍵點擊後，\n再點選網路偏好服務。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/mac/m1.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/mac/m2.png",
                        title="第二步：建立 PPPOE 服務",
                        text="插上轉接器後，才會跳出此畫面。\n接者如上圖所示：\n點選設定IPv4 > 建立 PPPOE 服務。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/mac/m2.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/mac/m3.png",
                        title="第三步：輸入網路帳號密碼",
                        text="如上圖所示，輸入HN帳號名稱及密碼，\n不知道帳號可以點擊下面「不知道帳號密碼」",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/mac/m3.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/mac/m4.png",
                        title="第四步：完成連線",
                        text="點擊連線後，就可以正常使用連線囉！\n如果還是不能使用，\n請點擊下面「我需要協助」。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/mac/m4.png",
                            ),
                        ],
                    ),
                ]
            ),
        )
        text = "網路設定步驟如下：\n【左上角蘋果圖示】>【系統偏好設定】>【網路】>【插上轉接頭】>【點擊左側 USB】>【點擊右側 IPv4】> 【建立 PPPOE 服務】> 【輸入HN帳號及密碼】> 【點擊連線】。"
        confirm_template_message = utils.ButtonWindow(
            title="請問有解決你的問題嗎？",
            context="請選擇下面的選項。",
            number=3,
            label_list=["不知道帳號密碼", "我需要協助", "已完成"],
        )
        line_bot_api.push_message(user, carousel_template_message)
        line_bot_api.push_message(to=user, messages=TextSendMessage(text))
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
    # over: 已完成連線
    elif event.message.text == "已完成":
        text = "很高興你已經可以使用宿舍網路了！\n我們下次見～"
        buttons_template_message = utils.ButtonWindow(
            title="請選擇下一步：",
            context="你下一步要去哪呢？",
            number=3,
            label_list=["回到一開始", "我需要協助", "連線教學"],
        )
        line_bot_api.push_message(to=user, messages=TextSendMessage(text))
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    # options: 使用者需要協助的部分
    elif event.message.text == "我需要協助":
        buttons_template_message = utils.ButtonWindow(
            title="請問要如何協助你呢？",
            context="請選擇下面的選項，\n目前有兩種方式。",
            number=2,
            label_list=["網路報修", "宿網會"],
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    elif event.message.text == "網路報修":
        carousel_template_message = TemplateSendMessage(
            alt_text="歡迎使用中華大學宿網會的簡易小機器人, 請至手機查看訊息。",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/fix/01.png",
                        title="第一步：進入學生資訊系統",
                        text="如上圖所示。進入學校首頁, 前往學生資訊系統。下方按鈕可以直接前往。（建議搭配電腦使用）",
                        actions=[
                            URIAction(
                                label="前往學生資訊系統",
                                uri=f"https://student2.chu.edu.tw/",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/fix/02.png",
                        title="第二步：登入學生資訊系統",
                        text="如上圖所示。\n輸入帳號及密碼。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/fix/02.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/fix/03.png",
                        title="第三步：點擊學生宿舍報修系統",
                        text="如上圖所示。\n【左方導航列】 >【學務系統】>【學生宿舍報修系統】。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/fix/03.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/fix/04.png",
                        title="第四步：點擊宿舍報修",
                        text="如上圖所示。\n【上方導航列】 >【宿舍報修&報修查詢】>【宿舍報修】。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/fix/04.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/fix/05.png",
                        title="第五步：填寫報修申請表",
                        text="如上圖所示。\n建議使用大圖觀看，請將需求填寫詳細，並留下地點資訊。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/fix/05.png",
                            ),
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{host}/static/img/fix/local.jpg",
                        title="需要尋找我們？",
                        text="我們的辦公室如上圖所示。\n位於三宿(萊爾富那一棟)，男生宿舍大門右手邊。",
                        actions=[
                            URIAction(
                                label="點我，觀看完整圖片",
                                uri=f"{host}/static/img/fix/local.jpg",
                            ),
                        ],
                    ),
                ]
            ),
        )
        ConfirmWindow = utils.ConfirmWindow(
            context="請問解決你的問題了嗎？", success_string="需要協助", error_string="已完成"
        )
        line_bot_api.push_message(user, carousel_template_message)
        line_bot_api.reply_message(event.reply_token, ConfirmWindow)
    elif event.message.text == "宿網會" or event.message.text == "需要協助":
        image_message = utils.ImageWindow(
            origin_path=f"{host}/static/img/fix/local.jpg"
        )
        text_message = "服務時間：\n每週一至週四，20:00 至 21:30。\n=\n服務地點：三宿管制門右手邊(萊爾富那棟)\n若不知道位置請看上圖。\n=\n注意：請務必敲門後開門。\n=\n無人回應請用網路報修，我們會於服務時間處理！"
        buttons_template_message = utils.ButtonWindow(
            title="請選擇下一步：",
            context="你下一步要去哪呢？",
            number=3,
            label_list=["回到一開始", "我需要協助", "連線教學"],
        )
        line_bot_api.push_message(user, image_message)
        line_bot_api.push_message(user, TextSendMessage(text_message))
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    elif event.message.text == "意見回饋":
        text_message = "意見回饋的表單連結：\nhttps://docs.google.com/forms/d/e/1FAIpQLSc3Vt6Ji8SE025whcbZN-GeX_-WvKe23Sl-wEydHc1xD06Cbw/formResponse"
        line_bot_api.push_message(user, TextSendMessage(text_message))
    else:
        text_message = TextSendMessage(｀
            text="請點擊下方功能選單按鈕使用機器人。\n",
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="我是新生 👋", text="新生")),
                    QuickReplyButton(
                        action=MessageAction(label="查詢網路帳號密碼", text="查詢網路帳號密碼")
                    ),
                    QuickReplyButton(action=MessageAction(label="連線教學 👌", text="連線教學")),
                    QuickReplyButton(
                        action=MessageAction(label="我需要協助 🤝", text="我需要協助")
                    ),
                    QuickReplyButton(action=MessageAction(label="意見回饋", text="意見回饋")),
                ]
            ),
        )
        line_bot_api.reply_message(event.reply_token, text_message)
    return "OK2"


if __name__ == "__main__":
    # app.run()
    app.run(port="5000", debug=True)
