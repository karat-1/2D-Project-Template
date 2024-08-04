import uuid
import json
import pygame

from scripts.engineconstants import INSTANTIABLE_OBJECTS, RESOURCEPATHS
from entity.player_entities.player import Player


class Manager:
    def __init__(self, game):
        self.game = game
        self.player = None
        self.__resource_paths = RESOURCEPATHS['rooms']
        self.list_of_objects = {}
        self.list_of_instantiable_objects = INSTANTIABLE_OBJECTS
        self.hb_manager = self.game.world.hitbox_manager
        self.runtime_added_entities = []
        self.callbacks_post_update = []

    def create_object(self, object_class_name: str, parameter: dict, return_object=False):
        parameter['game'] = self.game
        parameter['creator'] = "Manager"
        parameter['position'] = pygame.Vector2(parameter['x'], parameter['y'])
        parameter['tile_data'] = self.game.world.tilemap
        parameter = {**parameter, **parameter['values']}
        instantiable_object = self.list_of_instantiable_objects[object_class_name]
        temp_obj = instantiable_object(**parameter)
        # TODO: check can be made simplified
        if temp_obj.__class__.__name__ in self.list_of_instantiable_objects.keys():
            self.__add_entity(temp_obj)
            if object_class_name == "Player":
                self.player = temp_obj
        if return_object:
            return temp_obj

    def init_entities(self, room_name: str):
        self.list_of_objects = {}
        self.list_of_instantiable_objects = INSTANTIABLE_OBJECTS
        room_data = self.read_room_data(room_name)
        entities_to_init = None
        for layer in room_data["layers"]:
            if layer['name'] == "Entities":
                entities_to_init = layer['entities'] # list of entities where each entity is a dict

        for entity_data in entities_to_init:
            self.create_object(entity_data['name'], entity_data)

    def read_room_data(self, room_name):
        path = self.__resource_paths + '/' + room_name + '.json'
        f = open(path, 'r')
        room_data = json.loads(f.read())
        f.close()
        return room_data

    def gen_player(self) -> None:
        pass

    def set_player(self, player, pos: pygame.Vector2):
        pass

    def init_player(self, position: pygame.Vector2, cave):
        self.player = Player(game=self.game,
                             position=position,
                             controllable=True,
                             size=pygame.Vector2(16, 16),
                             creator="Manager",
                             id=str(uuid.uuid4()))
        self.__add_entity(self.player)

    def update(self):
        for entity_type in self.list_of_objects:
            for i, entity in enumerate(self.list_of_objects[entity_type]):
                alive = entity.update(self.game.window.dt)
                if not alive:
                    self.list_of_objects[entity_type].pop(i)
        for entity in self.runtime_added_entities:
            self.__add_entity(entity)
        self.runtime_added_entities.clear()

        for callback in self.callbacks_post_update:
            callback()

        self.callbacks_post_update.clear()

    def __add_entity(self, entity):
        if entity.__class__.__name__ in self.list_of_objects.keys():
            self.list_of_objects[entity.__class__.__name__].append(entity)
        else:
            self.list_of_objects[entity.__class__.__name__] = [entity]

    def add_entity(self, entity):
        self.runtime_added_entities.append(entity)

    def add_callback(self, callback):
        self.callbacks_post_update.append(callback)

    def get_all_entities(self):
        all_entities = []
        for list_of_entities in self.list_of_objects.values():
            all_entities.extend(list_of_entities)
        return all_entities

    def get_entities_by_type(self, entity_type: str):
        try:
            return self.list_of_objects[entity_type]
        except KeyError:
            return []
    def render(self, surf, front=False):
        front = []
        for entity_type in self.list_of_objects:
            for entity in self.list_of_objects[entity_type]:
                if entity.render_priority:
                    front.append(entity)
                    continue
                entity.render(surf, self.game.world.render_scroll)
        for entity in front:
            entity.render(surf, self.game.world.render_scroll)
