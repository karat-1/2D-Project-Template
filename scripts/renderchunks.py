import pygame
from scripts.tile import Tile


class RenderChunk:
    def __init__(self, chunk_location, chunk_size, tile_size, id: int = 0):
        self.chunk_location: pygame.Vector2 = chunk_location
        self.tile_surfaces: list[Tile] = []
        self.chunk_size: int = chunk_size
        self.tile_size: int = tile_size
        height, width = self.tile_size * self.chunk_size, self.tile_size * self.chunk_size
        self.CHUNK_SURFACE = pygame.Surface((height, width)).convert()
        self.CHUNK_SURFACE.set_colorkey((0, 0, 0))

    def add_tile(self, tile) -> None:
        self.tile_surfaces.append(tile)

    def generate_chunk_surface(self) -> None:
        for tile in self.tile_surfaces:
            if tile.image:
                chunk_x = tile.position.x - (self.chunk_location.x * self.chunk_size)
                chunk_y = tile.position.y - (self.chunk_location.y * self.chunk_size)
                self.CHUNK_SURFACE.blit(tile.image, (chunk_x * self.tile_size, chunk_y * self.tile_size))

    def has_tiles(self) -> bool:
        if len(self.tile_surfaces) > 0:
            return True
        else:
            return False
