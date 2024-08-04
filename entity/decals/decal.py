from copy import copy
from typing import Union

from scripts.entity import Entity


class Decals(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sprite_name = kwargs.get('sprite_name')
        self.sprite_animation = kwargs.get('sprite_animation')
        self.sprite_speed = kwargs.get('sprite_speed')
        self.set_animation(self.sprite_animation, True, self.sprite_name, should_loop=True)


class ActorDecals(Decals):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.creator = kwargs.get('creator')
        self.centered = False
        self.__center_decal()
        self.set_animation(self.sprite_animation, True, self.sprite_name, should_loop=False)

    def update(self, dt) -> Union[bool, None]:
        self.position = copy(self.creator.position)
        self.__center_decal()
        if self.active_animation.is_done():
            self.alive = False
            self.active_animation.rewind()
        return super().update(dt)

    def set_direction(self, face, flip):
        self.face = face
        self.flip = flip

    def __center_decal(self):
        self.position.x = self.position.x - self.size.x // 2
        self.position.y = self.position.y + self.size.y // 2
