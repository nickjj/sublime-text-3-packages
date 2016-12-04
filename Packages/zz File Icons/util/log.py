# -*- coding: utf-8 -*-

DEBUG = False
WARN = 'Please restart Sublime Text for the applied icons to take effect ...'


def log(*args):
    text = []

    for arg in args:
        text.append(str(arg))
    print(''.join(text))


def message(*args):
    if DEBUG:
        log('File Icons: ', *args)


def value(*args):
    if DEBUG:
        log('        >>> ', *args)


def done():
    if DEBUG:
        log('File Icons: ', 'Finished')
        log('***\n')


def separator():
    if DEBUG:
        log('\n***')


def warning():
    log('\n***')
    log('File Icons: ', WARN)
    log('***\n')
