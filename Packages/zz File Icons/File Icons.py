# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import os
import re

from .util import log
from .util.env import *
from .util.tpl import PATCH_TEMPLATE

PKG = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
SETTINGS = 'File Icons.sublime-settings'
SETTINGS_CHANGED = False
THEME_EXTENSION = '.sublime-theme'
UUID = '9ebcce78-4cac-4089-8bd7-d551c634b064'

CURRENT = {
    'color': '',
    'color_on_hover': '',
    'color_on_select': '',
    'force_override': '',
    'opacity': '',
    'opacity_on_hover': '',
    'opacity_on_select': '',
    'size': '',
    'aliases': ''
}

DIST = 'dist'
PATCHES = 'zpatches'
THEMES = '*' + THEME_EXTENSION
SUPPORTED_THEMES = '.st-file-icons'
ALIASES = 'languages'


def get_settings():
    return sublime.load_settings(SETTINGS)


def get_dest_path():
    return os.path.join(sublime.packages_path(), PKG, DIST, PATCHES)


def get_aliases_path():
    return os.path.join(sublime.packages_path(), PKG, DIST, ALIASES)


def get_installed():
    log.message('Getting installed themes')

    installed_res = sublime.find_resources(THEMES)
    installed_themes = {}

    for ires in installed_res:
        installed_themes.setdefault(os.path.basename(os.path.dirname(ires)),
                                    []).append(os.path.basename(ires))

    if PATCHES in installed_themes:
        del installed_themes[PATCHES]

    log.value(installed_themes)

    return installed_themes


def get_supported():
    log.message('Getting supported themes')

    installed_res = sublime.find_resources(THEMES)
    supported_res = sublime.find_resources(SUPPORTED_THEMES)

    supported = {}

    for sres in supported_res:
        pkg = os.path.basename(os.path.dirname(sres))

        for ires in installed_res:
            if pkg in ires:
                supported.setdefault(pkg, []).append(os.path.basename(ires))

    log.value(supported)

    return supported


def is_supported(pkg, supported):
    if pkg in supported:
        log.message(pkg, ' is supported')
        return True

    log.message(pkg, ' isn\'t supported')
    return False


def is_ignored():
    preferences = sublime.load_settings('Preferences.sublime-settings')

    if PKG in preferences.get('ignored_packages'):
        return True

    return False


def get_colors():
    log.message('Getting colors of the icons')

    colors = []
    settings = get_settings()
    pattern = re.compile('#([A-Fa-f0-9]{6})')
    options = ['color', 'color_on_hover', 'color_on_select']

    if settings.get('color'):
        for opt in options:
            color = settings.get(opt)

            if pattern.match(color):
                hex_color = color.lstrip('#')
                rgb_color = [
                    int(hex_color[i: i + 2], 16) for i in (0, 2, 4)
                ]

                color = ', '.join(str(e) for e in rgb_color)

                log.value('`', opt, '`: ', '[', color, ']')

                colors.append('\n    "layer0.tint": [' + color + '],')
            else:
                colors.append('')

    return colors


def patch(themes, colors):
    log.message('Patching the themes')

    dest = get_dest_path()

    theme_dest = ''
    theme_name = ''

    color = colors[0]
    color_on_hover = colors[1]
    color_on_select = colors[2]

    size = CURRENT['size']

    opacity = CURRENT['opacity']
    opacity_on_hover = CURRENT['opacity_on_hover']
    opacity_on_select = CURRENT['opacity_on_select']

    for theme in themes:
        theme_dest = os.path.join(dest, theme)
        theme_name = os.path.splitext(theme)[0]

        with open(theme_dest, 'w') as t:
            t.write(PATCH_TEMPLATE % {
                'name': theme_name,
                'color': color,
                'color_on_hover': color_on_hover,
                'color_on_select': color_on_select,
                'size': size,
                'opacity': opacity,
                'opacity_on_hover': opacity_on_hover,
                'opacity_on_select': opacity_on_select
            })
            t.close()


def activate():
    log.message('Activating the icons')

    dest = get_dest_path()

    colors = get_colors()
    icons = os.path.join(dest, 'icons')
    multi = os.path.join(dest, 'multi')
    single = os.path.join(dest, 'single')

    installed = get_installed()
    supported = get_supported()
    force_override = CURRENT['force_override']
    themes = []

    for pkg in installed:
        tset = installed[pkg]

        if force_override:
            themes.extend(tset)
        elif not is_supported(pkg, supported):
                themes.extend(tset)

    if not SETTINGS_CHANGED:
        tmp = themes
        for theme in tmp:
            theme_path = os.path.join(dest, theme)

            if os.path.isfile(theme_path):
                themes = [t for t in themes if t != theme]

    if colors:
        if os.path.isdir(single):
            log.message('Activating the single color mode')
            os.rename(icons, multi)
            os.rename(single, icons)
        else:
            log.message('The single color mode is already activated')
    else:
        if os.path.isdir(multi):
            log.message('Activating the multi color mode')
            os.rename(icons, single)
            os.rename(multi, icons)
        else:
            log.message('The multi color mode is already activated')

        colors = ['', '', '']

    if not force_override:
        clear_patches(list(set([i for sl in supported.values() for i in sl])))

    if themes:
        patch(themes, colors)
        sublime.set_timeout_async(log.warning, 500)
    else:
        log.message('Themes are already patched')

    log.done()


def aliases():
    log.message('Checking aliases')

    aliases = get_aliases_path()

    for alias in os.listdir(aliases):
        path = os.path.join(aliases, alias)

        if os.path.isfile(path):
            name, ext = os.path.splitext(path)

            if CURRENT['aliases'] and ext == '.disabled-tmLanguage':
                os.rename(path, path.replace('.disabled-', '.'))

            if not CURRENT['aliases'] and ext == '.tmLanguage':
                os.rename(path, path.replace('.tmLanguage',
                                             '.disabled-tmLanguage'))


def clear_patches(patches):
    log.message('Clearing patches')

    dest = get_dest_path()

    for patch in patches:
        path = os.path.join(dest, patch)

        try:
            if os.path.isfile(path):
                os.remove(path)
        except Exception as e:
            print(e)


def clear_all():
    patches = []
    dest = get_dest_path()

    for patch in os.listdir(dest):
        path = os.path.join(dest, patch)

        if os.path.isfile(path):
            name, ext = os.path.splitext(path)
            if ext == '.sublime-theme':
                patches.append(path)

    clear_patches(patches)


def on_change():
    global CURRENT
    global SETTINGS_CHANGED

    settings = get_settings()

    if not is_ignored():
        log.DEBUG = settings.get('debug')

        log.separator()
        log.message('The settings are changed')

        for k in CURRENT.keys():
            if CURRENT[k] != settings.get(k):
                SETTINGS_CHANGED = True
                log.message('`', k, '` is changed')
                CURRENT[k] = settings.get(k)

        if SETTINGS_CHANGED:
            log.message('Current settings')
            log.value(CURRENT)
            aliases()
            activate()
            SETTINGS_CHANGED = False
        else:
            log.done()


def add_listener():
    get_settings().add_on_change(UUID, on_change)


def remove_listener():
    get_settings().clear_on_change(UUID)


def init():
    global CURRENT

    settings = get_settings()

    log.DEBUG = settings.get('debug')

    log.separator()
    log.message('Initializing')
    log.message('Getting the settings')

    for k in CURRENT.keys():
        CURRENT[k] = settings.get(k)

    log.value(CURRENT)


class FileIconsCleanUpCommand(sublime_plugin.WindowCommand):
    def run(self):
        clear_all()
        activate()


def plugin_loaded():
    init()
    aliases()
    activate()
    add_listener()


def plugin_unloaded():
    remove_listener()
    clear_all()
