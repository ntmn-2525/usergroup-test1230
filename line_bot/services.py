# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 09:38:41 2018

@author: urano
"""

from data_storage.models import Advice
from google.cloud import language #emotionAPI

import random

import nnabla as nn #nnabla
import nnabla.functions as F #nnabla
import nnabla.parametric_functions as PF #nnabla
from nnabla.utils.data_iterator import data_iterator_csv_dataset #nnabla
        
        
IS_DUMMY_ANALYZE_SENTIMENT = False
IS_DUMMY_ASSUME_BY_NNABLA = True

class LinebotService():

    def advice(self, message, category_code):
        sentiment_score = self.__analyze_sentiment(message)
        advice_labels = self.__assume_by_nnabla(sentiment_score, category_code)

        advices = []
        for label in advice_labels:
            adjusted_category_code = int(label * 10)
            adjusted_content_code = int(label * 1000) - adjusted_category_code * 100
            advice_result = Advice.objects.filter(category_code = adjusted_category_code, code = adjusted_content_code)[0]
            advices.append(advice_result.sentence)

        return advices

    def __analyze_sentiment(self, message):
        if IS_DUMMY_ANALYZE_SENTIMENT:
            return round(random.uniform(-1.0, 1.0), 1)

        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
        #
        # [START]：感情分析ロジック
        # ロジックを有効にする場合は、「IS_DUMMY_ANALYZE_SENTIMENT」をFalseへ変更
        #
        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/

        # クライアントのインスタンス化
        language_client = language.Client()

        # 分析したいテキスト
        text = message

        # リクエストのデータを格納
        document = language_client.document_from_text(text)
        # 感情分析のレスポンスを格納
        response = document.analyze_sentiment()
        # ドキュメント全体の感情が含まれたオブジェクト
        sentiment = response.sentiment
        # 各段落の感情が含まれたオブジェクトのリスト
        sentences = response.sentences

        # 全体の感情スコアを出力
        print('Text全体')
        print('Text: {}'.format(text))
        print('Sentiment: {}'.format(sentiment.score))
        #print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))

        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
        #
        # [END]：感情分析ロジック
        #
        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/

        
        
    def __assume_by_nnabla(self, sentiment_score, category_code):
        if IS_DUMMY_ASSUME_BY_NNABLA:
            options = []
            while True:
                for i in range(3):
                    options.append(float(random.randint(1, 5) / 10) + float(random.randint(1, 30) / 1000))
                if len(options) == len(set(options)):
                    break
                options.clear
            return options

        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
        #
        # [START]：AIによる推測ロジック
        # ロジックを有効にする場合は、「IS_DUMMY_ASSUME_BY_NNABLA」をFalseへ変更
        #
        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/


        def network(x, test=False):
            # Input:x -> 3

            # Affine -> 100
            h = PF.affine(x, (100,), name='Affine')
            # BatchNormalization
            h = PF.batch_normalization(h, (1,), 0.9, 0.0001, not test, name='BatchNormalization')
            # LeakyReLU
            h = F.leaky_relu(h)

            # Affine_2
            h = PF.affine(h, (100,), name='Affine_2')
            # BatchNormalization_2
            h = PF.batch_normalization(h, (1,), 0.9, 0.0001, not test, name='BatchNormalization_2')
            # LeakyReLU_2
            h = F.leaky_relu(h)

            # Affine_3
            h = PF.affine(h, (100,), name='Affine_3')
            # BatchNormalization_3
            h = PF.batch_normalization(h, (1,), 0.9, 0.0001, not test, name='BatchNormalization_3')
            # LeakyReLU_3
            h = F.leaky_relu(h)

            # Affine_4 -> 131
            h = PF.affine(h, (131,), name='Affine_4')
            # BatchNormalization_4
            h = PF.batch_normalization(h, (1,), 0.9, 0.0001, not test, name='BatchNormalization_4')

            # Softmax
            h = F.softmax(h)
            return h



        # load parameters
        nn.load_parameters('./result_train.nnp')

        # Prepare input variable
        x=nn.Variable((1,3))

        # Let input data to x.d
        #test_data = ["0.5","0.1","1.1050143"]
        #x.d = test_data
        data = [sentiment_score, category_code, "1.1050143"]
        x.d = data
        #x.data.zero()

        # Build network for inference
        y = network(x, test=True)

        # Execute inference
        y.forward()
        #"%.10f" % 
        print(y.d)

        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
        #
        # [END]：AIによる推測ロジック
        #
        #_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/

