import pygame
from pygame import Surface as Surface
from pygame import Vector2 as Vec2
from pygame import Rect as Rect
import random


class Tile:
    """
    The Tile Object holding all necessary information regarding the tiles in this game

    """

    def __init__(self, tile_size: int = 16, pos: Vec2 = (0, 0), solid: bool = True, destructable: bool = False, layer: int=4,
                 tileset_name: str = 'exampleset', tile_list: list = None, tile_index: int = 0, tile_type: str = "SOLID", color: tuple = (125, 125, 125), image=None, tile_grid=None, cave=None, scalar: Vec2 = Vec2(1, 1), tilemap = None):
        """
        :param tile_size: the pixel size of a tile
        :param pos: the tuple position of a tile
        :param solid: wether a tile is collideable or not
        :param destructable: wether a tile is destructable or not
        :param layer: a reference to the layer the tile should be on
        :param tileset_name: a name for the tileset so the correct tileset can be accessed during rendering
        :param tile_index: the tileset index so the correct sprite from the tileset can be accessed during rendering
        :param tile_type: a type definition of a tile as string
        :param color: a color for debugging purposes. grey by tilesetDefault
        """
        self.tile_size: int = tile_size
        self.__cave = cave
        self.__tile_grid: list[list[Tile]] = tile_grid
        self.position: Vec2 = pos
        self.pixel_position: Vec2 = Vec2(pos.x * tile_size, pos.y * tile_size)
        self.scalar = scalar
        self.scaled_pixel_position: Vec2 = self.pixel_position * self.scalar
        self.solid: bool = solid
        self.tileset_name: str = tileset_name
        self.destructable: bool = destructable
        self.tile_index: int = tile_index
        self.tile_type: str = tile_type
        self.neighbours: list[Tile] = []
        self.color: tuple = color
        self.image: pygame.Surface = image
        self.veg_spawnchance = 45
        self.corner_index = 0
        self.layer: int = layer
        self.tilemap = tilemap
        self.tile_list = tile_list
        self.__replacement_values = {15: 22, 14: 16, 11: 17, 7: 18, 13: 19}
        self.__cornertile_values = {1: 25, 2: 24, 4: 26, 8: 27}

        if not self.image and self.tile_index >= 0 and self.tile_list:
            self.image = self.tile_list[self.tile_index]


        # currently hardcoded for the editor
        # self.scaled_img: pygame.Surface = pygame.transform.scale_by(self.image, (4, 4))

        if not self.image:
            self.image = Surface((tile_size, tile_size))
            pygame.draw.rect(self.image, self.color, self.rect)

    @property
    def rect(self) -> Rect:
        """
        :return: the tiles rectangle
        """
        return Rect(self.position.x * self.tile_size, self.position.y * self.tile_size, self.tile_size, self.tile_size)

    @property
    def pixel_rect(self) -> Rect:
        return Rect(self.pixel_position.x * self.tile_size, self.pixel_position.y * self.tile_size, self.tile_size, self.tile_size)

    def get_scaled_rect(self, scalar: pygame.Vector2):
        return Rect(((self.position.x * self.tile_size * 4), (self.position.y * self.tile_size), self.tile_size * scalar.x, self.tile_size * scalar.y))

    def add_neighbour(self, neighbour) -> None:
        """
        Takes in a tile object and appends the neighbour list of this tile object
        :param neighbour: a tile object
        :return: Nothing
        """
        self.neighbours.append(neighbour)

    def clear_neighbours(self) -> None:
        """
        Clears the neighbours list
        :return:
        """
        self.neighbours.clear()

    def check_tile_index(self, offset: Vec2, dimensions: Vec2):
        return (0 <= self.position.x + offset.x < dimensions.x) and (0 <= self.position.y + offset.y < dimensions.y)

    def autotile(self, tileset: list, tilemap, layer: int = 0):
        """
        The autotiling ruleset for the indices is as follows:
        - 0-15 are the 4 bit values for the general 3x3 tileset
        - If a tiles autotile bitvalue is either 14, 13, 11 or 7 its a repeating tile.
            There is a x% chance to spawn a vegetation tile on top/left/right/bottom of it
            Repeating tiles have a 50% chance to use an additional tile which is found in index 16-19
            as each cardinal tile has 1 additional tile to randomize the visualsation
        - if the tile is a center tile (index 15) it checks if the diagonals exist,
            if there is a digaonal tile missing it becomes a corresponding corner tile which is found
            in indices 20-23
        """
        north_value = 0
        east_value = 0
        south_value = 0
        west_value = 0
        northwest_value = 0
        northeast_value = 0
        southwest_value = 0
        southeast_value = 0

        vegetation_chance: int = random.randint(0, 100)
        different_tile_chance = random.randint(0, 100)

        # check northern tile
        tile = tilemap.get_tile_cell(self.position.x, self.position.y - 1)
        if tile:
            north_value = 1

        # check eastern tile
        tile = tilemap.get_tile_cell(self.position.x + 1, self.position.y)
        if tile:
            east_value = 1

        # check south tile
        tile = tilemap.get_tile_cell(self.position.x, self.position.y + 1)
        if tile:
            south_value = 1

        # check west tile
        tile = tilemap.get_tile_cell(self.position.x - 1, self.position.y)
        if tile:
            west_value = 1

        # check north east tile
        tile = tilemap.get_tile_cell(self.position.x + 1, self.position.y - 1)
        if not tile:
            northeast_value = 1

        # check north west tile
        tile = tilemap.get_tile_cell(self.position.x - 1, self.position.y - 1)
        if not tile:
            northwest_value = 1

        # check south east tile
        tile = tilemap.get_tile_cell(self.position.x + 1, self.position.y + 1)
        if not tile:
            southeast_value = 1

        # check south west tile
        tile = tilemap.get_tile_cell(self.position.x - 1, self.position.y + 1)
        if not tile:
            southwest_value = 1

        # calc value
        self.tile_index = 1 * north_value + 2 * west_value + 4 * east_value + 8 * south_value
        self.corner_index = 1 * northwest_value + 2 * northeast_value + 4 * southwest_value + 8 * southeast_value
        # set image to tile img
        self.image = tileset[self.tile_index]

        # vegetational spawn
        if self.tile_index in [14, 6] and vegetation_chance <= self.veg_spawnchance:
            veg_type_index = random.randint(28, 31)
            veg_tile = Tile(self.tile_size, Vec2(self.position.x, self.position.y - 1), False, False, self.tileset_name, veg_type_index, "VEG", image=tileset[veg_type_index])
            self.__cave.add_tile_cell(veg_tile)

        # random tiles
        if different_tile_chance < 50 and self.tile_index in self.__replacement_values:
            self.tile_index = self.__replacement_values[self.tile_index]
            self.image = tileset[self.tile_index]

        if self.tile_index in [15, 22] and self.corner_index in self.__cornertile_values:
            self.image = tileset[self.__cornertile_values[self.corner_index]]

    def simple_autotile(self, layer: int = 4):
        """
        The autotiling ruleset for the indices is as follows:
        - 0-15 are the 4 bit values for the general 3x3 tileset
        - If a tiles autotile bitvalue is either 14, 13, 11 or 7 its a repeating tile.
            There is a x% chance to spawn a vegetation tile on top/left/right/bottom of it
            Repeating tiles have a 50% chance to use an additional tile which is found in index 16-19
            as each cardinal tile has 1 additional tile to randomize the visualsation
        - if the tile is a center tile (index 15) it checks if the diagonals exist,
            if there is a digaonal tile missing it becomes a corresponding corner tile which is found
            in indices 20-23
        """
        north_value = 0
        east_value = 0
        south_value = 0
        west_value = 0
        northwest_value = 0
        northeast_value = 0
        southwest_value = 0
        southeast_value = 0
        different_tile_chance = random.randint(0, 100)
        # check northern tile
        tile = self.tilemap.get_tile_cell(self.position.x, self.position.y - 1, layer=layer)
        if tile:
            north_value = 1

        # check eastern tile
        tile = self.tilemap.get_tile_cell(self.position.x + 1, self.position.y, layer=layer)
        if tile:
            east_value = 1

        # check south tile
        tile = self.tilemap.get_tile_cell(self.position.x, self.position.y + 1, layer=layer)
        if tile:
            south_value = 1

        # check west tile
        tile = self.tilemap.get_tile_cell(self.position.x - 1, self.position.y, layer=layer)
        if tile:
            west_value = 1

        # check north east tile
        tile = self.tilemap.get_tile_cell(self.position.x + 1, self.position.y - 1, layer=layer)
        if not tile:
            northeast_value = 1

        # check north west tile
        tile = self.tilemap.get_tile_cell(self.position.x - 1, self.position.y - 1, layer=layer)
        if not tile:
            northwest_value = 1

        # check south east tile
        tile = self.tilemap.get_tile_cell(self.position.x + 1, self.position.y + 1, layer=layer)
        if not tile:
            southeast_value = 1

        # check south west tile
        tile = self.tilemap.get_tile_cell(self.position.x - 1, self.position.y + 1, layer=layer)
        if not tile:
            southwest_value = 1

        # calc value
        self.tile_index = 1 * north_value + 2 * west_value + 4 * east_value + 8 * south_value
        self.corner_index = 1 * northwest_value + 2 * northeast_value + 4 * southwest_value + 8 * southeast_value
        # set image to tile img
        self.image = self.tile_list[self.tile_index]

        if different_tile_chance < 50 and self.tile_index in self.__replacement_values:
            self.tile_index = self.__replacement_values[self.tile_index]
            self.image = self.tile_list[self.tile_index]

        if self.tile_index in [15, 22] and self.corner_index in self.__cornertile_values:
            self.image = self.tile_list[self.__cornertile_values[self.corner_index]]

    def render(self, surf, offset: Vec2):
        rect = Rect(self.pixel_position.x - offset.x, self.pixel_position.y - offset.y, self.tile_size, self.tile_size)
        pygame.draw.rect(surf, (255, 0, 0), rect, 1)

    def tile_to_json(self):
        temp_dict = {'layer': self.layer, 'tile_size': self.tile_size, 'position': (int(self.position.x), int(self.position.y)), 'solid': self.solid, 'tileset_name': self.tileset_name, 'destructable': self.destructable,
                     'tile_index': self.tile_index, 'tile_type': self.tile_type, 'scalar': (int(self.scalar.x), int(self.scalar.y))}
        return temp_dict

