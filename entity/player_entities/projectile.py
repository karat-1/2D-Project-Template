from scripts.entity import Entity
from scripts.engine_core_funcs import *
from scripts.config import config
import pygame


class Projectile(Entity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config['projectiles'][self.type]
        self.speed = self.config['speed']
        self.collision_types = {}
        self.damage = 1
        self.reverse_dir = 1
        self.hit_entities = {}
        self.hit_hitboxes = {}
        self.set_animation('throw', True)
        self.render_angle = 360 - self.rotation
        self.shooting_angle = self.rotation
        self.rotation = self.render_angle
        self.centered = True
        self.can_rotate = True

    def update(self, dt):
        collisions = self.move(dt)
        if any(collisions.values()):
            self.alive = False
        ent_list = self.game.world.entities.get_entities_by_type('player_entities,enemy') # no whitespaces, needs bugfixing
        for entity in ent_list:
            try:
                if entity.attack and self.rect.colliderect(entity.attack.rect) and entity.attack.id not in self.hit_hitboxes:
                    self.hit_hitboxes[entity.attack.id] = False
                    self.alive = False
                    entity.parry.set_state(True)
                elif entity.parry and self.rect.colliderect(entity.parry.rect) and entity.parry.id not in self.hit_hitboxes:
                    self.hit_hitboxes[entity.parry.id] = False
                    self.flip_dir()
                    self.creator = entity.id
                elif entity.block and self.rect.colliderect(entity.block.rect):
                    self.alive = False
                    entity.parry.set_state(True)
                elif self.rect.colliderect(entity.parry.rect):
                    if entity.id not in self.hit_entities:
                        self.hit_entities[entity.id] = entity
                        entity.damage(self.damage)
            except AttributeError:
                if entity.rect.colliderect(self.rect) and entity.id != self.creator:
                    if entity.id not in self.hit_entities:
                        self.hit_entities[entity.id] = entity
                        entity.damage(self.damage)
        # print('Render Angle: ' + str(self.render_angle) + ' ' + 'Rotation :' + str(self.rotation) + ' ' + 'shooting angle: ' + str(self.shooting_angle))
        return self.alive

    def move(self, dt):
        directions = {k: False for k in ['top', 'left', 'right', 'bottom']}
        hsp = math.cos(math.radians(self.shooting_angle)) * self.speed * dt * self.reverse_dir
        vsp = math.sin(math.radians(self.shooting_angle)) * self.speed * dt * self.reverse_dir


        if self.game.world.tile_map.get_tile(self.rect.center, self.collision_layer):
            if hsp > 0:
                directions['right'] = True
            else:
                directions['left'] = True
            return directions
        self.pos[0] += hsp

        if self.game.world.tile_map.get_tile(self.rect.center, self.collision_layer):
            if vsp > 0:
                directions['bottom'] = True
            else:
                directions['top'] = True
        self.pos[1] += vsp
        return directions

    def flip_dir(self):
        """
        This function is called if the projectile gets hit by something that isnt a tile, e.g. a
        parry hitbox or an enemy
        :return:
        """
        self.reverse_dir *= -1

    def hit_entity(self, entity):
        if entity.id not in self.hit_entities:
            self.hit_entities[entity.id] = entity
            return False

    def render(self, surf: pygame.Surface, offset=(0, -10)) -> None:
        super().render(surf, offset)
        pygame.draw.rect(surf, (255, 0, 0), pygame.Rect(self.rect.x - offset[0], self.rect.y - offset[1], self.img.get_width(), self.img.get_height()), 1)
