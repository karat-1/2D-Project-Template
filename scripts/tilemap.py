import pygame

from scripts.tile import Tile
from scripts.engineconstants import RESOURCEPATHS
from pygame import Surface
import json
import math
from scripts.renderchunks import RenderChunk
from pygame import Vector2 as Vec2

SURROUND_POS = [
    [0, 0],  # SAME
    [1, 0],  # RIGHT
    [0, 1],  # BELOW
    [1, 1],  # DOWN RIGHT
    [-1, 0],  # LEFT
    [1, -1],  # ABOVE RIGHT
    [-1, 1],  # DOWN LEFT
    [0, -1],  # ABOVE
    [-1, -1]] # ABOVE LEFT

DOUBLE_SURROUND = [[0, 2],
                   [2, 1],
                   [-2, 0],
                   [-2, 1],
                   [-2, 2],
                   [1, -2],
                   [0, -2],
                   [-1, -2],
                   [-1, 2],
                   [2, 0],
                   [1, 2]]
class Tilemap:

    def __init__(self, *args, **kwargs):
        self.__width = 0
        self.__height = 0
        self.__tile_size: int = 8
        self.__spritesheetmanager = kwargs.get('smanager')
        self.__tile_data = {
            'layer': [{}, {}, {}, {}, {}, {}, {}, {}, {}],
            'decals': [],
            'tile_size': self.__tile_size,
            'width': 128,
            'height': 128

        }
        self.__tileset: list[Surface] = kwargs.get('tileset')
        self.__render_chunks = []
        self.__chunk_size = 8
        self.__resource_paths = RESOURCEPATHS['rooms']
        self.__default_layer = 4

    def get_surround_tiles(self, position: Vec2):
        tile_position = (int(position.x // self.__tile_size), int(position.y // self.__tile_size))
        rects = []
        for p in SURROUND_POS + DOUBLE_SURROUND:
            check_location = [tile_position[0] + p[0], tile_position[1] + p[1]]
            tile = (self.get_tile_cell(check_location[0], check_location[1]))
            if isinstance(tile, Tile):
                if tile.solid:
                    rects.append(self.get_tile_cell(check_location[0], check_location[1]))
        return rects

    def get_surround_tiles_new(self, position, radius):
        _position = position // self.__tile_size
        rects = []
        for y in range(-radius, radius + 1):
            for x in range(-radius, radius + 1):
                check_location = [_position.x + x, _position.y + y]
                tile = self.get_tile_cell(check_location[0], check_location[1])
                if isinstance(tile, Tile):
                    if tile.solid:
                        rects.append(tile)
        return rects

    def get_tile_cell(self, x: int, y: int, layer: int = 4):
        if (x, y) in self.__tile_data['layer'][layer]:
            tile = self.__tile_data['layer'][layer][(x, y)]
            if tile:
                return tile

    def add_tile_cell(self, x: int, y: int, layer: int = 4, tile: Tile = None):
        pass

    def add_tile(self, tile: Tile):
        self.__tile_data['layer'][tile.layer][(int(tile.position.x), int(tile.position.y))] = tile

    def load_map_from_json(self, room_name: str):
        pass

    def save_room(self) -> dict:
        room_data: dict = {}
        room_data['layers'] = {}
        # get all the tile data
        for i, layer in enumerate(list(self.__tile_data['layer'])):
            tile_list = []
            for tile in list(layer.values()):
                tile_list.append(tile.tile_to_json())
            room_data['layers'][i] = tile_list
        room_data['width'] = self.__tile_data['width']
        room_data['height'] = self.__tile_data['height']
        room_data['tile_size'] = self.__tile_size
        room_data['name'] = "default_level"

        path = self.__resource_paths + '/' + room_data['name'] + '.json'

        with open(path, 'w') as f:
            f.write(json.dumps(room_data))

        print("map saved")

    def autotile(self):
        for i, layer in enumerate(self.__tile_data["layer"]):
            for tile in list(layer.values()):
                if tile:
                    tile.simple_autotile(layer=i)

    def __reset_room(self):
        self.__tile_data = {
            'layer': [{}, {}, {}, {}, {}, {}, {}, {}, {}],
            'decals': [],
            'tile_size': self.__tile_size,
            'width': 128,
            'height': 128

        }
        self.__render_chunks = []

    def load_room_ogmo(self, room_name: str):
        self.__reset_room()
        room_data = self.read_room_data(room_name)
        self.__height = room_data['height'] // 8
        self.__width = room_data['width'] // 8
        for layer in room_data['layers']:
            if 'Layer' in layer['name']:
                data2d = layer["data2D"]
                for y, row in enumerate(data2d):
                    for x, column in enumerate(row):
                        tile_index = data2d[y][x]
                        if tile_index == -1:
                            continue
                        tilesheet = self.__spritesheetmanager.get_spritesheet("tilesetdarkfield")
                        temp_tile = Tile(tile_size=layer['gridCellWidth'],
                                         pos=pygame.Vector2(x, y),
                                         solid=True,
                                         destructable=False,
                                         tileset_name=layer['tileset'],
                                         tile_list = tilesheet,
                                         tile_index=tile_index,
                                         tilemap=self,
                                         scalar=pygame.Vector2(4, 4),
                                         layer=int(layer['name'][-2:]))
                        self.__tile_data['layer'][temp_tile.layer][
                            (temp_tile.position.x, temp_tile.position.y)] = temp_tile
        self.autotile()
        self.chunk_tilemap()

    def load_room(self, room_name: str):
        # This returns a tile data dictionary as seen in  the __init__ function
        room_data = self.read_room_data(room_name)

        for layer in room_data['layer']:
            for tile_list in room_data[layer]:
                for tile_data_dict in tile_list:
                    temp_tile = Tile(tile_size=tile_data_dict['tile_size'],
                                     pos=tile_data_dict['position'],
                                     solid=tile_data_dict['solid'],
                                     destructable=tile_data_dict['destructable'],
                                     tileset_name=tile_data_dict['tileset_name'],
                                     tile_index=tile_data_dict['tile_index'],
                                     scalar=tile_data_dict['scalar'],
                                     layer=tile_data_dict['layer'])
                    self.__tile_data['layer'][temp_tile.layer][(int(temp_tile.position.x), int(temp_tile.position.y))] = temp_tile
        self.autotile()
        self.chunk_tilemap()

    def read_room_data(self, room_name):
        path = self.__resource_paths + '/' + room_name + '.json'
        f = open(path, 'r')
        room_data = json.loads(f.read())
        f.close()
        return room_data

    def chunk_tilemap(self):
        # chunking the grid
        chunk_rows = (self.__height // self.__chunk_size) + 10
        chunk_columns = (self.__width // self.__chunk_size) + 10
        chunk_counter = 0
        # Here we create empty chunks based on the dimension given by the editor
        for index, layer_dict in enumerate(self.__tile_data['layer']):
            chunk_dict = {}
            for row in range(int(chunk_rows)):
                for column in range(int(chunk_columns)):
                    temp = RenderChunk(pygame.Vector2(row, column), self.__chunk_size, self.__tile_size, chunk_counter)
                    chunk_counter += 1
                    chunk_dict[(row, column)] = temp
            self.__render_chunks.append(chunk_dict)

        # Here we go through each layer and give each chunk the corresponding tile data, so it can create its own
        # surfaces to render later on
        for index, layer_dict in enumerate(self.__tile_data['layer']):
            for tile in list(layer_dict.values()):
                chunk_loc = (int(tile.position.x // self.__chunk_size), int(tile.position.y // self.__chunk_size))
                self.__render_chunks[index][chunk_loc].add_tile(tile)
        # Now we generate surfaces for each chunk so rendering becomes more efficient as we batch more tiles together
        for layer in list(self.__render_chunks):
            for chunk in list(layer.values()):
                chunk.generate_chunk_surface()

    def render_tiles_blit(self, surf, offset=pygame.Vector2(0, 0)):
        for layer in self.__tile_data['layer']:
            for tile in list(layer.values()):
                surf.blit(tile.image, tile.pixel_position - offset)

    def render_chunks_blits(self, surf: Surface, offset, position):
        for i, layer in enumerate(self.__render_chunks):
            chunk_sequence = []
            y_chunks = int(surf.get_height() // (self.__chunk_size * self.__tile_size)) + 4
            x_chunks = int(surf.get_width() // (self.__chunk_size * self.__tile_size)) + 4
            for y in range(y_chunks):
                if y < 0:
                    continue
                for x in range(x_chunks):
                    if x < 0:
                        continue
                    target_x = x - 1 + int(math.ceil(offset[0] / (self.__chunk_size * self.__tile_size)))
                    target_y = y - 1 + int(math.ceil(offset[1] / (self.__chunk_size * self.__tile_size)))
                    check_pos = (int(target_x), int(target_y))
                    if check_pos in self.__render_chunks[i]:
                        chunk = layer[check_pos]
                        if chunk.has_tiles():
                            chunk_sequence.append(
                                (chunk.CHUNK_SURFACE, (
                                    chunk.chunk_location.x * chunk.chunk_size * self.__tile_size - offset[0],
                                    chunk.chunk_location.y * chunk.chunk_size * self.__tile_size - offset[1])))
            surf.blits(chunk_sequence)
