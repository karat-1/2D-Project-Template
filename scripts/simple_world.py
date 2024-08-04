import pygame

from scripts.entitytesting import Manager
from scripts.hitbox_manager import HitboxManager
from scripts.spritesheets import SpritesheetManager
from scripts.background import BackgroundManager, Background
from scripts.tilemap import Tilemap
import json
from scripts.engineconstants import RESOURCEPATHS


class SimpleWorld:
    """
    A class which holds the whole Update loop and all variables, objects etc.
    """

    def __init__(self, game) -> None:
        self.master_clock: float = 0.0
        self.__tile_size = 8
        self.__resource_paths = RESOURCEPATHS['rooms']
        self.entities: Manager = None
        self.content: game.content_manager = None
        self.sh_manager: SpritesheetManager = None
        self.hitbox_manager: HitboxManager = None
        self.background: Background = None
        self.background_manager: BackgroundManager = None
        self.tilemap: Tilemap = None
        self.game = game
        self.scroll = [0, 0]
        self.render_scroll = [0, 0]
        self.restrict_rect = None
        self.active_room = None

    def init_world(self):
        self.content = self.game.content_manager
        self.sh_manager = self.content.get_sprite_sheet_manager()
        self.background_manager = self.content.get_background_manager()
        self.hitbox_manager = HitboxManager(self.game)
        self.background = Background(self.game)
        self.entities = Manager(self.game)
        self.tilemap = Tilemap(smanager=self.sh_manager)
        self.load_world(True)

    def load_world(self, generate_room: bool = False, room_name: str = 'biome_00_00'):
        room_data = self.read_room_data(room_name)
        self.active_room = room_name
        self.background.load_background(self.background_manager.get_backgrounds(room_data['values']['bg_name']), offset=(0, 0))
        self.tilemap.load_room_ogmo(room_name)
        self.entities.init_entities(room_name)
        self.hitbox_manager.init_manager()
        # the restriction should be saved inside the level data
        self.restrict_rect = pygame.Rect(8, 8, room_data['width'] - 16, room_data['height'] - 16)

    def update(self) -> None:
        """
        This is the game loop. If we have new mechanics, objects or systems that need to be updated
        then this has to be done here.
        :return: Nothing
        """

        self.update_camera()
        self.entities.update()
        self.hitbox_manager.update()
        self.master_clock += self.game.window.dt

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.load_world(room_name=self.active_room)

    def render(self, surf: pygame.Surface) -> None:
        """
        The world renderings function only important purpose is to render every entity or object
        that is part of a level to a surface. E.g. NPCs, players, enemies, items, particles etc.
        This is the main render function which gets called from the renderer. As of right now
        the Background (e.g. everything that uses parallax is not directly part of the world and is rendered
        before the world gets blitted to the surface)
        :param surf: The surface which everything should be blit too
        :return: None
        """
        self.background.render(surf, self.render_scroll)
        self.tilemap.render_tiles_blit(surf, self.render_scroll)
        # self.tilemap.render_chunks_blits(surf, self.render_scroll, pygame.Vector2(0, 0))
        self.entities.render(surf)
        self.hitbox_manager.render(surf, self.render_scroll)

    def get_entity_manager(self):
        return self.entities

    def update_camera(self):
        # Camera code, maybe needs to end up in its own object once its figured out
        self.scroll[0] += (self.entities.player.rect.centerx - self.game.window.display.get_width() / 2 - self.scroll[
            0])
        self.scroll[1] += (self.entities.player.rect.centery - self.game.window.display.get_height() / 2 - self.scroll[
            1])
        if self.restrict_rect:

            if self.scroll[0] + self.game.window.display.get_width() > self.restrict_rect.right:
                self.scroll[0] = self.restrict_rect.right - self.game.window.display.get_width()

            if self.scroll[0] < self.restrict_rect.left:
                self.scroll[0] = self.restrict_rect.left

            if self.scroll[1] < self.restrict_rect.top:
                self.scroll[1] = self.restrict_rect.top

            if self.scroll[1] + self.game.window.display.get_height() > self.restrict_rect.bottom:
                self.scroll[1] = self.restrict_rect.bottom - self.game.window.display.get_height()

        self.render_scroll = [int(self.scroll[0]), int(self.scroll[1])]

    def read_room_data(self, room_name):
        path = self.__resource_paths + '/' + room_name + '.json'
        f = open(path, 'r')
        room_data = json.loads(f.read())
        f.close()
        return room_data
