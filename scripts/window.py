import time
import pygame


class Window:
    """
    The Window class holds all necessary information about the Pygame Window, base resolution
    scaled resolution, scale ratio, the surfaces etc. Once everything as been blitted to the display
    surface in the renderers class rendering function, the Render function from this class gets called
    and the final image is getting blitted to the screen
    """

    def __init__(self, game) -> None:
        """
        :param game: Game Object
        """
        self.ms = 0
        self.game = game
        self.dt = 0.1
        self.clock = pygame.time.Clock()
        self.TAGET_FPS = 60
        self.debug_dt = False
        self.tick = 65

        pygame.init()
        self.base_resolution = [128, 128]
        self.window_resolution = [512, 512]
        self.scale_ratio = [1, 1]
        self.offset = [0, 0]
        self.background_color = (60, 58, 114)

        self.screen = pygame.display.set_mode(self.window_resolution)
        # self.screen = pygame.display.set_mode(self.base_resolution, pygame.SCALED | pygame.RESIZABLE)
        # self.window = pygame._sdl2.video.Window.from_display_module().size = (1280, 720)
        pygame.display.set_caption('Samurai Microvania')
        pygame.mouse.set_visible(True)
        self.display = pygame.Surface((self.base_resolution[0] - self.offset[0] * 2, self.base_resolution[1] - self.offset[1] * 2))

        self.frame_history = [0.01]
        self.frame_start = time.time()

        self.cursor_id = 'cursor'
        self.freeze_frame = {}

    def render_frame(self) -> None:
        """
        This function gets called after the renderer is finished blitting the image. The display
        surface gets blitted to the screen. Also deltaTime gets calculated in here
        :return:
        """

        # THIS IS SLOW AF
        # self.screen.blit(pygame.transform.scale(self.display, (int(self.display.get_width() * self.scale_ratio[0]), int(self.display.get_height() * self.scale_ratio[1]))), (self.offset[0] * self.scale_ratio[0],self.offset[1] * self.scale_ratio[1]))

        # THIS IS FAST AF WITH SCALED
        # self.screen.blit(self.display, self.offset)

        # This is the best of both I guess
        pygame.transform.scale_by(self.display, (self.window_resolution[0] // self.base_resolution[0],
                                                 self.window_resolution[1] // self.base_resolution[1]), self.screen)
        # pygame.transform.scale(self.display, (6, 6), self.screen)

        pygame.display.update()

        self.dt = self.clock.tick(self.tick) * .001 * self.TAGET_FPS
        self.dt = min(max(0.0001, self.dt), 1)
        self.display.fill(self.background_color)
        pygame.display.set_caption(f'playground - {int(self.clock.get_fps())}fps')
