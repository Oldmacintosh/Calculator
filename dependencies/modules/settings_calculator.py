# -*- coding: utf-8 -*-
"""settings_calculator"""
import webbrowser
import darkdetect
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty
from kivy.core.window import Window


class SettingsCalculator(Screen):
    """Subclass for Settings"""
    theme = 'dark'
    theme_value = 1

    operator_color = ListProperty([.15, .15, .15, 1])
    text_color = ListProperty([1, 1, 1, 1])

    # Ids of all the widgets that are hover-able
    widget_ids: list[str] = []

    '''
    This list tells if the color of a widget is changed on mouse 
    hover when no widget's color is changed 'it is [False] else it 
    contains [True,widget ids,original button color] respectively.
    '''
    widget_changed_on_hover = [False]

    # Position and co-ordinates of all the widgets that are
    # hover-able
    x_coordinate_widget_min: list[float] = []
    x_coordinate_widget_max: list[float] = []
    y_coordinate_widget_max: list[float] = []
    y_coordinate_widget_min: list[float] = []

    # Tells if a button is pressed
    button_press: bool = False

    current_mouse_pos: tuple = (0, 0)

    # Status of the appearance dropdown menu
    status_appearance_dd = False

    # Radius of the dropdown menu canvas
    radius = ListProperty([(10, 10) for num in range(4)])

    def on_pre_enter(self, *args):
        """Function executed before entering the Settings"""
        Window.bind(mouse_pos=self.on_mouse_position,
                    on_cursor_leave=lambda arg: self.on_mouse_position(arg, (-1, -1)))
        self.change_colors(self.theme)
        self.ids[f'checkbox_{self.theme_value}'].active = True
        self.on_mouse_position(0, Window.mouse_pos)

    def on_pre_leave(self, *args):
        """Function executed before leaving the screen"""
        Window.unbind(mouse_pos=self.on_mouse_position,
                      on_cursor_leave=lambda arg: self.on_mouse_position(arg, (-1, -1)))
        '''
        This function is called to ensure that no button's color is 
        left changed on hover
        '''
        self.on_mouse_position(0, (-1, -1))

    def on_mouse_position(self, instance, position):
        """
        Function executed whenever the mouse is moved on the
        screen Settings inside the app window
        """
        self.current_mouse_pos = position
        # Instance can be 1 to get position of widgets instantly
        # or 0 to get position of widgets in the next possible frame
        if instance == 1:
            self.position_of_widgets()
        else:
            Clock.schedule_once(lambda *arg: self.position_of_widgets())
        for widget_number, widget_id in enumerate(self.widget_ids):

            # If the current mouse position is inside any of the
            # buttons in the list
            if self.x_coordinate_widget_min[widget_number] < position[0] < (
                    self.x_coordinate_widget_max[widget_number]) and (
                    self.y_coordinate_widget_min[widget_number]) < position[1] < (
                    self.y_coordinate_widget_max[widget_number]):

                if not self.widget_changed_on_hover[0]:
                    if self.status_appearance_dd and 'checkbox' not in widget_id:
                        continue
                    if 'checkbox' in widget_id:
                        widget_color = self.ids[widget_id].color
                    else:
                        widget_color = self.ids[widget_id].background_color

                    # Changes the color of on the button on based
                    # of the original color
                    if self.theme == 'dark':
                        # For checkboxes
                        if 'checkbox' in widget_id:
                            hover_color = -0.4
                        # For buttons with icons/[1,1,1,1]
                        elif widget_color[0] == 1 and widget_id in ['button_1', 'button_0']:
                            hover_color = -0.2
                        # For operator buttons/operator color
                        else:
                            hover_color = 0.02
                    else:  # For light theme
                        # For checkboxes
                        if 'checkbox' in widget_id:
                            hover_color = 0.6
                        # For buttons with icons/[1,1,1,1]
                        elif widget_color[0] == 1 and widget_id in ['button_1', 'button_0']:
                            hover_color = -0.4
                        # For operator buttons/operator color
                        else:
                            hover_color = 0.02

                    self.widget_changed_on_hover = [True, widget_id, widget_color.copy()]

                    if 'checkbox' in widget_id:
                        self.ids[widget_id].color = \
                            [widget_color[index] + hover_color for index in range(3)]
                    else:
                        self.ids[widget_id].background_color = \
                            [widget_color[index] + hover_color for index in range(3)]
                    break
            else:
                # To change back to original color of the button
                if self.widget_changed_on_hover[0] and self.widget_changed_on_hover[1] == \
                        widget_id and not self.button_press:

                    if 'checkbox' in widget_id:
                        self.ids[self.widget_changed_on_hover[1]].color = \
                            self.widget_changed_on_hover[2]
                    else:
                        self.ids[self.widget_changed_on_hover[1]].background_color = \
                            self.widget_changed_on_hover[2]
                    self.widget_changed_on_hover = [False]
                    break

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

        for button_number in range(2):
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

    def on_active_checkbox_0(self):
        """Executed on activation of checkbox_0"""
        self.theme_value = 0
        self.theme = 'light'
        self.change_colors(theme='light')
        self.change_theme_variables(updated_theme='light')
        if self.widget_changed_on_hover[0]:
            self.widget_changed_on_hover[2] = self.text_color  # noqa
        self.on_mouse_position(0, (-1, -1))
        self.on_mouse_position(0, Window.mouse_pos)

    def on_active_checkbox_1(self):
        """Executed on activation of checkbox_1"""
        self.theme_value = 1
        self.theme = 'dark'
        self.change_theme_variables(updated_theme='dark')
        self.change_colors(theme='dark')
        if self.widget_changed_on_hover[0]:
            self.widget_changed_on_hover[2] = self.text_color  # noqa
        self.on_mouse_position(0, (-1, -1))
        self.on_mouse_position(0, Window.mouse_pos)

    def on_active_checkbox_2(self):
        """Executed on activation of checkbox_2"""
        self.theme_value = 2
        self.theme = 'dark' if darkdetect.isDark() else 'light'
        self.change_colors(theme=self.theme)
        self.change_theme_variables(updated_theme=self.theme)
        if self.widget_changed_on_hover[0]:
            self.widget_changed_on_hover[2] = self.text_color  # noqa
        self.on_mouse_position(0, (-1, -1))
        self.on_mouse_position(0, Window.mouse_pos)

    @staticmethod
    def update_clearcolor(background_color: tuple[float, float, float, float]):
        """..."""

    def update_screen(self):
        """..."""

    def change_colors(self, theme: str):
        """"
        Updates all the colors of the widgets depending on theme
        """
        if theme == 'dark':
            self.update_clearcolor((.13, .13, .13, 1))
            self.text_color = [1, 1, 1, 1]
            self.operator_color = [.15, .15, .15, 1]
        elif theme == 'light':
            self.update_clearcolor((.95, .95, .95, 1))
            self.text_color = [0, 0, 0, 1]
            self.operator_color = [.9, .9, .9, 1]

    def change_theme_variables(self, updated_theme: str):
        """..."""

    @staticmethod
    def on_ref_press():
        """
        Function executed whenever 'More Info' is pressed inside
        the label
        """
        webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
