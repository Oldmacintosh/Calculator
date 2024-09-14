# -*- coding: utf-8 -*-
"""Main execution Script for the application"""

__author__ = 'Oldmacintosh'
__version__ = 'v2.5.3'
__date__ = 'September 2024'
__DEBUG__ = False

import configparser
import multiprocessing
import os
import pickle
import sys
import darkdetect
import pymsgbox
from tblib import pickling_support

if __name__ == "__main__":
    multiprocessing.freeze_support()
    if not __DEBUG__:
        os.environ['KIVY_NO_CONSOLELOG'] = '1'
    try:
        from dependencies.modules import kivy_config
        from dependencies.modules.standard_calculator import StandardCalculator
        from dependencies.modules.quadratic_calculator import QuadraticCalculator
        from dependencies.modules.settings_calculator import SettingsCalculator
        from kivy.app import App
        from kivy.metrics import Metrics
        from kivy.lang import Builder
        from kivy.clock import Clock
        from kivy import Config
        from kivy.core.window import Window
        from kivy.uix.screenmanager import Screen, ScreenManager
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput

        pickling_support.install()
        MAIN_FOLDER_PATH = kivy_config.main_folder_path
        LOGGING_PATH = kivy_config.log_dir
        SCREEN = kivy_config.screen
        THEME_VALUE = kivy_config.theme_value

        theme = ['light', 'dark', 'dark' if darkdetect.isDark() else 'light'][THEME_VALUE]


        class RightAlignedTextButton(Button):
            """
            Normal Button except text is aligned to the right for
            this button
            """


        class LabelLikeTextInput(TextInput):
            """
            It is a text input that can be used as normal label which
            has selectable text
            """


        class EmptyScreen(Screen):
            """
            The Application loads in to this screen first and then
            transitions to the necessary screen
            """

            def __init__(self, **kw):
                super().__init__(**kw)
                Window.bind(on_resize=self.on_resize, on_key_down=self.on_key_down,
                            on_request_close=lambda *args: self.on_request_close())

            @staticmethod
            def on_key_down(*args):
                """
                Function executed whenever a keyboard key is pressed
                on any screen
                """
                if args[4] in [['ctrl', 'shift'], ['shift', 'ctrl']] and args[3] == 'l':
                    raise InterruptedError('This is a demo of exception handling')

            @staticmethod
            def on_resize(*args):
                """
                Updates the window height and width variables
                irrespective of the current screen
                """
                Config.set('graphics', 'height', int(args[2] / Metrics.dp))
                Config.set('graphics', 'width', int(args[1] / Metrics.dp))
                Config.write()

            @staticmethod
            def on_request_close():
                """
                Updates the settings config file whenever the
                app is closed
                """
                try:
                    Config.add_section('app')
                except configparser.DuplicateSectionError:
                    pass
                Config.set('app', 'theme_value', THEME_VALUE)
                Config.set('app', 'current_screen', SCREEN)
                Config.write()


        class Standard(StandardCalculator):
            """Main Class for the Standard Calculator"""
            theme = theme

            class RightAlignedTextButton(RightAlignedTextButton):
                """..."""

            @staticmethod
            def update_screen():
                """
                Updates the SCREEN variable to Standard on pre enter
                """
                global SCREEN
                SCREEN = 'Standard'


        class Quadratic(QuadraticCalculator):
            """Main Class for the Quadratic Calculator"""
            theme = theme

            class LabelLikeTextInput(LabelLikeTextInput):
                """..."""

            @staticmethod
            def update_screen():
                """
                Updates the SCREEN variable to Quadratic on pre enter
                """
                global SCREEN
                SCREEN = 'Quadratic'


        class _Settings(SettingsCalculator):
            """Main Class for the Settings Calculator"""
            theme = theme
            theme_value = THEME_VALUE
            screen = SCREEN
            version = __version__

            def update_screen(self):
                """
                Update the screen variable inside the class to refer
                back to it on pressing back button
                """
                self.screen = SCREEN

            @staticmethod
            def update_clearcolor(background_color: tuple[float, float, float, float]):
                """Update the background color of the window"""
                Window.clearcolor = background_color

            def change_theme_variables(self, updated_theme: str):
                """To change the theme variables in all classes"""
                global THEME_VALUE, theme
                THEME_VALUE = self.theme_value
                theme = updated_theme
                Standard.theme = updated_theme
                Quadratic.theme = updated_theme
                self.theme = updated_theme


        class Calculator(App):
            """..."""
            if theme == 'dark':
                Window.clearcolor = (.13, .13, .13, 1)
            elif theme == 'light':
                Window.clearcolor = (.95, .95, .95, 1)

            class SM(ScreenManager):
                """Widget to manage all the screens"""

                def __init__(self, **kwargs):
                    super().__init__(**kwargs)
                    Clock.schedule_once(lambda *arg: self.transit_screen())

                def transit_screen(self):
                    """In order to transition to the screen"""
                    self.current = SCREEN

            def build(self):
                """Builds the app and returns the root widget"""
                Builder.load_file(r'dependencies/kv/widgets.kv')
                Builder.load_file(r'dependencies/kv/standard_calculator.kv')
                Builder.load_file(r'dependencies/kv/quadratic_calculator.kv')
                Builder.load_file(r'dependencies/kv/settings_calculator.kv')
                return self.SM()


        Calculator().run()

    except Exception as error:

        from kivy.logger import Logger

        pickle.dumps(sys.exc_info())
        Logger.exception('main: ' + str(error))
        if not __DEBUG__:
            pymsgbox.alert(text=f'''Calculator has crashed due to an unexpected except\nException"{
            error}"''',
                           title='Error', button='OK')
    Window.close()
