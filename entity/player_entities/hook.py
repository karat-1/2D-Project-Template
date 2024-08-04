from scripts.entity import Entity
import pygame
from scripts.engine_core_funcs import approach


class Hook(Entity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = kwargs.get('creator')
        self.velocity = kwargs.get('velocity')
        self.__range = 4.5
        self.__x_shift = 0
        self.position = self.player.center
        self.__origin_position = self.position
        self.tiles = []
        self.tile_data = self.player.tile_data
        self.__speed_mult = 0.3
        self.position.y -= 0
        self.set_animation('default_animation', True, 'samurai_hook', True)
        if self.velocity[0] < 0:
            self.flip[0] = True

    def update(self, dt):
        self.__x_shift += (self.velocity.x * self.__speed_mult) * dt
        if abs(self.__x_shift) > self.__range:
            self.player.continue_movement()
            return False
        ct = self.move(dt)
        if True in ct.values():
            self.player.pull_player(self)
        return self.alive

    def move(self, dt):
        collision_types = {'top': False, 'bottom': False, 'left': False, 'right': False}
        self.tiles.clear()
        self.tiles = self.tile_data.get_surround_tiles(self.center)
        # oneway_colliders = self.em.get_oneway_colliders()
        # self.tiles = self.tiles + oneway_colliders

        if self.velocity.x != 0:
            self.position.x = (self.__origin_position.x + self.__x_shift)
            for tile in self.tiles:
                if self.velocity.x > 0:
                    if tile.rect.colliderect(self.rect):
                        self.position.x = tile.rect.left - self.rect.width
                        self.velocity.x = 0
                        collision_types['right'] = True
                        self.player.continue_movement()
                        break
                elif self.velocity.x < 0:
                    if tile.rect.colliderect(self.rect):
                        self.position.x = tile.rect.right
                        self.velocity.x = 0
                        collision_types['left'] = True
                        self.player.continue_movement()
                        break

        return collision_types

    def flip_dir(self):
        """
        This function is called if the projectile gets hit by something that isnt a tile, e.g. a
        parry hitbox or an enemy
        :return:
        """
        pass

    def hit_entity(self, entity):
        pass

    def render(self, surf: pygame.Surface, offset=(0, 0)) -> None:
        pygame.draw.line(surf, (255, 255, 255),
                         (self.position.x - offset[0], self.position.y - offset[1] - 2),
                         (self.player.center.x - offset[0], self.position.y - offset[1] - 2))
        super().render(surf, offset)
