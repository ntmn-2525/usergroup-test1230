# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 19:19:08 2018

@author: urano
"""

import sys

from enum import (
    auto,
    IntEnum,
)

class LogLevel(IntEnum):
    DEBUG = 1
    INFO  = auto()
    ERROR = auto()
    FATAL = auto()
    UNDEF = auto()

    def to_value(self, level_name):
        if level_name == 'DEBUG':
            return self.DEBUG
        elif level_name == 'INFO':
            return self.INFO
        elif level_name == 'ERROR':
            return self.ERROR
        elif level_name == 'FATAL':
            return self.FATAL
        else:
            return self.UNDEF

class SimpleConsoleLogger():
    def __init__(self, level = LogLevel.UNDEF):
        self.setLevel(level)

    def setLevel(self, level):
        self.__level = level

    def debug(self, message):
        if self.__level <= LogLevel.DEBUG:
            self.__output(message, 'DEBUG')

    def info(self, message):
        if self.__level <= LogLevel.INFO:
            self.__output(message, 'INFO')

    def error(self, message):
        if self.__level <= LogLevel.ERROR:
            self.__output(message, 'ERROR')

    def fatal(self, message):
        if self.__level <= LogLevel.FATAL:
            self.__output(message, 'FATAL')

    def __output(self, message, level_name):
        sys.stderr.write('[{0: <5}] {1}\n'.format(level_name, message))
