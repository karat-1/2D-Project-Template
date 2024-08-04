from typing import Union

import pygame
from pygame import Vector2
from scripts.entity import Entity
from scripts.tile import Tile
from scripts.engine_dataclasses import ENTITYTYPES


class Actor(Entity):
    def __init__(self, game, position: Vector2, controllable: bool = False, *args, **kwargs):
        super().__init__(game, position, controllable, *args, **kwargs)
        self.hurt: int = 0
        self.max_health: int = 1
        self.health: int = self.max_health
        self.tile_data = kwargs.get('tile_data')
        self.tiles: list[Tile] = []
        self.on_ground: bool = False
        self.debug = True
        self.requests = {}
        self.type = ENTITYTYPES.actor
        self.hb_manager = self.game.world.hitbox_manager

    @property
    def ground_check(self) -> pygame.Rect:
        return pygame.Rect(self.position.x, self.position.y, self.img.get_width(), self.img.get_height() + 1)

    def destroy(self):
        if self.health <= 0:
            self.alive = 0

    def damage(self, amount):
        self.health -= amount
        self.destroy()

    def add_request(self):
        pass

    def move(self, dt: float) -> dict:
        """
        This function moves the entity object and returns a dictionary containing the info of which side collided with a collider object
        :param dt: deltaTime as float
        :return: A dictionary of collision types as specified 2 lines below
        """
        collision_types = {'top': False, 'bottom': False, 'left': False, 'right': False}
        self.tiles.clear()
        self.tiles = self.tile_data.get_surround_tiles(self.center)
        # oneway_colliders = self.em.get_oneway_colliders()
        # self.tiles = self.tiles + oneway_colliders

        self.calculate_fractions()
        self.position.x += self.final_velocity.x * dt
        if self.final_velocity.x != 0:
            for tile in self.tiles:
                if self.final_velocity.x > 0:
                    if tile.rect.colliderect(self.rect):
                        self.position.x = tile.rect.left - self.rect.width
                        self.final_velocity.x = 0
                        collision_types['right'] = True
                        break
                elif self.final_velocity.x < 0:
                    if tile.rect.colliderect(self.rect):
                        self.position.x = tile.rect.right
                        self.final_velocity.x = 0
                        collision_types['left'] = True
                        break

        self.position.y += self.final_velocity.y * dt
        for tile in self.tiles:
            if self.final_velocity.y > 0:
                if tile.rect.colliderect(self.rect):
                    self.position.y = tile.rect.top - self.rect.height
                    self.final_velocity.y = 0
                    collision_types['bottom'] = True
                    break
            elif self.final_velocity.y < 0:
                if tile.rect.colliderect(self.rect):
                    self.position.y += tile.rect.bottom - self.rect.top
                    self.final_velocity.y = 0
                    collision_types['top'] = True
                    break

        if len(self.tiles) > 0:
            for tile in self.tiles:
                new_rect = pygame.Rect(self.position.x, self.position.y + 1, self.size.x, self.size.y)
                if tile.rect.colliderect(new_rect):
                    self.on_ground = True
                    break
                else:
                    self.on_ground = False
        else:
            self.on_ground = False

        return collision_types

    def update(self, dt) -> Union[bool, None]:
        r = super().update(dt)
        if self.hurt:
            self.hurt = max(0, self.hurt - dt * 3)
        if self.alive:
            return True

    def check_water_collisions(self):
        water_objs = self.em.get_entities_by_type('Wave')
        for wave in water_objs:
            wave.set_impact(self)

    def check_rope_collisions(self):
        rope_objs = self.em.get_entities_by_type('ParticleRope')
        for rope in rope_objs:
            rope.set_impact(self)

    def render(self, surf: pygame.Surface, offset=(0, -8)) -> None:
        super().render(surf, offset)
        if self.debug:
            for tile in self.tiles:
                rect = pygame.Rect(tile.rect.x - 8, tile.rect.y - 8, 8, 8)
                pygame.draw.rect(surf, (0, 255, 0), rect, 1)
