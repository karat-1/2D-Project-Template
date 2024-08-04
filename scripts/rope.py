import math
import pygame
from scripts.entity import Entity

Vector2 = pygame.Vector2


class Particle:
    def __init__(self, x, y, mass, fixed):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.init_pos_x = x
        self.init_pos_y = y
        self.mass = mass
        self.fixed = fixed

    def set_init_pos(self):
        self.x = self.init_pos_x
        self.y = self.init_pos_y


class Stick:
    def __init__(self, p1, p2, length):
        self.p1 = p1
        self.p2 = p2
        self.length = length


class ParticleRope(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.particles: list[Particle] = []
        self.sticks: list[Stick] = []
        self.gravity = kwargs.get('gravity')
        self.length = kwargs.get('length')
        self.mass = kwargs.get('mass')
        self.color = pygame.Color(kwargs.get('color'))
        self.amount_of_particles = kwargs.get('amount_of_particles')
        self.drag = 0.1
        self.end_x = kwargs.get('end_x')
        self.end_y = kwargs.get('end_y')
        for i in range(self.amount_of_particles):
            self.particles.append(
                Particle(self.position.x, self.position.y + self.length * i, 20, True if i == 0 else False))
        if self.end_x >= 0 and self.end_y >= 0:
            self.particles.append(Particle(self.end_x, self.end_y, self.mass, True))
        for i, particle in enumerate(self.particles):
            if i > 0:
                self.sticks.append(Stick(self.particles[i - 1], self.particles[i], self.length))

    def __get_difference(self, p1: Vector2, p2: Vector2):
        return Vector2(p1.x - p2.x, p1.y - p2.y)

    def __get_length(self, p: Vector2):
        return math.sqrt(p.x * p.x + p.y * p.y)

    def set_impact(self, entity):
        if entity.velocity.x != 0:
            for particle in self.particles:
                if entity.rect.collidepoint((particle.x, particle.y)) and not particle.fixed:
                    particle.x += entity.velocity.x - 0.5

    def __get_distance(self, p1: Particle, p2: Particle):
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        return math.sqrt(dx * dx + dy * dy)

    def move_head(self, position):
        self.particles[0].x += position.x
        self.particles[0].y += position.y
        self.particles[0].init_pos_x += position.x
        self.particles[0].init_pos_y += position.y

    def update(self, dt):
        for particle in self.particles:
            if particle.fixed:
                particle.set_init_pos()
                continue
            force = Vector2(0, self.gravity)
            acceleration = Vector2(force.x / particle.mass, force.y / particle.mass)
            prev_pos = Vector2(particle.x, particle.y)

            particle.x = 2 * particle.x - particle.prev_x + acceleration.x * (dt * dt)
            particle.y = 2 * particle.y - particle.prev_y + acceleration.y * (dt * dt)
            particle.prev_x = prev_pos.x
            particle.prev_y = prev_pos.y

        for stick in self.sticks:
            diff = self.__get_difference(stick.p1, stick.p2)
            diff_factor = (stick.length - self.__get_length(diff)) / self.__get_length(diff) * 0.5
            offset = Vector2(diff.x * diff_factor, diff.y * diff_factor)

            if not stick.p1.fixed:
                stick.p1.x += offset.x
                stick.p1.y += offset.y
            if not stick.p2.fixed:
                stick.p2.x -= offset.x
                stick.p2.y -= offset.y

        return True

    def render(self, surf, offset=(0, 0)):
        super().render(surf)
        points = []
        """for particle in self.particles:
            points.append(Vector2(particle.x, particle.y))
            pygame.draw.circle(surf, (255, 255, 255), Vector2(particle.x, particle.y), 1)"""
        for stick in self.sticks:
            pygame.draw.line(surf, self.color, Vector2(stick.p1.x - offset[0], stick.p1.y - offset[1]),
                             Vector2(stick.p2.x - offset[0], stick.p2.y - offset[1]), 1)
