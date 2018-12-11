# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 14:42:02 2018

@author: Yusaku Urano
"""

from django import forms

class TestForm(forms.Form):
    comment = forms.CharField(
            label = 'comment',
            required = True,
            max_length = 140,
            widget = forms.TextInput()
            )

    category = forms.ChoiceField(
            label = 'category',
            choices = [
                    ('0.1', 'ショッピング'),
                    ('0.2', '旅行'),
                    ('0.3', 'グルメ'),
                    ('0.4', 'スポーツ'),
                    ('0.5', '音楽')
                    ]
            )
