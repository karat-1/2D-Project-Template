import pygame
import uuid
from scripts.engine_dataclasses import ENTITYTYPES


class HitBox:
    def __init__(self, entity, position, size, game, duration=15, decrement=0.5):
        self.game = game
        self.position = position
        self.entity = entity
        self.creator_id = entity.id
        self.size = size
        self.hit_entities = []
        self.dmg = 1
        self.duration = duration
        self.decrement = decrement
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)

    def __add_hit_entity(self, entity):
        self.hit_entities.append(entity.id)

    def check_collision(self, entity):
        if self.rect.colliderect(entity.rect) and entity.id not in self.hit_entities and entity.id != self.creator_id:
            entity.damage(self.dmg)
            self.__add_hit_entity(entity)

    def update(self):
        horizontal_difference = self.entity.position.x - self.position.x
        vertical_difference = self.entity.position.y - self.position.y
        self.position.x += horizontal_difference
        self.position.y += vertical_difference
        self.duration -= self.decrement
        if self.duration <= 0:
            self.alive = False


class HitboxManager:
    def __init__(self, game):
        self.game = game
        self.hitboxes_list: list[HitBox] = []
        self.entity_manager = None
        self.debug = False

    def init_manager(self):
        self.entity_manager = self.game.world.entities

    def create_hitbox(self, entity, position, size, duration=15):
        hitbox = HitBox(entity, position, size, self.game, duration=duration)
        self.hitboxes_list.append(hitbox)

    def update(self):
        for i, hitbox in enumerate(self.hitboxes_list):
            if hitbox.alive:
                hitbox.update()
            else:
                self.hitboxes_list.pop(i)
        self.check_for_collisions()

    def check_for_collisions(self):
        # hitbox entity collision
        for hitbox in self.hitboxes_list:
            for entity in self.entity_manager.get_all_entities():
                if entity.type == ENTITYTYPES.actor:
                    hitbox.check_collision(entity)

        # hitbox hitbox collision
        # when programming a parry system i need to check the interaction
        # between other entities (projectiles) and hitboxes

    def render(self, surf, offset):
        if self.debug:
            for hitbox in self.hitboxes_list:
                rect = (hitbox.position.x - offset[0], hitbox.position.y - offset[1], hitbox.rect.width, hitbox.rect.height)
                pygame.draw.rect(surf, (255, 0, 0), rect)
