
class Renderer:
    def __init__(self, game):
        self.game = game

    def render(self):

        """
        Takes the games display surface, gives it to the world to let it render
        all the GameObjects, Tiles and Entities, and then adds all speical FX
        to the Surface (e.g. Bloom, HUD, etc.)
        """

        surf = self.game.window.display
        self.game.world.render(surf)
