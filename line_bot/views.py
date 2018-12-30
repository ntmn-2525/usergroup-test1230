# Standard modules.
import os

# Django modules.
from django.http import (
    HttpResponse,
)

# LINE Bot modules.
from linebot import (
    LineBotApi,
    WebhookParser,
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
    FollowService,
    MessageService,
    PostbackService,
    ServiceMode,
    UnfollowService,
)

from .models import LineSession
import json

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
#line_bot_api = LineBotApi(channel_access_token = LINE_ACCESS_TOKEN)
#webhook_handler = WebhookHandler(channel_secret = LINE_CHANNEL_SECRET)

def callback(request):
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    request_body = request.body.decode('utf-8')

    logger.debug('Raw request body is:')
    logger.debug(request_body)

    line_bot_api = LineBotApi(channel_access_token = LINE_ACCESS_TOKEN)
    webhook_parser = WebhookParser(channel_secret = LINE_CHANNEL_SECRET)

    try:
        events = webhook_parser.parse(request_body, signature)
    except InvalidSignatureError as e:
        raise e

    logger.debug('Parsing events successfully.')

    for event in events:
        session = Session(event).get_session()

        if 'container' in session:
            logger.debug('container is in session.')
            container = session['container']
            container['msgs'] = []
        else:
            logger.debug('container is not in session.')
            container = {
                'mode'      : {
                    'prev'  : ServiceMode.UNDEFINED,
                    'curr'  : ServiceMode.UNDEFINED,
                },
                'msgs'  : [
                ],
                'temp'  : {
                },
            }

        logger.debug('Parsing events successfully.')

        event_type = event.type
        if event_type == 'unfollow':
            service = UnfollowService(event, container)
            session.clear()
        else:
            if event_type == 'message':
                service = MessageService(event, container)
                logger.debug('MessageService::')
            elif event_type == 'postback':
                service = PostbackService(event, container)
            elif event_type == 'follow':
                service = FollowService(event, container)
            elif event_type == 'join':
                pass
            elif event_type == 'leave':
                pass
            elif event_type == 'beacon':
                pass
            elif event_type == 'accountLink':
                pass
            else:
                return HttpResponse('NG', status = 500)
    
            new_container = service.execute()
            session['container'] = new_container
            line_bot_api.reply_message(event.reply_token, new_container['msgs'])

    return HttpResponse('OK', status = 200)

class Session(object):

    def __init__(self, event):
        user_id = event.source.user_id
        sessions = LineSession.objects.filter(user_id = user_id)

        if sessions.exists():
            session = sessions[0]
        else:
            session = LineSession(user_id = user_id)
            session.save()

        self.__session = session

        decoded_data = session.data.decode('utf-8')
        data_dict = json.dumps(decoded_data)
        self.data = data_dict

    def get_session(self):
        return self.data

    def save(self):
        json_code = json.dumps(self.data)
        encoded_data = json_code.encode('utf-8')

        session = self.__session
        session.data = encoded_data
        session.save()

#@webhook_handler.add(FollowEvent)
#def handle_follow(event):
#
#
#    messages = FollowService(event).execute()
#    line_bot_api.reply_message(event.reply_token, messages)
#    pass
#
#
#
#    logger.info('FolloEvent has occurred. (user_id => ' + event.source.user_id + ')')
#
#
#
#
#    try:
#        friend = LineFriend(user_id = event.source.user_id)
#        friend.save()
#
#        logger.debug('Registerred ' + event.source.user_id + ' as line friend.')
#
#    except Exception as e:
#        logger.error('EXECUTE FAILURE!!')
#        logger.error('Failed to register ' + event.source.user_id + '.')
#        logger.error('Caused by:')
#        logger.error(e.args)
#
#    carouselColumns = []
#    for category in Category.objects.all():
#        carouselColumns.append(
#            CarouselColumn(
#                text = category.name,
#                actions = [
#                    PostbackAction(
#                        label = '選択',
#                        data = 'mode=after_follow&category_code=' + str(category.code)
#                    ),
#                ]
#            )
#        )
#
#    line_bot_api.reply_message(
#        event.reply_token,
#        [
#            TextSendMessage(text = 'はじめまして、' + LINE_BOT_NAME + 'です。'),
#            TextSendMessage(text = 'カテゴリを選択してください。'),
#            TemplateSendMessage(
#                alt_text = 'カテゴリを選択してください。',
#                template = CarouselTemplate(
#                    columns = carouselColumns
#                ),
#            ),
#        ]
#    )
#
#@webhook_handler.add(UnfollowEvent)
#def handle_unfollow(event):
#    logger.info('UnfolloEvent has occurred. (user_id => ' + event.source.user_id + ')')
#
#    try:
#        friend = LineFriend.objects.filter(user_id = event.source.user_id)
#        friend.delete()
#
#        logger.debug('Deleted ' + event.source.user_id + '.')
#
#    except Exception as e:
#        logger.error('EXECUTE FAILURE!!')
#        logger.error('Failed to delete ' + event.source.user_id + '.')
#        logger.error('Caused by:')
#        logger.error(e.args)
#
#@webhook_handler.add(PostbackEvent)
#def handle_postback(event):
#    logger.info('PostbackEvent has occurred.')
#
#    query_string = urllib.parse.parse_qs(event.postback.data)
#
#    if 'mode' in query_string:
#        mode = query_string['mode'][0]
#
#        logger.debug('mode as ' + mode + ".")
#
#        if mode == 'after_follow':
#            handle_postback_after_follow(event, query_string)
#
#def handle_postback_after_follow(event, query_string):
#    try:
#        favorite_category_code = query_string['category_code'][0]
#        favorite_category = Category.objects.get(code = favorite_category_code)
#
#        friend = LineFriend.objects.get(user_id = event.source.user_id)
#        friend.favorite_category_code = favorite_category
#        friend.save()
#
#    except Exception as e:
#        logger.error(e.args)
#
#    line_bot_api.reply_message(
#        event.reply_token,
#        [
#            TextSendMessage(text = 'カテゴリを登録しました。'),
#            TextSendMessage(text = '「' + LINE_BOT_NAME + '」と呼んでみてください。'),
#        ]
#    )
#
#@webhook_handler.add(MessageEvent, message = TextMessage)
#def handle_text_message(event):
#    friend = LineFriend.objects.get(user_id = event.source.user_id)
#
#    if event.message.text == LINE_BOT_NAME:
#        handle_text_message_call_me(event)
#    else:
#        if bool(friend.asking):
#            handle_text_message_advice(event)
#        else:
#            logger.error('雑談バージョン')
#
#def handle_text_message_call_me(event):
#    try:
#        friend = LineFriend.objects.get(user_id = event.source.user_id)
#        friend.asking = True
#        friend.save()
#    except Exception as e:
#        logger.error(e.args)
#
#    line_bot_api.reply_message(
#        event.reply_token,
#        TextSendMessage(text = '気分を入力してください。')
#    )
#
#def handle_text_message_advice(event):
#    try:
#        friend = LineFriend.objects.get(user_id = event.source.user_id)
#        friend.asking = False
#        friend.save()
#    except Exception as e:
#        logger.error(e.args)
#
#    linebot_service = LinebotService()
#    advices = linebot_service.advice(event.message.text, friend.favorite_category_code.code)
#
#    actions = []
#    for advice in advices:
#        actions.append(
#            MessageTemplateAction(
#                label = advice,
#                text = advice,
#            )
#        )
#
#
#    line_bot_api.reply_message(
#        event.reply_token,
#        TemplateSendMessage(
#            alt_text = 'Buttons template',
#            template = ButtonsTemplate(
#                title = 'Menu',
#                text = 'Please select.',
#                actions = actions,
#            )
#        )
#    )
