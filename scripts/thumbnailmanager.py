import os

import pygame

from scripts.engineconstants import RESOURCEPATHS
from scripts.engine_core_funcs import load_img


class ThumbnailManager:
    def __init__(self):
        self.thumbnails = {}
        self.resource_path = RESOURCEPATHS['thumbnails']

    def load_thumbnails(self):
        for img in os.listdir(self.resource_path):
            if img.split('.')[-1] == 'png':
                name = img.split(".", 1)[0]
                temp_thumbnail = Thumbnail(name, load_img(self.resource_path + '/' + img, (0, 0, 0)))
                self.thumbnails[name] = temp_thumbnail

    def get_thumbnail(self, name):
        return self.thumbnails[name]


class Thumbnail:
    def __init__(self, name, image: pygame.Surface, position: list[int] = (0, 0), scalar: list[int] = (4, 4)):
        self.position = position
        self.name = name
        self.image = image
        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = image.get_rect()
        self.scalar = scalar

    def get_scaled_rect(self):
        return pygame.Rect(self.position[0], self.position[1], self.width * self.scalar[0], self.height * self.scalar[1])
