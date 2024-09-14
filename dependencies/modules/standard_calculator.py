# -*- coding: utf-8 -*-
"""standard_calculator"""

from kivy.clock import Clock
from kivy.metrics import Metrics
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from dependencies.modules.simplemathematics import eval_expression, add_commas, remove_extra_zeroes


class StandardCalculator(Screen):
    """Subclass for Standard Calculator"""

    main_text = StringProperty('0')
    side_text = StringProperty('')
    num_1 = ''
    operator = '0'
    num_2 = ''

    theme = 'dark'

    # To match widget's background color with background color of
    # the screen
    canvas_color = ListProperty([.137, .137, .137, 1])
    button_color = ListProperty([.2, .2, .2, 1])
    operator_color = ListProperty([.15, .15, .15, 1])
    equal_color = ListProperty([1, .5, 0, .5])
    text_color = ListProperty([1, 1, 1, 1])
    # For less bright color for side text
    side_text_color = ListProperty([1, 1, 1, .5])
    trash_color = ListProperty([0, 0, 0, 0])

    RightAlignedTextButton = None

    widget_ids: list[str] = []  # Hover able widget ids
    '''
    This list tells if the color of a widget is changed on mouse 
    hover when no widget's color is changed 'it is [False] else it 
    contains [True,widget ids,original button color] respectively.
    '''
    widget_changed_on_hover: list[bool] | list[bool, str, list[float]] = [False]

    # Position and coordinates of all the widgets that are
    # hover-able
    x_coordinate_widget_min: list[float] = []
    x_coordinate_widget_max: list[float] = []
    y_coordinate_widget_max: list[float] = []
    y_coordinate_widget_min: list[float] = []

    # Color of button before pressing it
    button_color_before_press: list[float] = []
    # Tells if a button is pressed
    button_press: bool = False
    # Button whose color has been changed on press
    button_pressed: object = None
    '''
    In some cases the button press function is executed before mouse 
    hover but color changing functions only work as intentional if 
    mouse hover function is executed before button press function.
    '''
    press_not_executed: bool = False

    current_mouse_pos: tuple = (0, 0)

    # Status of the dropdown menu
    status_dd: bool = False
    # To check whether history widget is added or not
    history_status: bool = True
    # To disable and enable history delete button
    trash_status: bool = BooleanProperty()

    # Number of history buttons
    no_of_history_buttons: int = 0
    list_of_history: list[str] = []
    topmost_history_button_visible: int = 1
    # List of all the history buttons that are not visible when
    # scrolled
    list_of_history_not_visible: list[str] = []

    animation_status: str = 'stopped'
    animation_event: Clock = None

    def on_pre_enter(self, *args, **kwargs):
        """Function executed before entering the Standard screen"""
        Window.bind(on_resize=self.on_resize,
                    mouse_pos=self.on_mouse_position,
                    on_cursor_leave=lambda *arg:
                    self.on_mouse_position(0, (-1, -1)))

        self.on_resize()

        if self.theme == 'dark':
            self.canvas_color = [.13, .13, .13, 1]
            self.button_color = [.2, .2, .2, 1]
            self.text_color = [1, 1, 1, 1]
            self.side_text_color = [1, 1, 1, .6]
            self.equal_color = [1, .5, 0, .5]
            self.operator_color = [.15, .15, .15, 1]
        elif self.theme == 'light':
            self.canvas_color = [.95, .95, .95, 1]
            self.button_color = [1, 1, 1, 1]
            self.text_color = [0, 0, 0, 1]
            self.side_text_color = [0, 0, 0, .4]
            self.equal_color = [1, .5, 0, 1]
            self.operator_color = [.9, .9, .9, 1]
        self.ids.standard_dd_button.background_color = self.button_color

        if self.history_status:
            self.ids.history_label.color = self.text_color
            if self.no_of_history_buttons == 0:
                self.ids.no_history.color = self.text_color
            else:
                # To change the color of all existing history
                # buttons
                for no in range(1, self.no_of_history_buttons + 1):
                    self.ids[f'history_button_{no}'].background_color = self.canvas_color
                    self.ids[f'history_button_{no}'].color = self.text_color

        self.on_mouse_position(0, Window.mouse_pos)

    def on_pre_leave(self, *args, **kwargs):
        """Function executed before leaving the screen"""
        Window.unbind(on_resize=self.on_resize,
                      mouse_pos=self.on_mouse_position,
                      on_cursor_leave=lambda *arg:
                      self.on_mouse_position(0, (-1, -1)))

        '''
        This function is called to ensure that no button's color is 
        left changed on hover
        '''
        self.on_mouse_position(0, (-1, -1))

    def on_enter(self, *args, **kwargs):
        """Function executed on entering the Quadratic screen"""
        self.on_resize(0, 0, 0)

    def on_resize(self, *args):  # noqa
        """
        Function executed on resize of window when screen is
        Standard
        """
        if not args:
            args = (1, Window.width, Window.height)
        if args[1] < 700 * Metrics.dp:
            if self.history_status:
                self.ids.main_box_layout.remove_widget(self.ids.history_main_grid)
                self.history_status = False
            if args[0] == 0:
                self.on_resize()
        else:
            if not self.history_status:
                grid = GridLayout(rows=3, size_hint=(None, 1), width=340 * Metrics.dp)
                self.ids['history_main_grid'] = grid
                label = Label(size_hint=(1, None), height=60 * Metrics.dp,
                              padding_x=10 * Metrics.dp, text='History',
                              font_size=18 * Metrics.dp, halign='left',
                              valign='middle', color=self.text_color)
                label.bind(size=label.setter('text_size'))
                self.ids['history_label'] = label
                scroll_view = ScrollView(always_overscroll=False, bar_width=0)
                self.ids['history_scroll_view'] = scroll_view
                grid2 = GridLayout(cols=1, size_hint_y=None)
                grid2.bind(minimum_height=grid2.setter('height'))
                self.ids['history_grid'] = grid2
                grid3 = GridLayout(cols=2, size_hint=(1, None),
                                   height=
                                   65 * Metrics.dp if Metrics.dpi < 100 else 55 * Metrics.dp)
                label2 = Label(size_hint=(1, None),
                               height=65 * Metrics.dp if Metrics.dpi < 100 else 55 * Metrics.dp)
                button = Button(size_hint=(None, None),
                                width=65 * Metrics.dp if Metrics.dpi < 100 else 55 * Metrics.dp,
                                height=65 * Metrics.dp if Metrics.dpi < 100 else 55 * Metrics.dp,
                                background_normal=r'dependencies/icons/trash.ico',
                                background_disabled_normal='',
                                background_down=r'dependencies/icons/trash_pressed.ico',
                                background_color=self.trash_color,
                                disabled=self.trash_status, always_release=True)
                button.bind(on_release=self.on_release_trash_button,
                            on_press=self.on_press_trash_button)
                self.ids['button_24'] = button
                grid.add_widget(label)
                grid.add_widget(scroll_view)
                scroll_view.add_widget(grid2)
                grid.add_widget(grid3)
                grid3.add_widget(label2)
                grid3.add_widget(button)
                self.ids.main_box_layout.add_widget(grid)

                # In order to add the history buttons
                if self.no_of_history_buttons > 0:
                    for num in range(1, self.no_of_history_buttons + 1):
                        button2 = \
                            self.RightAlignedTextButton(text=self.list_of_history[num - 1],
                                                        background_color=self.canvas_color,
                                                        color=self.text_color, markup=True)
                        button2.bind(on_press=self.on_press_history_button,
                                     on_release=self.on_release_history_button)
                        button2.font_size = 14 * Metrics.sp
                        self.ids[f'history_button_{num}'] = button2
                        lbl_for_spacing = Label(size_hint=(None, 1), width=5 * Metrics.dp)
                        layout = BoxLayout(orientation='horizontal',
                                           size_hint=(1, None), height=80 * Metrics.dp)
                        layout.add_widget(button2)
                        layout.add_widget(lbl_for_spacing)
                        self.ids.history_grid.add_widget(layout)
                        self.ids.button_24.disabled = False
                        self.ids.button_24.background_color = [1, 1, 1, 1]
                # In order to add the num history label if there are
                # num history buttons
                elif self.no_of_history_buttons == 0:
                    label3 = Label(size_hint=(1, None), height=20 * Metrics.dp,
                                   padding_x=10 * Metrics.dp, text='There is no history yet',
                                   font_size=17 * Metrics.dp, halign='left',
                                   valign='middle', color=self.text_color)
                    label3.bind(size=label3.setter('text_size'))
                    self.ids[f'no_history'] = label3
                    self.ids.history_grid.add_widget(label3)
                self.history_status = True

        # It scrolls to the top most button in the history while
        # resizing the window
        if self.history_status and self.topmost_history_button_visible != 1:
            self.ids.history_scroll_view.scroll_to(self.ids.history_button_1,
                                                   animate=False, padding=0)
            self.topmost_history_button_visible = 1
        self.on_mouse_position(0, self.current_mouse_pos)
        self.on_mouse_position(0, self.current_mouse_pos)

    def on_mouse_position(self, instance, position):
        """
        Function executed whenever the mouse is moved on the screen
        Standard inside the app window
        """
        self.current_mouse_pos = position
        # Instance can be 1 to get position of widgets instantly
        # or 0 to get position of widgets in the next possible frame
        if instance == 1:
            self.position_of_widgets()
        else:
            Clock.schedule_once(lambda *arg: self.position_of_widgets())
        for widget_number, widget_id in enumerate(self.widget_ids):
            # Skip button_1 and button_2 if dropdown menu is not
            # open
            if widget_number in [1, 2] and not self.status_dd:
                continue
            # Skip button_24/trash button if it is disabled,it
            # would not be added in the list if the graph is
            # not visible
            if widget_number == 24 and self.trash_status:
                continue

            # If the current mouse position is inside any of the
            # buttons in the list
            if self.x_coordinate_widget_min[widget_number] < position[0] < (
                    self.x_coordinate_widget_max[widget_number]) and (
                    self.y_coordinate_widget_min[widget_number]) < position[1] < (
                    self.y_coordinate_widget_max[widget_number]):

                if not self.widget_changed_on_hover[0]:
                    # If the dropdown menu is open it will only
                    # change the color of buttons on hover in the
                    # dropdown menu
                    if self.status_dd and widget_number not in [1, 2]:
                        continue

                    widget_color = self.ids[widget_id].background_color

                    # Changes the color of on the button on based
                    # of the original color
                    if self.theme == 'dark':
                        # For history buttons/canvas color
                        if widget_color[0] == 0.1:
                            hover_color = 0.02
                        # For buttons with icons/[1,1,1,1]
                        elif widget_color[0] == 1 and widget_id in ['button_24', 'button_0']:
                            hover_color = -0.2
                        # For equals to button/equal color
                        elif widget_color[0] == 1:
                            hover_color = -0.08
                        # For normal buttons/button color
                        elif widget_color[0] == 0.2:
                            hover_color = -0.02
                        # For operator buttons/operator color
                        else:
                            hover_color = 0.02
                    else:  # For light theme
                        # For history buttons/canvas color
                        if widget_color[0] == 0.95:
                            hover_color = -0.05
                        # For buttons with icons/[1,1,1,1]
                        elif widget_color[0] == 1 and widget_id in ['button_24', 'button_0']:
                            hover_color = -0.2
                        # For equals to button/ equal color
                        elif widget_color[0] == 1 and widget_id == 'button_22':
                            hover_color = -0.05
                        # For normal buttons/button color
                        elif widget_color[0] == 1:
                            hover_color = -0.025
                        # For operator buttons/operator color
                        else:
                            hover_color = 0.02

                    self.widget_changed_on_hover = [True, widget_id, widget_color.copy()]

                    self.ids[widget_id].background_color = \
                        [widget_color[index] + hover_color for index in range(3)]
                    break
            else:
                # To change back to original color of the button
                if self.widget_changed_on_hover[0] and (
                        self.widget_changed_on_hover[1] == widget_id or
                        self.widget_changed_on_hover[1] in self.list_of_history_not_visible) \
                        and not self.button_press:
                    self.ids[self.widget_changed_on_hover[1]].background_color = \
                        self.widget_changed_on_hover[2]
                    self.widget_changed_on_hover = [False]
                    break

            if self.press_not_executed:
                self.change_color_on_press(self.button_pressed)
                self.press_not_executed = False

    def position_of_widgets(self):
        """
        Get the position,co-ordinates and size of all the buttons
        present on the current screen with their respective ids.
        """
        self.x_coordinate_widget_min.clear()
        self.x_coordinate_widget_max.clear()
        self.y_coordinate_widget_min.clear()
        self.y_coordinate_widget_max.clear()
        self.widget_ids.clear()

        for button_number in range(24 + 1 if self.history_status else 23 + 1):
            if button_number == 1:
                self.x_coordinate_widget_min.append(self.x_coordinate_widget_min[0])
                self.x_coordinate_widget_max.append(self.x_coordinate_widget_min[0] + 220
                                                    * Metrics.dp)
                self.y_coordinate_widget_max.append(self.y_coordinate_widget_min[0] - 78
                                                    * Metrics.dp)
                self.y_coordinate_widget_min.append(self.y_coordinate_widget_min[0] - 113
                                                    * Metrics.dp)
                self.widget_ids.append('button_1')
            elif button_number == 2:
                self.x_coordinate_widget_min.append(self.x_coordinate_widget_min[0])
                self.x_coordinate_widget_max.append(self.x_coordinate_widget_min[0] + 220
                                                    * Metrics.dp)
                self.y_coordinate_widget_max.append(self.y_coordinate_widget_min[0] - 133
                                                    * Metrics.dp)
                self.y_coordinate_widget_min.append(self.y_coordinate_widget_min[0] - 173
                                                    * Metrics.dp)
                self.widget_ids.append('button_2')
            else:
                widget_name = f'button_{button_number}'
                widget_pos_0 = self.ids[widget_name].pos[0]
                widget_pos_1 = self.ids[widget_name].pos[1]
                widget_size_0 = self.ids[widget_name].size[0]
                widget_size_1 = self.ids[widget_name].size[1]
                self.x_coordinate_widget_min.append(widget_pos_0)
                self.x_coordinate_widget_max.append(widget_pos_0 + widget_size_0)
                self.y_coordinate_widget_max.append(widget_pos_1 + widget_size_1)
                self.y_coordinate_widget_min.append(widget_pos_1)
                self.widget_ids.append(widget_name)

    def change_color_on_press(self, button):
        """
        Function changes button's color on press according to the
        theme
        """
        self.button_pressed = button
        # To ensure the button's color has been changed on hover
        if self.widget_changed_on_hover[0] and \
                button == eval(f'self.ids.{self.widget_changed_on_hover[1]}'):
            self.button_press = True
            button_color = button.background_color
            if self.theme == 'dark':
                # For normal buttons/button color
                if round(button_color[0], 4) == 0.18:
                    press_color = -0.025
                # For operator buttons/operator color
                elif round(button_color[0], 4) == 0.17:
                    press_color = 0.03
                # For equals to button/ equal color
                else:
                    press_color = 0.04
            else:
                # For normal buttons/button color
                if button_color[0] == 0.975:
                    press_color = -0.07
                # For operator buttons/operator color
                elif button_color[0] == .92:
                    press_color = 0.07
                # For equals to button/ equal color
                else:
                    press_color = -0.06
            self.button_color_before_press = button_color.copy()
            button.background_color = [button_color[index] + press_color
                                       for index in range(3)]
        else:
            self.press_not_executed = True

    def change_color_on_release(self, button):
        """Function changes the color of the button to the color it was before pressing it"""
        if self.button_press:
            self.button_press = False
            button.background_color = self.button_color_before_press
            self.on_mouse_position(0, self.current_mouse_pos)
            self.on_mouse_position(0, self.current_mouse_pos)
        self.press_not_executed = False

    def add_history_button(self):
        """Adds a history button whenever called"""
        self.no_of_history_buttons += 1
        text = \
            f'[color=8e8e8e]{self.get_side_text()} =[/color]\n[b]{add_commas(self.main_text)}[/b]'
        self.list_of_history.insert(0, text)
        self.trash_status = False
        self.trash_color = [1, 1, 1, 1]

        if self.history_status:

            button = \
                self.RightAlignedTextButton(text='',
                                            background_color=self.canvas_color,
                                            color=self.text_color, markup=True)
            button.bind(on_press=self.on_press_history_button,
                        on_release=self.on_release_history_button)
            button.font_size = 14 * Metrics.sp
            self.ids[f'history_button_{self.no_of_history_buttons}'] = button
            lbl_for_spacing = Label(size_hint=(None, 1), width=5 * Metrics.dp)
            layout = BoxLayout(orientation='horizontal',
                               size_hint=(1, None), height=80 * Metrics.dp)
            layout.add_widget(button)
            layout.add_widget(lbl_for_spacing)
            self.ids.history_grid.add_widget(layout)
            self.ids.button_24.disabled = False
            self.ids.button_24.background_color = [1, 1, 1, 1]
            for num in range(2, self.no_of_history_buttons + 1):
                self.ids[f'history_button_{num}'].text = self.list_of_history[num - 1]

            # It will scroll to the top most button if the user has
            # scrolled towards the bottom and a history button is
            # added
            if self.topmost_history_button_visible not in (1, 0):
                self.topmost_history_button_visible = 1
                self.ids.history_scroll_view.scroll_to(self.ids.history_button_1,
                                                       animate=False, padding=0)
            self.ids.history_button_1.text = ''
            # For removing num history label
            if self.no_of_history_buttons == 1:
                self.ids.history_grid.remove_widget(self.ids.no_history)
                self.ids.history_button_1.text = self.list_of_history[0]
            # For animation of text of history button
            # Animation is only applied to history_button_1
            else:
                # To stop the animation if the user is clicking
                # fast
                if self.animation_status == 'running':
                    self.animation_event.cancel()
                    self.ids.history_button_1.text = self.list_of_history[0]
                    self.animation_status = 'stopped'
                    return
                self.animation_event = Clock.schedule_once(self.history_button_animation, 0.3)
                self.animation_status = 'running'

    def history_button_animation(self, *args):  # noqa
        """Animates the text of the first button"""
        self.ids.history_button_1.text = self.list_of_history[0]
        # Animation changes opacity of text of history button from
        # 0 to 1 in 0.3 seconds
        self.ids.history_button_1.opacity = 0
        animation = Animation(opacity=1, duration=0.3)
        animation.start(self.ids.history_button_1)
        self.animation_status = 'stopped'

    def on_press_history_button(self, button):  # noqa
        """Function executed on press of a history button"""
        self.button_press = True

    def on_release_history_button(self, button):
        """Function executed on release of a history button"""
        widget_text = button.text
        side_text = ''
        for i in range(14, widget_text.index('[/color]')):
            side_text += widget_text[i]
        main_text = ''
        for i in range(widget_text.index('[b]') + 3, widget_text.index('[/b]')):
            main_text += widget_text[i]
        operators = {'+': '+', '-': '-', '×': '*', '÷': '/'}
        self.side_text = side_text
        self.main_text = main_text
        self.num_1 = side_text.split(' ')[0]
        self.operator = operators[side_text.split(' ')[2]]
        self.num_2 = side_text.split(' ')[4]
        self.button_press = False
        self.on_mouse_position(0, self.current_mouse_pos)
        self.on_mouse_position(0, self.current_mouse_pos)

    def on_press_trash_button(self, *args):  # noqa
        """Function executed on press of history delete button"""
        self.button_press = True
        self.no_of_history_buttons = 0
        self.ids.button_24.background_normal = r'dependencies/icons/trash_animate.ico'

    def on_release_trash_button(self, *args):  # noqa
        """
        Function used to give the animation effect to the history
        delete button on release
        """
        Clock.schedule_once(self.on_release_trash_button_main)

    def on_release_trash_button_main(self, *args):  # noqa
        """Function executed on release of history delete button"""
        self.ids.button_24.background_normal = r'dependencies/icons/trash.ico'
        self.ids.history_grid.clear_widgets()
        self.list_of_history.clear()
        label = Label(size_hint=(1, None), height=20 * Metrics.dp,
                      padding_x=10 * Metrics.dp, text='There is no history yet',
                      font_size=17 * Metrics.dp, halign='left',
                      valign='middle', color=self.text_color)
        label.bind(size=label.setter('text_size'))
        self.ids['no_history'] = label
        self.ids.history_grid.add_widget(label)
        self.list_of_history_not_visible.clear()
        self.button_press = False
        self.widget_changed_on_hover = [False]
        self.trash_status = True
        self.trash_color = [0, 0, 0, 0]
        self.ids.button_24.disabled = True
        self.ids.button_24.background_color = [0, 0, 0, 0]
        self.on_mouse_position(0, self.current_mouse_pos)
        self.on_mouse_position(0, self.current_mouse_pos)

    def get_side_text(self) -> str:
        """Calculates the text for the expression label"""
        temp_num_1 = \
            add_commas(remove_extra_zeroes(
                str(eval(self.num_1)))) if ',' not in self.num_1 else self.num_1
        temp_num_2 = ''
        if self.num_2 != '':
            temp_num_2 = \
                add_commas(remove_extra_zeroes(
                    str(eval(self.num_2)))) if ',' not in self.num_2 else self.num_2
        text = f'{temp_num_1}  {self.operator}  {temp_num_2}'
        if self.operator == '*':
            text = f'{temp_num_1}  ×  {temp_num_2}'
        elif self.operator == '/':
            text = f'{temp_num_1}  ÷  {temp_num_2}'
        elif self.operator == '**':
            if temp_num_2 == '2':
                text = f'{temp_num_1}[size=18][sup] 2[/sup][/size]'
            elif temp_num_2 == '0.5':
                text = f'√{temp_num_1}'

        return text

    def on_num_click(self, widget):
        """Executed when a number is clicked except for 0"""
        if '=' in self.side_text or self.main_text in ['Not Defined', 'Invalid Input',
                                                       'Infinity']:
            self.clear()
        # to remove 0
        if self.main_text == '0':
            self.main_text = ''
        # for max 16 digit input
        if len(self.main_text) < 16 and 'e' not in self.main_text:
            self.main_text += widget.text

    def on_zero_click(self):
        """Executed when 0 is clicked"""
        if '=' in self.side_text or self.main_text in ['Not Defined', 'Invalid Input',
                                                       'Infinity']:
            self.clear()
        if self.main_text == '0':
            return
        # for max 16 digit input
        if len(self.main_text) < 16 and 'e' not in self.main_text:
            self.main_text += '0'

    def on_decimal_click(self):
        """Executed when . is clicked"""
        if self.main_text in ['Not Defined', 'Invalid Input', 'Infinity']:
            self.clear()
        # To check if the given number is an integer or already a
        # float
        try:
            int(self.main_text)
        except ValueError:
            return
        if len(self.main_text) < 15:
            main_text = self.main_text
            main_text += '.'
            if '=' in self.side_text:
                self.clear()
            self.main_text = main_text

    def plus_minus(self):
        """Executed when ± is clicked"""
        if self.main_text in ['Not Defined', 'Invalid Input', 'Infinity']:
            self.clear()
        if eval(self.main_text) == 0:
            return
        if '-' in self.main_text:
            main_text = ''.join([i for i in self.main_text if i != '-'])
        else:
            main_text = f'-{self.main_text}'
        if '=' in self.side_text:
            self.clear()
        self.main_text = main_text

    def clear(self):
        """Executed when C is clicked"""
        self.main_text = '0'
        self.side_text = ''
        self.num_1 = ''
        self.operator = '0'
        self.num_2 = ''

    def backspace(self):
        """Executed when ⌫ is clicked"""
        if self.main_text in ['Not Defined', 'Invalid Input', 'Infinity']:
            self.clear()
        if self.main_text == '0':
            pass
        elif 'e' in self.main_text:
            pass
        else:
            main_text = self.main_text
            if '=' in self.side_text:
                self.clear()
            main_text = main_text[:-1]
            try:
                float(main_text)
            except ValueError:
                main_text = '0'
            self.main_text = main_text

    def addition(self):
        """Executed when + is clicked"""
        if self.main_text in ['Not Defined', 'Invalid Input', 'Infinity']:
            self.clear()
            return
        # For operation on ans
        if '=' in self.side_text:
            self.num_1 = self.main_text
            self.operator = '+'
            self.num_2 = ''
            self.main_text = '0'
            self.side_text = self.get_side_text()
        # To add on clicking
        elif self.operator == '+':
            if self.side_text == self.get_side_text():
                self.equal_to()
                self.addition()
        # To change predefined operator
        elif self.operator in '-/*%':
            self.operator = '+'
            self.side_text = self.get_side_text()
        else:
            self.num_1 = self.main_text
            self.operator = '+'
            self.main_text = '0'
            self.side_text = self.get_side_text()

    def subtraction(self):
        """Executed when - is clicked"""
        if self.main_text in ['Not Defined', 'Invalid Input', 'Infinity']:
            self.clear()
            return
        # For operations on ans
        if '=' in self.side_text:
            self.num_1 = self.main_text
            self.operator = '-'
            self.num_2 = ''
            self.main_text = '0'
            self.side_text = self.get_side_text()
        # To subtract on clicking
        elif self.operator == '-':
            if self.side_text == self.get_side_text():
                self.equal_to()
                self.subtraction()
        # To change predefined operator
        elif self.operator in '+/*%':
            self.operator = '-'
            self.side_text = self.get_side_text()
        else:
            self.num_1 = self.main_text
            self.operator = '-'
            self.main_text = '0'
            self.side_text = self.get_side_text()

    def multiplication(self):
        """Executed when × is clicked"""
        if self.main_text in ['Not Defined', 'Invalid Input', 'Infinity']:
            self.clear()
            return
        # For operations on ans
        if '=' in self.side_text:
            self.num_1 = self.main_text
            self.operator = '*'
            self.num_2 = ''
            self.main_text = '0'
            self.side_text = self.get_side_text()
        # To multiply on clicking
        elif self.operator == '*':
            if self.side_text == self.get_side_text():
                self.equal_to()
                self.multiplication()
        # To change predefined operator
        elif self.operator in '-/+%':
            self.operator = '*'
            self.side_text = self.get_side_text()
        else:
            self.num_1 = self.main_text
            self.operator = '*'
            self.main_text = '0'
            self.side_text = self.get_side_text()

    def division(self):
        """Executed when ÷ is clicked"""
        if self.main_text in ['Not Defined', 'Invalid Input', 'Infinity']:
            self.clear()
            return
        # For operations on ans
        if '=' in self.side_text:
            self.num_1 = self.main_text
            self.operator = '/'
            self.num_2 = ''
            self.main_text = '0'
            self.side_text = self.get_side_text()
        # To divide on click
        elif self.operator == '/':
            if self.side_text == self.get_side_text():
                if eval(self.main_text) == 0:
                    pass
                else:
                    self.equal_to()
                    self.division()
        # To change predefined operator
        elif self.operator in '-*+%':
            self.operator = '/'
            self.side_text = self.get_side_text()
        else:
            self.num_1 = self.main_text
            self.operator = '/'
            self.main_text = '0'
            self.side_text = self.get_side_text()

    def sqr_rt(self):
        """Executed when √x is clicked"""
        if self.main_text in ['Not Defined', 'Invalid Input', 'Infinity']:
            self.clear()
            return
        if self.operator != '0' and '=' not in self.side_text:
            main_text = eval_expression(self.main_text, '**', '0.5')
            if not main_text == 'Invalid Input':
                self.main_text = main_text
            return
        self.num_1 = self.main_text
        self.operator = '**'
        self.num_2 = '0.5'
        self.main_text = eval_expression(self.main_text, '**', '0.5')
        self.side_text = f'{self.get_side_text()} ='
        self.num_1 = ''
        self.operator = '0'
        self.num_2 = ''

    def sqr(self):
        """Executed when x^2 is clicked"""
        if self.main_text in ['Not Defined', 'Invalid Input', 'Infinity']:
            self.clear()
            return
        if self.operator != '0' and '=' not in self.side_text:
            main_text = eval_expression(self.main_text, '**', '2')
            if not main_text == 'Infinity':
                self.main_text = main_text
            return
        self.num_1 = self.main_text
        self.operator = '**'
        self.num_2 = '2'
        self.main_text = eval_expression(self.main_text, '**', '2')
        self.side_text = f'{self.get_side_text()} ='
        self.num_1 = ''
        self.operator = '0'
        self.num_2 = ''

    def equal_to(self):
        """Executed when = is clicked"""
        if self.main_text in ['Not Defined', 'Invalid Input', 'Infinity']:
            self.clear()
            return
        if not self.num_1 == '':
            if '=' in self.side_text:
                self.num_1 = self.main_text
            else:
                self.num_2 = self.main_text
            self.main_text = eval_expression(self.num_1, self.operator, self.num_2)
            self.side_text = f'{self.get_side_text()} ='
            if self.main_text not in ['Not Defined', 'Invalid Input', 'Infinity']:
                self.add_history_button()
