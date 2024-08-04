import pygame
from scripts.entity import Entity
import random
from scripts.engine_dataclasses import ENTITYTYPES


class ParticleEmitter(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.particles: list[Particle] = []
        self.emitter_position: pygame.Vector2 = kwargs.get('position')
        self.spawn_rate = kwargs.get('spawn_rate')
        self.spawn_timer = 0
        self.master_clock = 0
        self.type = ENTITYTYPES.particle_system
    def add_particle(self):
        pass

    def update(self, dt):
        pass


class Particle:
    """
    This class only holds the data for a particle, the emitter itself is doing the operation on this set of data
    instead of self.
    """

    def __init__(self, position: pygame.Vector2, velocity: pygame.Vector2, timer: int, decrement: int):
        self.position: pygame.Vector2 = position
        self.velocity: pygame.Vector2 = velocity
        self.timer: int = timer
        self.timer_decrement: int = decrement
        self.sine_offset = random.uniform(0.2, 0.8)
        self.particle_clock = 0
        self.particle_clock_increment = random.uniform(0.1, 0.4)
