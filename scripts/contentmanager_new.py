from scripts.animations_new import AnimationManager
from scripts.spritesheets import SpritesheetManager
from scripts.thumbnailmanager import ThumbnailManager
from scripts.background import BackgroundManager


class ContentManager:

    def __init__(self):
        self.__animations = AnimationManager()
        self.__sprite_sheet_manager = SpritesheetManager()
        self.__thumbnail_manager = ThumbnailManager()
        self.__background_manager = BackgroundManager()
        self.load_assets()

    def load_assets(self):
        self.__animations.load_animations()
        self.__sprite_sheet_manager.load_spritesheets()
        self.__thumbnail_manager.load_thumbnails()
        self.__background_manager.load_backgrounds()

    def get_sprite_sheet_manager(self):
        return self.__sprite_sheet_manager

    def get_animation_manager(self):
        return self.__animations

    def get_background_manager(self):
        return self.__background_manager

    def get_thumbnail_manager(self):
        return self.__thumbnail_manager

    def get_thumbnail(self, name: str):
        return self.__thumbnail_manager.get_thumbnail(name)

    def get_animation(self, character_id, animation_id):
        return self.__animations.get_animation(character_id, animation_id)

    def get_animation_array(self, character_id, animation_id):
        return self.__animations.get_animation_array(character_id, animation_id)