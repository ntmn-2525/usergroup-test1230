# Standard modules.
import os
import urllib

# Django modules.
from django.http import (
    HttpResponse,
)

# LINE Bot modules.
from linebot import (
    LineBotApi,
    WebhookHandler,
)

from linebot.models import (
    ButtonsTemplate,
    CarouselColumn,
    CarouselTemplate,
    FollowEvent,
    MessageEvent,
    MessageTemplateAction,
    PostbackAction,
    PostbackEvent,
    TemplateSendMessage,
    TextMessage,
    TextSendMessage,
    UnfollowEvent,
)

from linebot.exceptions import (
    InvalidSignatureError,
)

# Local modules.
from .logging import (
    to_log_level,
    SimpleConsoleLogger,
)

from .services import (
    LinebotService,
)

from .settings_line_bot import (
    LINE_BOT_NAME,
)

from data_storage.models import (
    Category,
    LineFriend,
)

try:
    DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
except ImportError:
    from poa_web.settings_local import (
        DJANGO_LOG_LEVEL,
        LINE_CHANNEL_SECRET,
        LINE_ACCESS_TOKEN,
    )

# Logging.
logger = SimpleConsoleLogger(to_log_level(DJANGO_LOG_LEVEL))

# LINE Bot handler.
line_bot_api = LineBotApi(channel_access_token = LINE_ACCESS_TOKEN)
webhook_handler = WebhookHandler(channel_secret = LINE_CHANNEL_SECRET)

def callback(request):
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    request_body = request.body.decode('utf-8')

    logger.debug('Raw request body is:')
    logger.debug(request_body)

    try:
        webhook_handler.handle(request_body, signature)
    except InvalidSignatureError as e:
        logger.error('Invalid signature error has occurred.')
        logger.error('error message => ' + e.message)
        raise

    return HttpResponse('OK', status = 200)

@webhook_handler.add(FollowEvent)
def handle_follow(event):
    logger.info('FolloEvent has occurred. (user_id => ' + event.source.user_id + ')')

    try:
        friend = LineFriend(user_id = event.source.user_id)
        friend.save()

        logger.debug('Registerred ' + event.source.user_id + ' as line friend.')

    except Exception as e:
        logger.error('EXECUTE FAILURE!!')
        logger.error('Failed to register ' + event.source.user_id + '.')
        logger.error('Caused by:')
        logger.error(e.args)

    carouselColumns = []
    for category in Category.objects.all():
        carouselColumns.append(
            CarouselColumn(
                thumbnail_image_url = 'https://poa-web.herokuapp.com/static/santa.png',
                text = category.name,
                actions = [
                    PostbackAction(
                        label = '選択',
                        data = 'mode=after_follow&category_code=' + str(category.code)
                    ),
                ]
            )
        )

    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text = 'はじめまして、' + LINE_BOT_NAME + 'です。'),
            TextSendMessage(text = 'カテゴリを選択してください。'),
            TemplateSendMessage(
                alt_text = 'カテゴリを選択してください。',
                template = CarouselTemplate(
                    columns = carouselColumns
                ),
            ),
        ]
    )

@webhook_handler.add(UnfollowEvent)
def handle_unfollow(event):
    logger.info('UnfolloEvent has occurred. (user_id => ' + event.source.user_id + ')')

    try:
        friend = LineFriend.objects.filter(user_id = event.source.user_id)
        friend.delete()

        logger.debug('Deleted ' + event.source.user_id + '.')

    except Exception as e:
        logger.error('EXECUTE FAILURE!!')
        logger.error('Failed to delete ' + event.source.user_id + '.')
        logger.error('Caused by:')
        logger.error(e.args)

@webhook_handler.add(PostbackEvent)
def handle_postback(event):
    logger.info('PostbackEvent has occurred.')

    query_string = urllib.parse.parse_qs(event.postback.data)

    if 'mode' in query_string:
        mode = query_string['mode'][0]

        logger.debug('mode as ' + mode + ".")

        if mode == 'after_follow':
            handle_postback_after_follow(event, query_string)

def handle_postback_after_follow(event, query_string):
    try:
        favorite_category_code = query_string['category_code'][0]
        favorite_category = Category.objects.get(code = favorite_category_code)

        friend = LineFriend.objects.get(user_id = event.source.user_id)
        friend.favorite_category_code = favorite_category
        friend.save()

    except Exception as e:
        logger.error(e.args)

    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text = 'カテゴリを登録しました。'),
            TextSendMessage(text = '「' + LINE_BOT_NAME + '」と呼んでみてください。'),
        ]
    )

@webhook_handler.add(MessageEvent, message = TextMessage)
def handle_text_message(event):
    friend = LineFriend.objects.get(user_id = event.source.user_id)

    if event.message.text == LINE_BOT_NAME:
        handle_text_message_call_me(event)
    else:
        if bool(friend.asking):
            handle_text_message_advice(event)
        else:
            logger.error('雑談バージョン')

def handle_text_message_call_me(event):
    try:
        friend = LineFriend.objects.get(user_id = event.source.user_id)
        friend.asking = True
        friend.save()
    except Exception as e:
        logger.error(e.args)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = '気分を入力してください。')
    )

def handle_text_message_advice(event):
    try:
        friend = LineFriend.objects.get(user_id = event.source.user_id)
        friend.asking = False
        friend.save()
    except Exception as e:
        logger.error(e.args)

    linebot_service = LinebotService()
    advices = linebot_service.advice(event.message.text, friend.favorite_category_code.code)

    actions = []
    for advice in advices:
        actions.append(
            MessageTemplateAction(
                label = advice,
                text = advice,
            )
        )


    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text = 'Buttons template',
            template = ButtonsTemplate(
                title = 'Menu',
                text = 'Please select.',
                actions = actions,
            )
        )
    )
