# -*- coding: utf-8 -*-
"""quadratic_calculator"""

import threading
from matplotlib import pyplot as plt
from dependencies.modules.kivy_matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.clock import Clock
from kivy.metrics import Metrics
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.progressbar import ProgressBar
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from dependencies.modules.equationsolver import quadratic, linear


class QuadraticCalculator(Screen):
    """Subclass for Quadratic Calculator"""
    # All the label text variables
    main_text = StringProperty('Roots Are:')
    equation_text = StringProperty('')
    discriminant_text = StringProperty('Discriminant:')
    por_text = StringProperty('Product of Roots:')
    sor_text = StringProperty('Sum of Roots:')
    vertex_text = StringProperty('Vertex:')
    coordinates_text = StringProperty('X = 0 , Y = 0')

    # All the theme and background color variables
    theme = 'dark'
    # Background color of the screen
    canvas_color = ListProperty([.13, .13, .13, 1])
    button_color = ListProperty([.2, .2, .2, 1])
    text_color = ListProperty([1, 1, 1, 1])
    # Background color for the DropDown menu buttons in this class
    operator_color = ListProperty([.15, .15, .15, 1])
    input_color_a = ListProperty([1, 1, 1, .5])
    input_color_b = ListProperty([1, 1, 1, .5])
    input_color_c = ListProperty([1, 1, 1, .5])
    trash_color = ListProperty([0, 0, 0, 0])

    LabelLikeTextInput = None

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

    current_mouse_pos = (0, 0)

    status_dd: bool = False
    graph_status: bool = True
    # Tells if the slider is disabled or not
    slider_status: bool = BooleanProperty()
    # Tells if the switch is enabled or not
    switch_status: bool = False
    # Tells if the trash button is disabled  or not
    trash_status: bool = BooleanProperty()
    # They are True if the input is selected else it remains False
    main_input_1_status: bool = False
    main_input_2_status: bool = False
    main_input_3_status: bool = False
    user_plotted_point_status: bool = False

    '''
    It will be True on press of keypad button and False on 
    release and used to change the focus of the text input.
    '''
    keypad_button_press: bool = False

    screen_pre_enter: bool = False
    # Tells weather to remove the graph temporarily while
    # calculating roots
    temp_remove_graph: bool = True

    # Lists in which co-ordinates for plotting the
    # graph are temporarily saved
    x_coordinates: list[float] = []
    y_coordinates: list[float] = []
    # For creating quadrants in the graph
    x_quadrant = [-1e30, 1e30]
    y_quadrant = [0, 0]
    x2_quadrant = [0, 0]
    y2_quadrant = [-1e30, 1e30]

    # Tells the value of slider, it is updated when slider is moved
    slider_value: float = 0.5

    # Co-ordinates of mouse on the graph or None if mouse not on
    # graph
    mouse_move_on_graph_x = None
    mouse_move_on_graph_y = None
    # To identify the user plotted point
    user_plotted_point = None
    user_plotted_point_x: float = 0
    user_plotted_point_y: float = 0
    # Graph button press event
    cid0 = None
    # Graph axes enter event
    cid1 = None
    # Graph figure leave event
    cid2 = None
    # Graph motion notify event
    cid3 = None

    # Coefficients of quadratic equation
    a: float = 0
    b: float = 0
    c: float = 0
    d: float = 0
    root_1: float = 0
    root_2: float = 0
    vertex_x: float = 0
    vertex_y: float = 0

    # Limits of graphs
    # smaller x limit
    x_lim0: float = 0
    x_lim1: float = 0
    y_lim1: float = 0
    # smaller y limit
    y_lim0: float = 0

    # Max value of the progress bar
    graph_total_points: float = 0
    # Distance between two points in the graph
    graph_points_to_be_added: float = 0
    # Starting point for calculating points of the graph
    starting_point: float = 0
    # Ending point for calculating points of the graph
    ending_point: float = 0

    '''
    Tells the current status of the thread for calculating points, 
    it can be [idle , running , stop].
    '''
    thread_status: str = 'idle'
    '''
    Tells the status of completion of the points, 
    it can be [none , incomplete , complete].
    '''
    points_status: str = 'none'

    # The thread for calculating points of graph
    thread_for_points: threading.Thread = None

    # Type of graph plotted , it can be empty or main
    graph_plotted: str = 'empty'

    # Clock scheduled events from thread
    event = None
    event_1 = None
    event_2 = None
    event_3 = None

    def on_pre_enter(self, *args, **kwargs):
        """Function executed before entering the Quadratic screen"""
        self.screen_pre_enter = False

        Window.bind(on_resize=self.on_resize,
                    mouse_pos=self.on_mouse_position,
                    on_cursor_leave=lambda *arg:
                    self.on_mouse_position(0, (-1, -1)),
                    on_touch_down=self.on_touch,
                    on_key_down=self.on_key_down,
                    on_request_close=self.stop_thread)

        # To check which one of the input is selected by the user
        self.ids.a.bind(focus=self.on_focus_a)
        self.ids.b.bind(focus=self.on_focus_b)
        self.ids.c.bind(focus=self.on_focus_c)

        # To check the graph status and add or remove it accordingly
        self.on_resize()
        if self.theme == 'dark':
            self.canvas_color = [.13, .13, .13, 1]
            self.button_color = [.2, .2, .2, 1]
            self.text_color = [1, 1, 1, 1]
            self.input_color_a = [1, 1, 1, .5]
            self.input_color_b = [1, 1, 1, .5]
            self.input_color_c = [1, 1, 1, .5]
            self.operator_color = [.15, .15, .15, 1]
        elif self.theme == 'light':
            self.canvas_color = [.95, .95, .95, 1]
            self.button_color = [1, 1, 1, 1]
            self.text_color = [0, 0, 0, 1]
            self.input_color_a = [0, 0, 0, .6]
            self.input_color_b = [0, 0, 0, .6]
            self.input_color_c = [0, 0, 0, .6]
            self.operator_color = [.9, .9, .9, 1]
        self.ids.quadratic_dd_button.background_color = self.button_color

        if self.graph_status:
            self.ids.coordinates_label.foreground_color = self.text_color
            if not self.thread_status == 'running':
                if self.points_status == 'complete':
                    self.plot_graph('main')
                else:
                    self.solve_equation()

        self.screen_pre_enter = False
        self.on_mouse_position(0, Window.mouse_pos)

    def on_pre_leave(self, *args, **kwargs):
        """Function executed before leaving the screen"""
        Window.unbind(on_resize=self.on_resize,
                      mouse_pos=self.on_mouse_position,
                      on_cursor_leave=lambda *arg:
                      self.on_mouse_position(0, (-1, -1)),
                      on_touch_down=self.on_touch,
                      on_key_down=self.on_key_down,
                      on_request_close=self.stop_thread)

        plt.disconnect(self.cid0)
        plt.disconnect(self.cid1)
        plt.disconnect(self.cid2)
        plt.disconnect(self.cid3)
        Window.set_system_cursor('arrow')

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
        Quadratic
        """
        if not args:
            args = (1, Window.width, Window.height)

        if args[1] < 700 * Metrics.dp:
            if self.graph_status:
                self.stop_thread()
                plt.clf()
                plt.close('all')
                self.ids.main_grid_layout.remove_widget(self.ids.box_graph)
                self.graph_status = False
            if args[0] == 0:
                self.on_resize()
        else:
            if not self.graph_status:
                grid = GridLayout(rows=4)
                self.ids['box_graph'] = grid
                box = BoxLayout()
                self.ids['graph1'] = box
                progress_bar = ProgressBar(size_hint=(.2, None), height=10 * Metrics.dp)
                self.ids['pg'] = progress_bar
                grid2 = GridLayout(size_hint=(1, None),
                                   height=
                                   65 * Metrics.dp if Metrics.dpi < 100 else 55 * Metrics.dp,
                                   cols=3)
                label = self.LabelLikeTextInput(size_hint=(1, 1),
                                                text=self.coordinates_text,
                                                foreground_color=self.text_color)
                self.ids['coordinates_label'] = label
                label1 = Label(size_hint=(None, 1), width=65 * Metrics.dp)
                button = Button(size_hint=(None, 1),
                                width=65 * Metrics.dp if Metrics.dpi < 100 else 55 * Metrics.dp,
                                background_normal=r'dependencies/icons/trash.ico',
                                background_down=r'dependencies/icons/trash_pressed.ico',
                                background_color=self.trash_color,
                                disabled=self.trash_status,
                                allow_stretch=True, always_release=True)
                self.ids['button_16'] = button
                button.bind(on_press=self.on_press_trash_button,
                            on_release=lambda *arg: self.on_release_trash_button())
                grid3 = GridLayout(size_hint=(.1, .1), cols=2)
                slider = Slider(size_hint=(1, .1), min=0.1,
                                max=2, value=self.slider_value,
                                value_track_color=[1, .5, 0, 1],
                                value_track=True,
                                disabled=self.slider_status)
                self.ids['sld'] = slider
                slider.bind(value=lambda *arg: self.on_value_slider())
                switch = Switch(size_hint=(None, 1), width=80 * Metrics.dp,
                                active=self.switch_status)
                self.ids['sld_switch'] = switch
                switch.bind(active=self.on_active_switch)
                grid2.add_widget(label1)
                grid2.add_widget(label)
                grid2.add_widget(button)
                grid.add_widget(box)
                grid.add_widget(progress_bar)
                grid.add_widget(grid2)
                grid3.add_widget(slider)
                grid3.add_widget(switch)
                grid.add_widget(grid3)
                self.ids.main_grid_layout.add_widget(grid)

                self.graph_status = True
                self.temp_remove_graph = False
                '''
                In order to prevent from plotting twice if the 
                graph is added on pre entering the screen
                '''
                if not self.screen_pre_enter:
                    if self.points_status == 'complete':
                        self.plot_graph('main')
                    else:
                        self.solve_equation()
                self.temp_remove_graph = True
        self.on_mouse_position(0, self.current_mouse_pos)
        self.on_mouse_position(0, self.current_mouse_pos)
        if self.graph_status:
            self.ids.coordinates_label.font_size = 0.03 * Window.size[1]

    def on_key_down(self, *args):
        """
        Function executed whenever a keyboard key is pressed on
        Quadratic screen
        """
        # To enable backspace during readonly mode of text input
        if args[1] == 8 and args[2] == 42:
            if self.ids.a.focus and len(self.ids.a.text) == 10:
                self.ids.a.readonly = False
            elif self.ids.b.focus and len(self.ids.b.text) == 10:
                self.ids.b.readonly = False
            elif self.ids.c.focus and len(self.ids.c.text) == 10:
                self.ids.c.readonly = False

    def on_touch(self, *args):
        """
        Function executed whenever a touch is received on Quadratic
        screen
        """
        if self.graph_status:
            sv_size = self.ids.graph1.size
            sv_pos = self.ids.graph1.pos
            scroll_value: float = 0.11

            '''
            If coordinates of scrolling is inside the graph and the 
            button is either 'scrollup'(scrolling to the bottom) or 
            'scrolldown'(scrolling to the top)
            '''
            if sv_pos[0] < args[1].pos[0] < sv_pos[0] + sv_size[0] and \
                    sv_pos[1] < args[1].pos[1] < sv_pos[1] + sv_size[1] \
                    and args[1].button in ['scrollup', 'scrolldown']:

                if self.switch_status:
                    if args[1].button == 'scrolldown' and \
                            self.ids.sld.value < 2:
                        if self.ids.sld.value + scroll_value > 2:
                            self.ids.sld.value += 2 - self.ids.sld.value
                        else:
                            self.ids.sld.value += scroll_value

                    elif args[1].button == 'scrollup' and \
                            self.ids.sld.value > 0.1:
                        if self.ids.sld.value - scroll_value < 0.1:
                            self.ids.sld.value -= self.ids.sld.value - 0.1
                        else:
                            self.ids.sld.value -= scroll_value

                    self.on_mouse_position(1, self.current_mouse_pos)
                    self.on_mouse_position(1, self.current_mouse_pos)

    def on_mouse_position(self, instance, position):
        """
        Function executed whenever the mouse is moved on the screen
        Quadratic inside the app window
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
            # Skip button_16/trash button if it is disabled
            if self.graph_status and widget_number == 16 and self.trash_status:
                # When mouse is over the trash button, and
                # it is disabled through the keyboard
                if self.widget_changed_on_hover[0] and self.widget_changed_on_hover[1] == (
                        'button_16'):
                    self.widget_changed_on_hover = [False]
                continue

            # If the current mouse position is inside any of the
            # buttons in the list
            if self.x_coordinate_widget_min[widget_number] < position[0] < (
                    self.x_coordinate_widget_max[widget_number]) and (
                    self.y_coordinate_widget_min[widget_number]) < position[1] < (
                    self.y_coordinate_widget_max[widget_number]):

                if not self.widget_changed_on_hover[0] and self.thread_status != 'running':
                    # If the dropdown menu is open it will only
                    # change the color of buttons on hover in the
                    # dropdown menu
                    if self.status_dd and widget_number not in [1, 2]:
                        continue

                    if widget_id in ['a', 'b', 'c']:
                        if eval(f'''self.main_input_{["a", "b", "c"].index(widget_id) + 1
                        }_status'''):
                            continue
                        widget_color = eval(f'self.input_color_{widget_id}')
                    else:
                        widget_color = self.ids[widget_id].background_color

                    # Changes the color of on the button on based
                    # of the original color
                    if self.theme == 'dark':
                        # For text inputs
                        if widget_id in ['a', 'b', 'c']:
                            hover_color = 0.2
                        # For history buttons/canvas color
                        elif widget_color[0] == 0.1:
                            hover_color = 0.02
                        # For buttons with icons/[1,1,1,1]
                        elif widget_color[0] == 1 and widget_id in ['button_16', 'button_0']:
                            hover_color = -0.2
                        # For normal buttons/button color
                        elif widget_color[0] == 0.2:
                            hover_color = -0.02
                        # For operator buttons/operator color
                        else:
                            hover_color = 0.02
                    else:  # For light theme
                        # For text inputs
                        if widget_id in ['a', 'b', 'c']:
                            hover_color = 0.15
                        # For history buttons/canvas color
                        elif widget_color[0] == 0.95:
                            hover_color = -0.05
                        # For buttons with icons/[1,1,1,1]
                        elif widget_color[0] == 1 and widget_id in ['button_16', 'button_0']:
                            hover_color = -0.2
                        # For normal buttons/button color
                        elif widget_color[0] == 1:
                            hover_color = -0.025
                        # For operator buttons/operator color
                        else:
                            hover_color = 0.02

                    self.widget_changed_on_hover = [True, widget_id, widget_color.copy()]

                    if widget_id in ['a', 'b', 'c']:
                        widget_color[3] += hover_color
                        if widget_id == 'a':
                            self.input_color_a = widget_color
                        elif widget_id == 'b':
                            self.input_color_b = widget_color
                        elif widget_id == 'c':
                            self.input_color_c = widget_color
                    else:
                        self.ids[widget_id].background_color = [
                            widget_color[index] + hover_color for index in range(3)]
                    break
            else:
                # To change back to original color of the button
                if self.widget_changed_on_hover[0] and self.widget_changed_on_hover[1] == \
                        widget_id and not self.button_press:

                    if widget_id in ['a', 'b', 'c']:
                        if widget_id == 'a' and not self.main_input_1_status:
                            self.input_color_a = self.widget_changed_on_hover[2]
                        elif widget_id == 'b' and not self.main_input_2_status:
                            self.input_color_b = self.widget_changed_on_hover[2]
                        elif widget_id == 'c' and not self.main_input_3_status:
                            self.input_color_c = self.widget_changed_on_hover[2]
                    else:
                        self.ids[self.widget_changed_on_hover[1]].background_color = \
                            self.widget_changed_on_hover[2]
                    self.widget_changed_on_hover = [False]
                    break

            if self.press_not_executed:
                Clock.schedule_once(
                    lambda *arg: self.change_color_on_press(self.button_pressed))
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

        for button_number in range(16 + 1 if self.graph_status else 15 + 1):
            if button_number == 1:
                self.x_coordinate_widget_min.append(self.x_coordinate_widget_min[0])
                self.x_coordinate_widget_max.append(self.x_coordinate_widget_min[0] + 220
                                                    * Metrics.dp)
                self.y_coordinate_widget_max.append(self.y_coordinate_widget_min[0] - 40
                                                    * Metrics.dp)
                self.y_coordinate_widget_min.append(self.y_coordinate_widget_min[0] - 75
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

        for text_input in ['a', 'b', 'c']:
            widget_name = text_input
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
        theme.
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
        """
        Function changes the color of the button to the color
        before pressing it.
        """
        if self.button_press:
            self.button_press = False
            button.background_color = self.button_color_before_press
            self.on_mouse_position(0, self.current_mouse_pos)
            self.on_mouse_position(0, self.current_mouse_pos)
        self.press_not_executed = False

    def plot_graph(self, graph_type: str = 'empty'):
        """
        Function used to plot the graph.
        :param graph_type: Plot empty or main graph
        """
        if self.graph_status:

            plt.clf()
            plt.close('all')

            if self.theme == 'dark':
                plt.figure(facecolor=[0, 0, 0, 0])
                axes = plt.axes()
                axes.set_facecolor((.13, .13, .13, 1))
                plt.plot(self.x_quadrant, self.y_quadrant, '#141414')
                plt.plot(self.x2_quadrant, self.y2_quadrant, '#141414')
                plt.tick_params(axis='y', labelsize=5.5, labelcolor='white', color='white')
                plt.tick_params(axis='x', labelsize=5.5, labelcolor='white', color='white')
            elif self.theme == 'light':
                plt.figure(facecolor=[0, 0, 0, 0])
                axes = plt.axes()
                axes.set_facecolor((.95, .95, .95, 1))
                plt.plot(self.x_quadrant, self.y_quadrant, '#969696')
                plt.plot(self.x2_quadrant, self.y2_quadrant, '#969696')
                plt.tick_params(axis='y', labelsize=5.5, labelcolor='black', color='black')
                plt.tick_params(axis='x', labelsize=5.5, labelcolor='black', color='black')

            if graph_type == 'main':
                self.graph_plotted = 'main'
                plt.plot(self.x_coordinates, self.y_coordinates, '#3fb2dd')
                plt.xlim(self.x_lim0, self.x_lim1)
                plt.ylim(self.y_lim0, self.y_lim1)
            elif graph_type == 'empty':
                self.graph_plotted = 'empty'
                plt.xlim(-self.slider_value * 10, self.slider_value * 10)
                plt.ylim(-self.slider_value * 10, self.slider_value * 10)

            plt.grid(True)

            if self.user_plotted_point_status:
                point = plt.plot(self.user_plotted_point_x, self.user_plotted_point_y,
                                 marker="o", markersize=2,
                                 markeredgecolor="#ff7f00",
                                 markerfacecolor="#ff7f00")
                self.user_plotted_point = point.pop()
                self.coordinates_text = \
                    f'''X = {round(self.user_plotted_point_x, 4)} , Y = {
                    round(self.user_plotted_point_y, 4)}'''
                self.ids.coordinates_label.text = self.coordinates_text

            if not self.switch_status:
                self.cid0 = plt.connect('button_press_event', self.button_press_event_graph)
                self.cid1 = plt.connect('axes_enter_event',
                                        lambda *arg: Window.set_system_cursor('crosshair'))
                self.cid2 = plt.connect('figure_leave_event',
                                        lambda *arg: Window.set_system_cursor('arrow'))
                self.cid3 = plt.connect('motion_notify_event', self.motion_notify_event_graph)

            self.ids.graph1.clear_widgets()
            self.ids.graph1.add_widget(FigureCanvasKivyAgg(plt.gcf()))

            self.ids.sld_switch.disabled = False
            if not self.switch_status:
                self.slider_status = True
                self.ids.sld.disabled = True
            else:
                self.slider_status = False
                self.ids.sld.disabled = False

    def on_value_slider(self):
        """
        Function executed whenever the value of the graph slider is
        changed
        """
        # Zoom in or out the graph
        self.slider_value = self.ids.sld.value
        if self.graph_plotted == 'main':
            self.eval_graph_limits()
        else:
            self.x_lim0 = -(10 * self.slider_value)
            self.x_lim1 = 10 * self.slider_value
            self.y_lim0 = -(10 * self.slider_value)
            self.y_lim1 = 10 * self.slider_value
        plt.xlim(self.x_lim0, self.x_lim1)
        plt.ylim(self.y_lim0, self.y_lim1)
        self.ids.graph1.clear_widgets()
        self.ids.graph1.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def on_active_switch(self, switch, status):
        """
        Function executed when the slider switch is activated or
        deactivated
        :param switch:
        :param status:
        """
        self.switch_status = status
        if not switch.active:
            self.slider_status = True
            self.ids.sld.disabled = True
            self.plot_graph('main' if len(self.x_coordinates) != 0 else 'empty')
        else:
            self.ids.sld.disabled = False
            self.slider_status = False
            self.ids.sld.disabled = False
            plt.disconnect(self.cid0)
            plt.disconnect(self.cid1)
            plt.disconnect(self.cid2)
            plt.disconnect(self.cid3)

    def on_press_trash_button(self, *args):  # noqa
        """Function executed on press of trash button"""
        self.button_press = True
        self.ids.button_16.background_normal = r'dependencies/icons/trash_animate.ico'

    def on_release_trash_button(self, *args):  # noqa
        """
        Function used to give the animation effect to the trash
        button on release.
        """
        Clock.schedule_once(self.on_release_trash_button_main)

    def on_release_trash_button_main(self, *args):  # noqa
        """Function executed on release of trash button"""
        self.ids.button_16.background_normal = r'dependencies/icons/trash.ico'
        self.remove_point()
        self.button_press = False
        if self.widget_changed_on_hover[0] and self.widget_changed_on_hover[1] == \
                'button_16':
            self.widget_changed_on_hover = [False]
        self.trash_status = True
        self.trash_color = [0, 0, 0, 0]
        self.ids.button_16.disabled = True
        self.ids.button_16.background_color = [0, 0, 0, 0]
        self.on_mouse_position(0, self.current_mouse_pos)
        self.on_mouse_position(0, self.current_mouse_pos)

    def get_equation_text(self) -> str:
        """Calculates the text for the equation label."""
        operator_1 = '+'
        operator_2 = '+'
        _a = self.ids.a.text
        _b = self.ids.b.text
        _c = self.ids.c.text
        if '-' in _b:
            operator_1 = '-'
            _b = ''.join([i for i in _b if i != '-'])
        if '-' in _c:
            operator_2 = '-'
            _c = ''.join([i for i in _c if i != '-'])
        return f'{_a}x[sup]2[/sup] {operator_1} {_b}x {operator_2} {_c} = 0'

    def on_num_click(self, widget):
        """Executed when a number is clicked except 0"""
        if self.main_input_1_status:
            if len(self.ids.a.text) < 10:
                self.ids.a.text += widget.text
        elif self.main_input_2_status:
            if len(self.ids.b.text) < 10:
                self.ids.b.text += widget.text
        elif self.main_input_3_status:
            if len(self.ids.c.text) < 10:
                self.ids.c.text += widget.text

    def on_zero_click(self):
        """Executed when 0 is clicked"""
        if self.main_input_1_status:
            # for max 6 digit input
            if len(self.ids.a.text) < 10:
                self.ids.a.text += '0'
        elif self.main_input_2_status:
            # for max 6 digit input
            if len(self.ids.b.text) < 10:
                self.ids.b.text += '0'
        elif self.main_input_3_status:
            # for max 6 digit input
            if len(self.ids.c.text) < 10:
                self.ids.c.text += '0'

    def on_decimal_click(self):
        """Executed when . is clicked"""
        if self.main_input_1_status:
            if '.' not in self.ids.a.text and len(self.ids.a.text) < 9:
                self.ids.a.text += '.'
        elif self.main_input_2_status and len(self.ids.b.text) < 9:
            if '.' not in self.ids.b.text:
                self.ids.b.text += '.'
        elif self.main_input_3_status and len(self.ids.c.text) < 9:
            if '.' not in self.ids.c.text:
                self.ids.c.text += '.'

    def plus_minus(self):
        """Executed when ± is clicked"""
        if self.main_input_1_status and len(self.ids.a.text) < 9:
            if '-' in self.ids.a.text:
                self.ids.a.text = \
                    ''.join([element for element in self.ids.a.text if element != '-'])
            else:
                self.ids.a.text = f'-{self.ids.a.text}'

        elif self.main_input_2_status and len(self.ids.b.text) < 9:
            if '-' in self.ids.b.text:
                self.ids.b.text = \
                    ''.join([element for element in self.ids.b.text if element != '-'])
            else:
                self.ids.b.text = f'-{self.ids.b.text}'

        elif self.main_input_3_status and len(self.ids.c.text) < 9:
            if '-' in self.ids.c.text:
                self.ids.c.text = \
                    ''.join([element for element in self.ids.c.text if element != '-'])
            else:
                self.ids.c.text = f'-{self.ids.c.text}'

    def backspace(self):
        """Executed when ⌫ is clicked"""
        if self.main_input_1_status:
            self.ids.a.text = self.ids.a.text[:-1]
        elif self.main_input_2_status:
            self.ids.b.text = self.ids.b.text[:-1]
        elif self.main_input_3_status:
            self.ids.c.text = self.ids.c.text[:-1]

    def on_focus_a(self, value, instance):  # noqa
        """
        Function executed when the user focuses or de focuses the
        1st text input
        """
        if instance:
            self.main_input_1_status = True
            if self.theme == 'dark':
                self.input_color_a = [1, 1, 1, 1]
            else:
                self.input_color_a = [0, 0, 0, 1]
        else:
            if self.keypad_button_press and self.main_input_1_status:
                self.ids.a.focus = True
                return
            self.main_input_1_status = False
            if self.theme == 'dark':
                self.input_color_a = [1, 1, 1, .5]
            else:
                self.input_color_a = [0, 0, 0, .6]

    def on_focus_b(self, value, instance):  # noqa
        """
        Function executed when the user focuses or de focuses
        the 2nd text input
        """
        if instance:
            self.main_input_2_status = True
            if self.theme == 'dark':
                self.input_color_b = [1, 1, 1, 1]
            else:
                self.input_color_b = [0, 0, 0, 1]
        else:
            if self.keypad_button_press and self.main_input_2_status:
                self.ids.b.focus = True
                return
            self.main_input_2_status = False
            if self.theme == 'dark':
                self.input_color_b = [1, 1, 1, .5]
            else:
                self.input_color_b = [0, 0, 0, .6]

    def on_focus_c(self, value, instance):  # noqa
        """
        Function executed when the user focuses or de focuses
        the 3rd text input
        """
        if instance:
            self.main_input_3_status = True
            if self.theme == 'dark':
                self.input_color_c = [1, 1, 1, 1]
            else:
                self.input_color_c = [0, 0, 0, 1]
        else:
            if self.keypad_button_press and self.main_input_3_status:
                self.ids.c.focus = True
                return
            self.main_input_3_status = False
            if self.theme == 'dark':
                self.input_color_c = [1, 1, 1, .5]
            else:
                self.input_color_c = [0, 0, 0, .6]

    @staticmethod
    def check_text_input_length(text_input):
        """
        Stops user from inputting more than 10 characters using
        keyboard.
        Function executed on text input in the text input
        """
        if len(text_input.text) == 10:
            text_input.readonly = True
        else:
            text_input.readonly = False

    def solve_equation(self):
        """
        Solve the current equation on the screen.
        Function also executed on text input in the text input
        """
        _a = self.ids.a.text
        _b = self.ids.b.text
        _c = self.ids.c.text
        self.stop_thread()
        self.remove_point(plot=False)
        self.trash_status = True
        self.trash_color = [0, 0, 0, 0]
        if self.graph_status:
            self.ids.button_16.disabled = True
            self.ids.button_16.background_color = [0, 0, 0, 0]
        try:
            if len(_a) > 10 or len(_b) > 10 or len(_c) > 10:
                raise ValueError
            self.a = float(_a)
            self.b = float(_b)
            self.c = float(_c)
            # To solve linear equations
            if self.a == 0 and self.b != 0:
                self.root_1 = self.root_2 = linear(self.b, self.c)['root']
                self.main_text = f'Root is: {self.root_1}'
                self.discriminant_text = 'Discriminant:N/A'
                self.por_text = 'Product of Roots:N/A'
                self.sor_text = 'Sum of Roots:N/A'
                self.vertex_text = 'Vertex:N/A'
            # To solve quadratic equations
            else:
                solved_equation = quadratic(self.a, self.b, self.c)
                self.d = solved_equation['discriminant']
                self.vertex_x = solved_equation['vertex'][0]
                self.vertex_y = solved_equation['vertex'][1]
                self.root_1 = solved_equation['root_1']
                self.root_2 = solved_equation['root_2']
                self.main_text = f'Roots Are: {self.root_1} , {self.root_2}'
                self.discriminant_text = f'Discriminant: {self.d}'
                self.sor_text = f'Sum of roots: {solved_equation["sor"]}'
                self.por_text = f'Product of Roots: {solved_equation["por"]}'
                self.vertex_text = f'Vertex: {solved_equation["vertex"]}'
            self.equation_text = self.get_equation_text()
            self.x_coordinates.clear()
            self.y_coordinates.clear()
            self.points_status = 'incomplete'
            if self.graph_status:
                self.ids.sld.value = 0.5
                self.eval_graph_limits()
                while True:
                    if self.thread_status == 'idle':
                        self.thread_for_points = \
                            threading.Thread(target=self.get_points_graph,
                                             args=(self.a, self.b, self.c))
                        self.thread_for_points.start()
                        break
                if self.temp_remove_graph:
                    self.ids.graph1.clear_widgets()
                    plt.clf()
                self.ids.sld_switch.disabled = True
                self.ids.sld.disabled = True
        except ValueError:
            self.x_coordinates.clear()
            self.y_coordinates.clear()
            self.equation_text = 'N/A'
            self.main_text = 'Roots Are:N/A'
            self.discriminant_text = 'Discriminant:N/A'
            self.por_text = 'Product of Roots:N/A'
            self.sor_text = 'Sum of Roots:N/A'
            self.vertex_text = 'Vertex:N/A'
            self.ids.button_0.disabled = False
            if self.graph_status:
                self.plot_graph()
                self.points_status = 'none'
                self.pg_value(0, '=')
            self.on_mouse_position(1, self.current_mouse_pos)

    # Sub functions for graph
    def motion_notify_event_graph(self, event):
        """
        Function executed whenever mouse is moved on the graph
        """
        self.mouse_move_on_graph_x, self.mouse_move_on_graph_y = event.xdata, event.ydata
        if self.mouse_move_on_graph_x is None:
            if not self.user_plotted_point_status:
                self.coordinates_text = 'X = 0 , Y = 0'
                self.ids.coordinates_label.text = self.coordinates_text
        else:
            if self.user_plotted_point_status:
                return

            self.coordinates_text = \
                f'''X = {round(self.mouse_move_on_graph_x, 4)
                } , Y = {round(self.mouse_move_on_graph_y, 4)}'''
            self.ids.coordinates_label.text = self.coordinates_text

    def button_press_event_graph(self, event):
        """
        Function executed whenever mouse button is pressed on the
        graph
        """
        self.mouse_move_on_graph_x, self.mouse_move_on_graph_y = event.xdata, event.ydata
        if self.mouse_move_on_graph_x is not None:
            if self.user_plotted_point_status:
                self.user_plotted_point.remove()
            self.user_plotted_point_status = True
            self.user_plotted_point_x = self.mouse_move_on_graph_x
            self.user_plotted_point_y = self.mouse_move_on_graph_y
            self.plot_graph('main' if len(self.x_coordinates) != 0 else 'empty')
            self.coordinates_text = \
                f'''X = {round(self.user_plotted_point_x, 4)
                } , Y = {round(self.user_plotted_point_y, 4)}'''
            self.ids.coordinates_label.text = self.coordinates_text
            self.trash_status = False
            self.trash_color = [1, 1, 1, 1]
            self.ids.button_16.background_color = [1, 1, 1, 1]
            self.ids.button_16.disabled = False

    def pg_value(self, val, opp):
        """Add or change the progress bar's value"""
        if self.graph_status:
            if opp == '+':
                self.ids.pg.value += val
            elif opp == '=':
                self.ids.pg.value = val

    def remove_point(self, plot=True):
        """To remove the plotted point by the user"""
        self.user_plotted_point_status = False
        self.coordinates_text = 'X = 0 , Y = 0'
        self.user_plotted_point_x = 0
        self.user_plotted_point_y = 0
        if self.graph_status:
            self.ids.coordinates_label.text = self.coordinates_text
            if plot:
                self.plot_graph('main' if len(self.x_coordinates) != 0 else 'empty')

    def eval_graph_limits(self):
        """Evaluate the graph limits"""
        # Limits for y-axis
        if self.a == 0:
            y_lim0 = -10 * self.slider_value
            y_lim1 = 10 * self.slider_value

        elif self.d > 0:
            if self.vertex_y < 0:
                y_lim1 = -(self.vertex_y - (-self.slider_value * self.vertex_y))
            else:
                y_lim1 = self.vertex_y + (self.slider_value * self.vertex_y)
            y_lim0 = -y_lim1

        else:
            if self.vertex_y < 0:
                if self.a > 0:
                    y_lim0 = self.vertex_y - (-self.slider_value * self.vertex_y * 0.2)
                    y_lim1 = self.vertex_y + (-self.slider_value * self.vertex_y)
                else:
                    y_lim0 = self.vertex_y - (-self.slider_value * self.vertex_y * 5)
                    y_lim1 = self.vertex_y + (-self.slider_value * self.vertex_y)

            elif self.vertex_y == 0:
                if self.a > 0:
                    y_lim0 = -(0.4 * self.slider_value)
                    y_lim1 = 2 * self.slider_value
                else:
                    y_lim0 = -(2 * self.slider_value)
                    y_lim1 = 0.4 * self.slider_value

            else:
                y_lim0 = self.vertex_y - (self.slider_value * self.vertex_y * 0.2)
                y_lim1 = self.vertex_y + (self.slider_value * self.vertex_y)

        # Limits for x-axis
        if self.a == 0:
            x_lim0 = self.root_1 - (self.slider_value * 10)
            x_lim1_max = self.root_1 - (2 * 10)
            x_lim1_min = self.root_1 - (0.1 * 10)
            x_lim1 = self.root_1 + (self.slider_value * 10)
            x_lim2_max = self.root_1 + (2 * 10)
            x_lim2_min = self.root_1 + (0.1 * 10)

        elif self.d > 0:
            if self.root_1 > self.root_2:
                larger_root = self.root_1
                smaller_root = self.root_2
            else:
                larger_root = self.root_2
                smaller_root = self.root_1
            x_lim0 = smaller_root - ((larger_root - smaller_root) * self.slider_value)
            x_lim1_max = smaller_root - ((larger_root - smaller_root) * 2)
            x_lim1_min = smaller_root - ((larger_root - smaller_root) * 0.1)
            x_lim1 = larger_root + ((larger_root - smaller_root) * self.slider_value)
            x_lim2_max = larger_root + ((larger_root - smaller_root) * 2)
            x_lim2_min = larger_root + ((larger_root - smaller_root) * 0.1)

        else:
            if self.a > 0:
                temp_vertex_y = y_lim1
            else:
                temp_vertex_y = y_lim0
            vertex_root_1 = ((-self.b) + ((self.b ** 2) - 4 * self.a *
                                          (self.c - temp_vertex_y)) ** (1 / 2)) / (2 * self.a)
            vertex_root_2 = ((-self.b) - ((self.b ** 2) - 4 * self.a *
                                          (self.c - temp_vertex_y)) ** (1 / 2)) / (2 * self.a)

            x_lim0 = self.vertex_x - (abs(vertex_root_2 - vertex_root_1) * (self.slider_value
                                                                            * 1.26))
            x_lim1_max = self.vertex_x - (abs(vertex_root_2 - vertex_root_1) * 3.2)
            x_lim1_min = self.vertex_x - (abs(vertex_root_2 - vertex_root_1) * 0.126)
            x_lim1 = self.vertex_x + (abs(vertex_root_2 - vertex_root_1) * (self.slider_value
                                                                            * 1.26))
            x_lim2_max = self.vertex_x + (abs(vertex_root_2 - vertex_root_1) * 3.2)
            x_lim2_min = self.vertex_x + (abs(vertex_root_2 - vertex_root_1) * 0.126)

        lowest_limit = 7e-04

        def check_lowest_limit(number) -> float:
            """Check All values are grater than the lowest value possible"""
            if abs(number) < lowest_limit:
                if number > 0:
                    number = lowest_limit
                elif number < 0:
                    number = -lowest_limit
            return number

        self.y_lim0 = y_lim0
        self.y_lim1 = y_lim1
        self.x_lim0 = check_lowest_limit(x_lim0)
        self.x_lim1 = check_lowest_limit(x_lim1)
        self.starting_point = check_lowest_limit(x_lim1_max) - 10
        self.ending_point = check_lowest_limit(x_lim2_max) + 10
        self.graph_total_points = abs(self.ending_point - self.starting_point)
        temp_x_lim1 = check_lowest_limit(x_lim1_min)
        temp_x_lim2 = check_lowest_limit(x_lim2_min)
        self.graph_points_to_be_added = abs((temp_x_lim2 - temp_x_lim1)) / 100

    def get_points_graph(self, _a, _b, _c):
        """Get the coordinates to plot the required graph"""
        Clock.schedule_once(lambda *arg: self.on_mouse_position(0, (-1, -1)))
        if self.event is not None:
            self.event.cancel()
            self.event_1.cancel()
            self.event_3.cancel()
        if self.event_2 is not None:
            self.event_2.cancel()
        self.thread_status = 'running'
        self.pg_value(0, '=')

        def menu_disable(status):
            """..."""
            self.ids.button_0.disabled = status

        self.event_2 = Clock.schedule_once(lambda *arg: menu_disable(True))
        if _a == 0:
            self.x_coordinates.clear()
            self.y_coordinates.clear()
            self.x_coordinates.append(self.starting_point)
            self.x_coordinates.append(self.ending_point)
            self.y_coordinates.append((_b * self.starting_point) + _c)
            self.y_coordinates.append((_b * self.ending_point) + _c)
            self.ids.pg.max = 100
            self.pg_value(100, '=')
        else:
            self.ids.pg.max = self.graph_total_points
            _x = self.starting_point
            while _x <= self.ending_point:
                if self.thread_status == 'stop':
                    self.thread_status = 'idle'

                    return
                val_x = (_a * (_x ** 2)) + (_b * _x) + _c
                self.x_coordinates.append(_x)
                self.y_coordinates.append(val_x)
                _x += self.graph_points_to_be_added
                self.pg_value(self.graph_points_to_be_added, '+')

        self.thread_status = 'idle'
        self.points_status = 'complete'
        self.event = Clock.schedule_once(lambda *arg: self.plot_graph('main'))
        self.event_1 = Clock.schedule_once(lambda *arg: self.pg_value(0, '='), 0.35)
        self.event_2 = Clock.schedule_once(lambda *arg: menu_disable(False))
        self.event_3 = Clock.schedule_once(
            lambda *arg: self.on_mouse_position(0, Window.mouse_pos))

    def stop_thread(self, *args):  # noqa
        """Stop the graph thread using flags"""
        if self.thread_status == 'running':
            self.thread_status = 'stop'
            while True:
                if self.thread_status == 'idle':
                    return

