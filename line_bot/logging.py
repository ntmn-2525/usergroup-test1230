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

def to_log_level(level_name):
    if level_name == 'DEBUG':
        return LogLevel.DEBUG
    elif level_name == 'INFO':
        return LogLevel.INFO
    elif level_name == 'ERROR':
        return LogLevel.ERROR
    elif level_name == 'FATAL':
        return LogLevel.FATAL
    else:
        return LogLevel.UNDEF

def to_log_name(level):
    if LogLevel.DEBUG == level:
        return "DEBUG"
    elif LogLevel.INFO == level:
        return "INFO"
    elif LogLevel.ERROR == level:
        return "ERROR"
    elif LogLevel.FATAL == level:
        return "FATAL"
    else:
        return "UNDEF"

class LogLevel(IntEnum):
    DEBUG = 1
    INFO  = auto()
    ERROR = auto()
    FATAL = auto()
    UNDEF = auto()

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
