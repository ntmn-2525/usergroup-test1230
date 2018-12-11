from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

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
from linebot.exceptions import InvalidSignatureError

from .forms import TestForm
from .services import LinebotService
from data_storage.models import (
    Category,
    LineFriend,
)

import os
import logging
import urllib

try:
    from poa_web.settings_local import LINE_CHANNEL_SECRET
    from poa_web.settings_local import LINE_ACCESS_TOKEN
except ImportError:
    LINE_CHANNEL_SECRET = ''
    LINE_ACCESS_TOKEN = ''
    
BOT_NAME = 'Chabo'

logger = logging.getLogger('poa_web')
line_bot_api = LineBotApi(channel_access_token = os.getenv('LINE_ACCESS_TOKEN', LINE_ACCESS_TOKEN))
webhook_handler = WebhookHandler(channel_secret = os.getenv('LINE_CHANNEL_SECRET', LINE_CHANNEL_SECRET))

def callback(request):
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    request_body = request.body.decode('utf-8')

    logger.fatal('request body => ' + request_body)

    try:
        webhook_handler.handle(request_body, signature)
    except InvalidSignatureError as e:
        logger.error('Invalid signature error has occurred.')
        logger.error('error message => ' + e.message)
        raise

    return HttpResponse('OK', status = 200)

@webhook_handler.add(FollowEvent)
def handle_follow(event):
    try:
        friend = LineFriend(user_id = event.source.user_id)
        friend.save()
    except Exception as e:
        logger.error(e.args)

    carouselColumns = []
    for category in Category.objects.all():
        carouselColumns.append(
            CarouselColumn(
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
            TextSendMessage(text = 'はじめまして、' + BOT_NAME + 'です。'),
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
    try:
        friend = LineFriend.objects.filter(user_id = event.source.user_id)
        friend.delete()
    except Exception as e:
        logger.error(e.args)

@webhook_handler.add(PostbackEvent)
def handle_postback(event):
    query_string = urllib.parse.parse_qs(event.postback.data)

    if 'mode' in query_string:
        mode = query_string['mode'][0]

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
            TextSendMessage(text = '「' + BOT_NAME + '」と呼んでみてください。'),
        ]
    )

@webhook_handler.add(MessageEvent, message = TextMessage)
def handle_text_message(event):
    friend = LineFriend.objects.get(user_id = event.source.user_id)

    if event.message.text == BOT_NAME:
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

    logger.error(friend)
    logger.error(friend.favorite_category_code)
    logger.error(friend.favorite_category_code.code)

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
                thumbnail_image = '',
                title = 'Menu',
                text = 'Please select.',
                actions = actions,
            )
        )
    )

class TestView(TemplateView):
    def __init__(self):
        self.params = {}

    def get(self, request):
        return self.post(request)

    def post(self, request):
        self.params['testForm'] = TestForm()
        return render(request, 'line_bot/test.html', self.params)
