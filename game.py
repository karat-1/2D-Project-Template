from scripts.contentmanager_new import ContentManager
from scripts.input import Input
from scripts.renderer import Renderer
from scripts.window import Window
from scripts.simple_world import SimpleWorld


class Game:
    def __init__(self):
        self.window = Window(self)
        self.input = Input(self)
        self.content_manager = ContentManager()
        self.renderer = Renderer(self)
        self.world = SimpleWorld(self)
        self.world.init_world()

    def update(self):
        self.input.update()
        self.world.update()
        self.renderer.render()
        self.window.render_frame()

    def run(self):
        while True:
            self.update()


# Entrypoint
Game().run()
