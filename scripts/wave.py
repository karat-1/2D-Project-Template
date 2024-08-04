import random

import pygame
import numpy
import random
from scripts.entity import Entity
from scipy.interpolate import interp1d

Point = pygame.Vector2


class Spring:
    def __init__(self, position):
        self.position = pygame.Vector2(position.x, position.y)
        self.target_y = position.y
        self.dampening = 0.05
        self.tension = 0.02
        self.velocity = pygame.Vector2(0, 0)

    def update(self, dt):
        dh = self.target_y - self.position.y
        if abs(dh) < 0.01:
            self.position.y = self.target_y
        self.velocity.y += self.tension * dh - self.velocity.y * self.dampening
        self.position.y += self.velocity.y * dt

    @property
    def rect(self):
        return pygame.Rect(self.position.x, self.position.y, 1, 1)

    def render(self, surface: pygame.Surface, type: str = 'circle'):
        if type == 'rect':
            pygame.draw.rect(surface, (255, 255, 255), self.rect)
        elif type == 'circle':
            pygame.draw.circle(surface, (255, 255, 255), self.position, 1)


class Wave(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.springs: list[Spring] = []
        self.points: list[Point] = []
        self.polysurf: pygame.Surface = pygame.Surface((512, 512))
        self.polysurf.set_colorkey((0, 0, 0))
        self.polysurf.set_alpha(80)
        self.water_color = pygame.Color(kwargs.get('water_color'))
        # self.natural_variance = kwargs.get('natural_variance')
        self.natural_variance = 1
        self.natural_variance_counter = 0

        point_iterations = int(self.size.x // 4)

        for i in range(point_iterations+1):
            self.springs.append(Spring(pygame.Vector2(self.position.x + (i * 4), self.position.y)))

        # this has to be done once otherwise it crashes upon entering a new room
        self.points = [Point(spring.position.x, spring.position.y) for spring in self.springs]

        # water needs to be moved once
        variance = random.randint(-self.natural_variance, self.natural_variance)
        self.springs[random.randint(1, len(self.springs) - 2)].position.y += variance
        self.natural_variance_counter = 0

    def update(self, dt):
        for spring in self.springs:
            spring.update(dt)
        self.spread_wave(dt)
        self.points = [Point(spring.position.x, spring.position.y) for spring in self.springs]
        # self.points = self.get_curve()
        self.points.extend([Point(self.position.x + self.size.x, self.position.y + self.size.y),
                            Point(self.position.x, self.position.y + self.size.y)])

        self.natural_variance_counter += dt
        if self.natural_variance_counter > 60:
            variance = random.randint(-self.natural_variance, self.natural_variance)
            self.springs[random.randint(1, len(self.springs)-2)].position.y += variance
            self.natural_variance_counter = 0

        return True

    def get_curve(self):
        x_new = numpy.arange(self.points[0].x, self.points[-1].x, 1)
        x = numpy.array([i.x for i in self.points[:-1]])
        y = numpy.array([i.y for i in self.points[:-1]])
        f = interp1d(x, y, kind='cubic', fill_value='extrapolate')
        y_new = f(x_new)
        x1 = list(x_new)
        y1 = list(y_new)
        points = [Point(x1[i], y1[i]) for i in range(len(x1))]
        return points

    def spread_wave(self, dt):
        spread = 0.01
        for i, spring in enumerate(self.springs[:-1]):
            if i > 0:
                self.springs[i - 1].velocity.y += (spread * (self.springs[i].position.y - self.springs[i - 1].position.y)) * dt
            try:
                self.springs[i + 1].velocity.y += (spread * (self.springs[i].position.y - self.springs[i + 1].position.y)) * dt
            except IndexError:
                pass
        self.springs[0].position.y = self.springs[0].target_y
        self.springs[-1].position.y = self.springs[-3].target_y

    def set_impact(self, entity):
        if entity.velocity.y != 0:
            for spring in self.springs:
                if entity.rect.collidepoint(spring.position):
                    spring.position.y = entity.rect.bottom

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)

        # rendering the transparent polygon
        self.polysurf.fill((0, 0, 0))
        pygame.draw.polygon(self.polysurf, self.water_color, self.points)
        surf.blit(self.polysurf, (0 - offset[0], 0 - offset[1]))

        # rendering the line
        for point in self.points:
            point.x -= offset[0]
            point.y -= offset[1]
        pygame.draw.lines(surf, (255, 255, 255), False, self.points[:-2], 1)

        # debugging renderering
        # for spring in self.springs:
        #    spring.render(surf, 'rect')
