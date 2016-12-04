# -*- coding: utf-8 -*-

import os
import sublime
import sublime_plugin
import textwrap


__version__ = '2.2.0'
__pc_name__ = 'zz File Icons'


def list2string(obj):
    return '.'.join([str(x) for x in obj])


def format_version(module, attr, call=False):
    try:
        if call:
            version = getattr(module, attr)()
        else:
            version = getattr(module, attr)
    except Exception as e:
        print(e)
        version = 'Version could not be acquired!'

    if not isinstance(version, str):
        version = list2string(version)
    return version


def is_installed_by_package_control():
    settings = sublime.load_settings('Package Control.sublime-settings')
    return str(__pc_name__ in set(settings.get('installed_packages', [])))


def get_installed_themes():
    installed_res = sublime.find_resources('*.sublime-theme')
    installed_themes = {}

    for ires in installed_res:
        installed_themes.setdefault(os.path.basename(os.path.dirname(ires)),
                                    []).append(os.path.basename(ires))

    if 'zpatches' in installed_themes:
        del installed_themes['zpatches']

    return installed_themes


def get_current_theme():
    return sublime.load_settings('Preferences.sublime-settings').get('theme')


class FileIconsEnvCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        info = {}

        info['platform'] = sublime.platform()
        info['version'] = sublime.version()
        info['file_icons_version'] = __version__
        info['pc_install'] = is_installed_by_package_control()
        info['current_theme'] = get_current_theme()
        info['installed_themes'] = get_installed_themes()

        msg = textwrap.dedent(
            '''\
            - File Icons: %(file_icons_version)s
            - Sublime Text: %(version)s
            - Platform: %(platform)s
            - Package Control: %(pc_install)s
            - Current Theme: %(current_theme)s
            - Installed Themes: %(installed_themes)s
            ''' % info
        )

        sublime.message_dialog(
            msg + '\nInfo has been copied to the clipboard.'
        )
        sublime.set_clipboard(msg)
