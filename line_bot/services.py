# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 09:38:41 2018

@author: urano
"""

from abc import abstractmethod

from line_bot.models import (
    LineFriend,
)

# Local modules.
from .logging import (
    to_log_level,
    SimpleConsoleLogger,
)

# Logging.
logger = SimpleConsoleLogger(to_log_level('DEBUG'))

from linebot.models import (
#    ButtonsTemplate,
#    CarouselColumn,
#    CarouselTemplate,
    ConfirmTemplate,
#    MessageTemplateAction,
    PostbackAction,
    TemplateSendMessage,
#    TextMessage,
    TextSendMessage,
)


#IS_DUMMY_ANALYZE_SENTIMENT = True
#IS_DUMMY_ASSUME_BY_NNABLA = True

from enum import(
    auto,
    Enum,
)

class ServiceMode(Enum):
    UNDEFINED           = -1
    CHATTING            = auto()
    NICKNAME            = auto()
    NICKNAME_CONFIRM    = auto()

class LinebotService(object):

    def __init__(self, event, container):
        self.event = event
        self.container = container

    def execute(self):
        self.init()
        self.process()
        self.destroy()
        return self.container

    def init(self):
        pass

    def destroy(self):
        pass

    @abstractmethod
    def process(self):
        raise NotImplementedError()

    def set_next_mode(self, next_mode):
        self.container['mode']['prev'] = self.container['mode']['curr']
        self.container['mode']['curr'] = next_mode

    def set_messages(self, msgs):
        self.container['msgs'] = msgs

class LinebotSubService(LinebotService):
    pass

class FollowService(LinebotService):

    def process(self):
        user_id = self.event.source.user_id
        line_friends = LineFriend.objects.filter(user_id = user_id)

        if line_friends.exists():
            line_friend = line_friends[0]
        else:
            line_friend = LineFriend(user_id = user_id)
            line_friend.save()

        msgs = []
        msgs.append(TextSendMessage(text = 'お友だち登録ありがとう！'))
        msgs.append(TextSendMessage(text = 'これからあなたの生活をサポートするよ。いつでも声をかけてね。'))
        msgs.append(TextSendMessage(text = 'そうだ！'))
        msgs.append(TextSendMessage(text = 'ぼくにニックネームをつけてみて！'))
        self.set_messages(msgs)

        self.set_next_mode(ServiceMode.NICKNAME)

class UnfollowService(LinebotService):

    def process(self):
        user_id = self.event.source.user_id
        line_friend = LineFriend.objects.get(user_id = user_id)
        line_friend.delete()

        self.set_messages([])

        self.set_next_mode(ServiceMode.UNDEFINED)

class MessageService(LinebotService):

    def process(self):
        logger.debug('MessageService::1')
        
        curr_mode = self.container['mode']['curr']

        logger.debug('MessageService::2 ' + str(curr_mode))
        
        if curr_mode == ServiceMode.NICKNAME:
            sub_service = NicknameSubService(self.event, self.container)

        self.container = sub_service.execute()

class NicknameSubService(LinebotSubService):

    def process(self):
        logger.debug('NicknameSubService::1')
        
        bot_name = self.event.message.text

        logger.debug('NicknameSubService::2')
        
        msgs = []
        msgs.append(
            TemplateSendMessage(
                alt_text = '',
                template = ConfirmTemplate(
                    text = 'これから「' + bot_name + '」と呼んでくれる？',
                    actions = [
                        PostbackAction(label = 'yes', data = 'yes'),
                        PostbackAction(label = 'no', data = 'no'),
                    ]
                )
            )
        )
        self.set_messages(msgs)

        logger.debug('NicknameSubService::3')
        
        self.set_next_mode(ServiceMode.NICKNAME_CONFIRM)

class PostbackService(LinebotService):

    def process(self):
        curr_mode = self.container['mode']['curr']

        if curr_mode == ServiceMode.NICKNAME_CONFIRM:
            sub_service = NicknameConfirmSubService(self.event, self.container)

        self.container = sub_service.execute()

class NicknameConfirmSubService(LinebotSubService):

    def process(self):
        message = self.event.postback.data

        if message == 'yes':
            user_id = self.event.source.user_id
            bot_name = self.container['temp']['bot_name']
            del self.container['temp']['bot_name']
    
            line_friend = LineFriend.objects.get(user_id = user_id)
            line_friend.bot_name = bot_name
            line_friend.save()

            msgs = []
            msgs.append(TextSendMessage(text = 'これから「' + bot_name + '」と呼んでね！'))
            self.set_messages(msgs)
    
            self.set_next_mode(ServiceMode.CHATTING)

        else:
            msgs = []
            msgs.append(TextSendMessage(text = 'もう一度ニックネームを入力してくれる？'))
            self.set_messages(msgs)

            self.set_next_mode(ServiceMode.NICKNAME)

class LinebotException(Exception):
    pass

#        columns = []
#        for category in Category.objects.all():
#            columns.append(
#                CarouselColumn(
#                    text = category.name,
#                    actions = [
#                        PostbackAction(
#                            label = '',
#                            data = 'mode=after_follow&category_code=' + str(category.code)
#                        ),
#                    ]
#                )
#            )
#
#        msgs.append(TemplateSendMessage(alt_text = '', template = CarouselTemplate(columns = columns)))



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



























#class LinebotService2():
#
#    def advice(self, message, category_code):
#        sentiment_score = self.__analyze_sentiment(message)
#        advice_labels = self.__assume_by_nnabla(sentiment_score, category_code)
#
#        advices = []
#        for label in advice_labels:
#            adjusted_category_code = int(label * 10)
#            adjusted_content_code = int(label * 1000) - adjusted_category_code * 100
#            advice_result = Advice.objects.filter(category_code = adjusted_category_code, code = adjusted_content_code)[0]
#            advices.append(advice_result.sentence)
#
#        return advices
#
#    def __analyze_sentiment(self, message):
#        if IS_DUMMY_ANALYZE_SENTIMENT:
#            return round(random.uniform(-1.0, 1.0), 1)
#
#        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
#        #
#        # [START]：感情分析ロジック
#        # ロジックを有効にする場合は、「IS_DUMMY_ANALYZE_SENTIMENT」をFalseへ変更
#        #
#        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
#
#
#
#        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
#        #
#        # [END]：感情分析ロジック
#        #
#        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
#
#    def __assume_by_nnabla(self, sentiment_score, category_code):
#        if IS_DUMMY_ASSUME_BY_NNABLA:
#            options = []
#            while True:
#                for i in range(3):
#                    options.append(float(random.randint(1, 5) / 10) + float(random.randint(1, 30) / 1000))
#                if len(options) == len(set(options)):
#                    break
#                options.clear
#            return options
#
#        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
#        #
#        # [START]：AIによる推測ロジック
#        # ロジックを有効にする場合は、「IS_DUMMY_ASSUME_BY_NNABLA」をFalseへ変更
#        #
#        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
#
#
#
#        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
#        #
#        # [END]：AIによる推測ロジック
#        #
#        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
#
