import sys
import pygame
from pygame.locals import *

from scripts.config import config


class Input:
    def __init__(self, game=None):
        self.game = game
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

        self.states = {}
        self.pad_states = {}
        self.mouse_state = {}
        self.mouse_pos = (0, 0)
        self.input_mode = 'core'
        self.input_method = 'keyboard'
        self.dpad = (0, 0)
        self.dpad_single = (0, 0)
        self.dpad_last_frame = (0, 0)

        self.full_reset()

    def full_reset(self):
        for binding in config['input']:
            self.states[binding] = False

        for binding in config['input_gamepad']:
                self.states[binding] = False

        for binding in config['input_editor']:
                self.states[binding] = False

        self.mouse_state = {
            'left': False,
            'right': False,
            'left_hold': False,
            'right_hold': False,
            'left_release': False,
            'right_release': False,
            'scroll_up': False,
            'scroll_down': False,
        }

    def soft_reset(self):
        for binding in config['input']:
            if config['input'][binding]['trigger'] == 'press':
                self.states[binding] = False

        for binding in config['input_gamepad']:
            if config['input_gamepad'][binding]['trigger'] == 'press':
                self.states[binding] = False

        for binding in config['input_editor']:
            if config['input_editor'][binding]['trigger'] == 'press':
                self.states[binding] = False

        self.mouse_state['left'] = False
        self.mouse_state['right'] = False

        self.dpad_single = (0, 0)

    def hold_reset(self):
        for binding in config['input']:
            if config['input'][binding]['trigger'] == 'press':
                self.states[binding] = False

        for binding in config['input_gamepad']:
            if config['input_gamepad'][binding]['trigger'] == 'press':
                self.states[binding] = False

        for binding in config['input_editor']:
            if config['input_editor'][binding]['trigger'] == 'press':
                self.states[binding] = False

        self.mouse_state['left'] = False
        self.mouse_state['right'] = False
        self.mouse_state['left_release'] = False
        self.mouse_state['right_release'] = False
        self.mouse_state['scroll_up'] = False
        self.mouse_state['scroll_down'] = False

    def event_update(self, event):
        self.soft_reset()
        # Keyboard Inputs
        if event.type == KEYDOWN:
            for binding in config['input']:
                if set(config['input'][binding]['mode']).intersection({'all', self.input_mode}):
                    if config['input'][binding]['binding'][0] == 'keyboard':
                        if config['input'][binding]['trigger'] in ['press', 'hold']:
                            if event.key in config['input'][binding]['binding'][1]:
                                self.states[binding] = True
            for binding in config['input_editor']:
                if set(config['input_editor'][binding]['mode']).intersection({'all', self.input_mode}):
                    if config['input_editor'][binding]['binding'][0] == 'keyboard':
                        if config['input_editor'][binding]['trigger'] in ['press', 'hold']:
                            if event.key in config['input_editor'][binding]['binding'][1]:
                                self.states[binding] = True
        if event.type == KEYUP:
            for binding in config['input']:
                if set(config['input'][binding]['mode']).intersection({'all', self.input_mode}):
                    if config['input'][binding]['binding'][0] == 'keyboard':
                        if config['input'][binding]['trigger'] in ['press', 'hold']:
                            if event.key in config['input'][binding]['binding'][1]:
                                self.states[binding] = False
            for binding in config['input_editor']:
                if set(config['input_editor'][binding]['mode']).intersection({'all', self.input_mode}):
                    if config['input_editor'][binding]['binding'][0] == 'keyboard':
                        if config['input_editor'][binding]['trigger'] in ['press', 'hold']:
                            if event.key in config['input_editor'][binding]['binding'][1]:
                                self.states[binding] = False

        # Controller Inputs
        # Buttons
        if event.type == JOYBUTTONDOWN:
            for binding in config['input_gamepad']:
                if set(config['input_gamepad'][binding]['mode']).intersection({'all', self.input_mode}):
                    if config['input_gamepad'][binding]['binding'][0] == 'gamepad_button':
                        if config['input_gamepad'][binding]['trigger'] in ['press', 'hold']:
                            if event.button in config['input_gamepad'][binding]['binding'][1]:
                                self.states[binding] = True
                                # print(event.button)

        if event.type == JOYBUTTONUP:
            for binding in config['input_gamepad']:
                if set(config['input_gamepad'][binding]['mode']).intersection({'all', self.input_mode}):
                    if config['input_gamepad'][binding]['binding'][0] == 'gamepad_button':
                        if config['input_gamepad'][binding]['trigger'] in ['press', 'hold']:
                            if event.button in config['input_gamepad'][binding]['binding'][1]:
                                self.states[binding] = False

        # DPAD
        if event.type == JOYHATMOTION:
            self.dpad = event.value
            self.dpad_single = event.value
        # print(str(self.dpad_last_frame) + "  " + str(self.dpad) + " " + str(self.dpad_single))

        """if event.type == JOYAXISMOTION:
            print(event)

        if event.type == JOYBALLMOTION:
            print(event)"""

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.mouse_state['left'] = True
                self.mouse_state['left_hold'] = True
            if event.button == 3:
                self.mouse_state['right'] = True
                self.mouse_state['right_hold'] = True
            if event.button == 4:
                self.mouse_state['scroll_up'] = True
            if event.button == 5:
                self.mouse_state['scroll_down'] = True
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_state['left_release'] = True
                self.mouse_state['left_hold'] = False
            if event.button == 3:
                self.mouse_state['right_release'] = True
                self.mouse_state['right_hold'] = False

    def update(self):
        x, y = pygame.mouse.get_pos()

        self.soft_reset()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Keyboard Inputs
            if event.type == KEYDOWN:
                for binding in config['input']:
                    if set(config['input'][binding]['mode']).intersection({'all', self.input_mode}):
                        if config['input'][binding]['binding'][0] == 'keyboard':
                            if config['input'][binding]['trigger'] in ['press', 'hold']:
                                if event.key in config['input'][binding]['binding'][1]:
                                    self.states[binding] = True
                                    print(event.key)
            if event.type == KEYUP:
                for binding in config['input']:
                    if set(config['input'][binding]['mode']).intersection({'all', self.input_mode}):
                        if config['input'][binding]['binding'][0] == 'keyboard':
                            if config['input'][binding]['trigger'] in ['press', 'hold']:
                                if event.key in config['input'][binding]['binding'][1]:
                                    self.states[binding] = False

            # Controller Inputs
            # Buttons
            if event.type == JOYBUTTONDOWN:
                for binding in config['input_gamepad']:
                    if set(config['input_gamepad'][binding]['mode']).intersection({'all', self.input_mode}):
                        if config['input_gamepad'][binding]['binding'][0] == 'gamepad_button':
                            if config['input_gamepad'][binding]['trigger'] in ['press', 'hold']:
                                if event.button in config['input_gamepad'][binding]['binding'][1]:
                                    self.states[binding] = True
                                    # print(event.button)

            if event.type == JOYBUTTONUP:
                for binding in config['input_gamepad']:
                    if set(config['input_gamepad'][binding]['mode']).intersection({'all', self.input_mode}):
                        if config['input_gamepad'][binding]['binding'][0] == 'gamepad_button':
                            if config['input_gamepad'][binding]['trigger'] in ['press', 'hold']:
                                if event.button in config['input_gamepad'][binding]['binding'][1]:
                                    self.states[binding] = False

            # DPAD
            if event.type == JOYHATMOTION:
                self.dpad = event.value
                self.dpad_single = event.value
            # print(str(self.dpad_last_frame) + "  " + str(self.dpad) + " " + str(self.dpad_single))

            """if event.type == JOYAXISMOTION:
                print(event)
    
            if event.type == JOYBALLMOTION:
                print(event)"""

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_state['left'] = True
                    self.mouse_state['left_hold'] = True
                if event.button == 3:
                    self.mouse_state['right'] = True
                    self.mouse_state['right_hold'] = True
                if event.button == 4:
                    self.mouse_state['scroll_up'] = True
                if event.button == 5:
                    self.mouse_state['scroll_down'] = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_state['left_release'] = True
                    self.mouse_state['left_hold'] = False
                if event.button == 3:
                    self.mouse_state['right_release'] = True
                    self.mouse_state['right_hold'] = False
