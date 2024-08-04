import pygame
from pygame import Vector2 as vec2
from scripts.config import config
import os
from scripts.engineconstants import RESOURCEPATHS
from scripts.engine_core_funcs import load_img

PARALLAXCLASS = [0, 0.1, 0.20, 0.4, 0.5]


class BackgroundManager:
    def __init__(self):
        self.__backgrounds = {}
        self.path = RESOURCEPATHS['backgrounds']

    def load_backgrounds(self):
        for background in os.listdir(self.path):
            if ".py" in background:
                continue
            self.__backgrounds[background[:-4]] = load_img(self.path + '/' + background, (0, 0, 0))

    def get_backgrounds(self, room_name):
        return self.__backgrounds[room_name]


class Background:
    def __init__(self, game):
        self.game = game
        self.width = 260
        self.height = 110
        self.layer_surfaces = []
        self.background_data = {}
        self.offset = (0, 0)

    def load_background(self, layer_sheet: pygame.Surface, offset=(0,0)):
        self.layer_surfaces = self.__sheet_to_layers(layer_sheet)
        for i, background in enumerate(self.layer_surfaces):
            position = vec2(0, 0)
            parallax_mult = PARALLAXCLASS[i]
            self.background_data[i] = [position, parallax_mult]
        self.offset = offset

    def __sheet_to_layers(self, layer_sheet):
        amount_of_layers = layer_sheet.get_height() // self.height
        layers = []
        for i in range(amount_of_layers):
            subsurface = layer_sheet.subsurface(pygame.Rect(0, i * self.height, self.width, self.height))
            layers.append(subsurface)
        return layers

    def update(self, dt, camera):
        pass

    def render(self, surf, camera):
        for i, layer in enumerate(self.layer_surfaces):
            surf.blit(layer, (((self.background_data[i][0].x - camera[0]) * self.background_data[i][1]  + self.offset[0]),
                              (self.background_data[i][0].y - camera[1]) * self.background_data[i][1]  + self.offset[1]))
