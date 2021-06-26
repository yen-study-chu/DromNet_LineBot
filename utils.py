from linebot.models import template
from linebot.models.actions import MessageAction
from linebot.models.send_messages import ImageSendMessage
from linebot.models.template import (
    ButtonsTemplate,
    CarouselColumn,
    ConfirmTemplate,
    TemplateSendMessage,
)


def Separate(n):
    return "=" * n


def ConfirmWindow(context, sucess_string, error_string):
    """
    重複使用只有對或錯的確認視窗

    :params context
    :params sucess_string
    :params error_string
    """
    confirm_template_message = TemplateSendMessage(
        alt_text="歡迎使用中華大學宿網會的簡易小機器人, 請至手機查看訊息。",
        template=ConfirmTemplate(
            text=f"{context}",
            actions=[
                MessageAction(label=f"{sucess_string}", text=f"{sucess_string}"),
                MessageAction(label=f"{error_string}", text=f"{error_string}"),
            ],
        ),
    )
    return confirm_template_message


def ButtonWindow(title, context, number, label_list):
    if number == len(label_list):
        actions = []
        for i in range(0, number):
            ButtonAction = MessageAction(
                label=f"{label_list[i]}", text=f"{label_list[i]}"
            )
            actions.append(ButtonAction)

        buttons_template_message = TemplateSendMessage(
            alt_text="歡迎使用中華大學宿網會的簡易小機器人, 請至手機查看訊息。",
            template=ButtonsTemplate(
                title=f"{title}", text=f"{context}", actions=actions
            ),
        )
        return buttons_template_message
    else:
        # FIXME 這邊到時候再寫判斷，基本上我自己寫不會去故意設不一樣的值 ...
        pass


def ImageWindow(origin_path, preview_path=None):
    if preview_path == None:
        preview_path = origin_path

    image_message = ImageSendMessage(
        original_content_url=f"{origin_path}",
        preview_image_url=f"{preview_path}",
    )
    return image_message
