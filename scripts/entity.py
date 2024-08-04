from copy import deepcopy
from pygame import Vector2, Rect, Surface
from scripts.engine_core_funcs import *


class Entity:
    """
    This behemoth of a class is the main entity class. An entity is an in any form interactable object such as:
    enemies, npcs, moving platforms, items, weapons, crates, the player_entities, doors etc.
    This class provides the main functionality that should be shared between all entities such as collision, movement,
    sprite and mask properties, mathematical functions, rendering and the update loop.
    """

    def __init__(self, game, position: Vector2, controllable: bool = False, *args, **kwargs):
        """
        Sets up the basic Entity with default values

        :param game: For accessing important systems throughout the game
        :param size: pixel size of the object as (w, h)
        :param entity_type: type as str
        :param controller: If it is controllable or not
        """

        self.game = game
        self.position: Vector2 = deepcopy(position)
        self.size: Vector2 = Vector2(kwargs.get('width'), kwargs.get('height'))
        self.type: int = 0
        self.creator: str = kwargs.get('creator')
        self.id: str = kwargs.get('id')
        self.category: str = 'default'
        self.flip: list[bool] = [False, False]
        self.centered: bool = False
        self.alive: bool = True
        self.can_rotate: bool = False
        self.face: list[int] = [1, 0]
        self.scale: list[int] = [1, 1]
        self.opacity: int = 255
        self.rotation: float = kwargs.get('rotation')
        self.gravity: float = .19
        self.velocity: Vector2 = Vector2(0, 0)
        self.fractals: Vector2 = Vector2(0, 0)
        self.final_velocity: Vector2 = Vector2(0, 0)
        self.gravity_timer: int = 0
        self.controllable = controllable
        self.em = self.game.world.get_entity_manager()
        self.active_animation: None
        self.current_image: Surface = None
        self.image_base_dimensions = None
        self.render_priority = 0
        self.active_animation = None
    @property
    def img(self) -> Surface:
        if not self.active_animation:
            img = self.current_image
        else:
            self.set_image(self.active_animation.get_current_animation_frame())
            img = self.current_image
        if self.scale != [1, 1]:
            img = pygame.transform.scale(img, (
                int(self.scale[0] * self.image_base_dimensions[0]), int(self.scale[1] * self.image_base_dimensions[1])))
        if any(self.flip):
            img = pygame.transform.flip(self.current_image, self.flip[0], self.flip[1])
        if self.opacity != 255:
            img.set_alpha(self.opacity)
        return img

    @property
    def rect(self) -> Rect:
        if not self.centered:
            return pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
        else:
            return pygame.Rect((self.position.x - self.img.get_width()) // 1, (self.position.y - self.img.get_width()) // 1, self.img.get_width(), self.img.get_height())

    @property
    def ground_check(self) -> pygame.Rect:
        return pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y + 1)

    @property
    def center(self) -> Vector2:
        return Vector2(self.position.x + self.size.x // 2, self.position.y + self.size.y // 2)

    def set_animation(self, action_id: str, force=False, entity_name: str = "maincharacter", should_loop=True) -> None:
        """
        Sets the entitiys" animation
        :param entity_name:
        :param action_id: animation name or id as string
        :param force: if the animation should be forced or not
        :return: Nothing
        """
        if force:
            self.active_animation = self.game.content_manager.get_animation(entity_name, action_id)
            self.active_animation.set_loop(should_loop)

    def set_image(self, surf: pygame.Surface = False, image_name: str = None):
        """
        Sets the current images base dimensions
        :param surf: pygame surface
        :param image_name: string
        :return: Nothing
        """
        if surf:
            self.current_image = surf.copy()
            self.image_base_dimensions = list(surf.get_size())
        else:
            self.current_image = (self.game.content_manager.get_static_image(image_name))

    def calculate_fractions(self):
        self.final_velocity = self.velocity + self.fractals

        self.fractals.x = self.final_velocity.x - ((abs(self.final_velocity.x) * sign(self.final_velocity.x))//1)
        self.final_velocity.x -= self.fractals.x

        self.fractals.y = self.final_velocity.y - ((abs(self.final_velocity.y) * sign(self.final_velocity.y)) // 1)
        self.final_velocity.y -= self.fractals.y


    def reset_fractions(self):
        self.fractals = pygame.Vector2(0, 0)

    def set_scale(self, new_scale: int, fit_hitbox=True):
        """
        Takes in a scale and multiplies that value by the images base dimensions to scale it up
        :param new_scale: new scale as integer value
        :param fit_hitbox: bool to check wether the new scale should fit the base dimension
        :return: Nothing
        """
        try:
            self.scale = deepcopy(new_scale)
        except AttributeError:
            self.scale = [new_scale, new_scale]
        if fit_hitbox:
            self.size = self.size = [int(self.scale[0] * self.image_base_dimensions[0]),
                                     int(self.scale[1] * self.image_base_dimensions[1])]

    def get_angle(self, target):
        """
        Return the arc tangent (measured in radians) of y/x between 2 entities
        :param target: entity object
        :return: arc tangent
        """
        if isinstance(target, Entity):
            return math.atan2(target.rect.center[1] - self.rect.center[1], target.center[0] - self.rect.center[0])
        else:
            return math.atan2(target[1] - self.rect.center[1], target[0] - self.rect.center[0])

    def init_self(self):
        pass

    def get_render_angle(self, target):
        """
        calculates the render angle of an entity
        :param target:
        :return: the render angle of an entity
        """
        if isinstance(target, Entity):
            return math.atan2(target.center[1] - self.center[1], target.center[0] - self.center[0] - self.size.y)
        else:
            return math.atan2(target[1] - self.center[1], target[0] - self.center[0] - self.size.y)

    def get_distance(self, target):
        """
        :param target: Entity object
        :return: The distance between 2 entities
        """
        try:
            return math.sqrt((target.position.x - self.position.x) ** 2 + (target.position.y - self.position.y) ** 2)
        except:
            return math.sqrt((target[0] - self.position.x) ** 2 + (target[1] - self.position.y) ** 2)

    def in_range(self, target, entity_range) -> bool:
        """
        Checks wether or not an entity is within the provided range
        :param target: target entity
        :param entity_range: the range to check
        :return: True or False as in wetheror not the entity is in the specified range
        """
        return self.get_distance(target) <= entity_range

    def destroy(self):
        pass

    def damage(self, amount):
        pass

    def render(self, surf: pygame.Surface, offset=(0, 0)) -> None:
        """
        The rendering function of an entity.
        :param surf: the surface to which the entity should be blitted to
        :param offset: a tuple containing the offset in pixels
        :return: Nothing
        """
        offset = self.calculate_render_offset(offset)
        if self.img:
            if not self.can_rotate:
                surf.blit(self.img, ((int(self.position[0]) - offset[0]), (int(self.position[1]) - offset[1] - self.size.y)))
            else:
                rotated_img = pygame.transform.rotate(self.img, self.rotation)
                surf.blit(rotated_img, (self.position.x - int(rotated_img.get_width() / 2) - offset[0], self.position[1] - int(rotated_img.get_height() / 2) - offset[1]))

    def update(self, dt) -> Union[bool, None]:
        """
        The update loop of an entity. This function usually gets inherited or overwritten
        :param dt: delta time
        :return: True
        """
        if not self.alive:
            return
        if self.active_animation:
            self.active_animation.play(dt)
        return self.alive

    def calculate_render_offset(self, offset=(0, 0)):
        """
        :param offset:
        :return:
        """
        offset = list(offset)
        if self.active_animation:
            offset[0] += self.active_animation.get_offset()[0]
            offset[1] += self.active_animation.get_offset()[1]
        return offset
