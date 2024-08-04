from typing import Union

from scripts.entity import Entity

class Door(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_room = kwargs.get('next_room')


    def update(self, dt) -> Union[bool, None]:
        if self.game.world.entities.player.rect.colliderect(self.rect):
            self.em.add_callback(self.change_room)
        return super().update(dt)

    def change_room(self):
        self.game.world.load_world(room_name=self.next_room)