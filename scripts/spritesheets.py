import json
import os
import pygame

SPRITESHEET_PATH = 'data/sprites/spritesheets'
COLORKEY = (0, 0, 0)


def load_img(path: str, colorkey=None, retain_alpha=False) -> pygame.Surface:
    if retain_alpha:
        img = pygame.image.load(path).convert_alpha()
    else:
        img = pygame.image.load(path).convert()
    if colorkey:
        img.set_colorkey(colorkey)
    return img


class Spritesheet:
    """
    A class holding a single spritesheet and its sprite elements
    """

    def __init__(self, path: str, colorkey=COLORKEY):
        """
        the path directory gets recursively searched, all spritesheet pngs get added to the spritesheet variable
        if no config for the spritesheet exists, a config will be created with tilesetDefault values
        Spritesheets are object which hold sprites for the tiles, animations and decals are not included (yet)
        The spritesheet then gets loaded into memory

        :param path: a path to the folder with all the spritesheets (can have subfolders)
        :param colorkey: a colorkey to key out the background
        """
        self.id = path.split('/')[-1]
        self.tile_list = []
        self.spritesheet = None

        for img in os.listdir(path):
            if img.split('.')[-1] == 'png':
                self.spritesheet = load_img(path + '/' + img, colorkey, False)
        try:
            f = open(path + '/config.json', 'r')
            self.config = json.loads(f.read())
            f.close()
        except FileNotFoundError:
            # TODO: Adjust Config so it can either hold tilesets or objects with variable sizes
            self.config = {
                'tile_width': 16,
                'tile_height': 16,
                'tile_size': 16,
                'rows': 8,
                'columns': 4,
                "tile_range": [0, 31],
                "foliage_range": False
            }
            f = open(path + '/config.json', 'w')
            f.write(json.dumps(self.config))
            f.close()

        for row in range(0, self.config['rows']):
            for column in range(0, self.config['columns']):
                x = self.config['tile_size'] * column
                y = self.config['tile_size'] * row
                width = self.config['tile_width']
                height = self.config['tile_height']
                rectangle = pygame.Rect(x, y, width, height)
                try:
                    tile = self.spritesheet.subsurface(rectangle)
                    self.tile_list.append(tile)
                except ValueError:
                    self.tile_list.append(None)

    def get_tile_list(self):
        return self.tile_list


class SpritesheetManager:
    """
    A Manager class holding all the spritesheets. All spritesheets can be accessed via this classes
    getter function
    """

    def __init__(self):
        self.spritesheets = {}

    def load_spritesheets(self):
        for ssheet in os.listdir(SPRITESHEET_PATH):
            if ".py" in ssheet:
                continue
            self.spritesheets[ssheet.lower()] = Spritesheet(SPRITESHEET_PATH + '/' + ssheet.lower(), COLORKEY)

    def get_spritesheet(self, sheetname: str) -> list:
        """
        Returns a spritesheetobject out of the dictionary if it exists
        :param sheetname: a string for the sheetname
        :return: the sheet object
        """
        if sheetname in self.spritesheets:
            return self.spritesheets[sheetname].get_tile_list()

    def get_all_sheets(self) -> list:
        return_list = []
        for sheet in self.spritesheets.values():
            return_list.append(sheet)
        return return_list

    def get_all_sheets_dict(self) -> dict:
        return self.spritesheets