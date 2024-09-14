# -*- coding: utf-8 -*-
r"""
This file configures kivy settings like window height,width,logger path,etc.
Settings and logs are stored in the following path for windows:
C:\Users\<UserName>\AppData\Local\<Project Name>
"""

__PROJECT__ = 'Calculator'
__SCREENS__ = ['Standard', 'Quadratic', 'Settings']

import os
import configparser
import logging
from tblib import pickling_support

main_folder_path = os.path.join(os.path.expanduser(r'~\AppData\Local'), __PROJECT__)
log_dir = os.path.join(main_folder_path, 'logs')

if not os.path.exists(main_folder_path):
    os.makedirs(main_folder_path)

os.environ['KIVY_HOME'] = main_folder_path

from kivy.logger import Logger
from kivy.config import Config

pickling_support.install()
logging.getLogger().setLevel(logging.INFO)

MIN_HEIGHT = 470
MIN_WIDTH = 320

while True:
    try:
        theme_value = int(Config.get('app', 'theme_value'))
        screen = str(Config.get('app', 'current_screen'))

        # Perform settings checks before proceeding
        if screen not in __SCREENS__:
            raise ValueError
        if theme_value not in [0, 1, 2]:
            raise ValueError

        Logger.info('kivy_config: ' + ' Kivy successfully configured')
        break
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError, TypeError):
        Config.set('kivy', 'log_name', f'%H-%M-%S_{__PROJECT__.lower()}_%y-%m-%d_%_.txt')
        Config.set('kivy', 'window_icon',
                   rf'{os.getcwd() if __name__ == "__main__" else __path__[0]}\icon\icon.png')
        Config.set('kivy', 'exit_on_escape', '0')
        Config.set('kivy', 'log_maxfiles', '25')
        Config.set('graphics', 'height', '500')
        Config.set('graphics', 'width', '320')
        Config.set('graphics', 'minimum_height', MIN_HEIGHT)
        Config.set('graphics', 'minimum_width', MIN_WIDTH)
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        # Add extra app settings
        try:
            Config.add_section('app')
        except configparser.DuplicateSectionError:
            pass
        Config.set('app', 'theme_value', '1')
        Config.set('app', 'current_screen', 'Standard')
        Config.write()
        continue

