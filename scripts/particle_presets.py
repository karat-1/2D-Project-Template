import pygame

from scripts.particle_emitter import ParticleEmitter, Particle
import random


class WindParticle(ParticleEmitter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vertical_range: int = kwargs.get('vertical_range')
        self.from_right = kwargs.get('from_right')
        self.content_manager = self.game.world.content
        self.animation_array = self.content_manager.get_animation_array('particle_leaf', 'default_animation').get_frames()
        print(self.animation_array)

    def add_particle(self):
        # random position in a given range
        if self.vertical_range != 0:
            random_y = random.randint(0, self.vertical_range) // 2
        else:
            random_y = self.emitter_position.y
        position = pygame.Vector2(self.emitter_position.x, random_y)

        # random velocity either from the left or right
        if self.from_right:
            velocity = pygame.Vector2(random.uniform(0.6, 1) * -1, random.uniform(-0.5, 0.1))
        else:
            velocity = pygame.Vector2(random.uniform(0.6, 1.2), 0)

        # add particle to list
        self.particles.append(Particle(position, velocity, 1, .001))

    def update(self, dt):
        if self.spawn_timer > self.spawn_rate:
            self.add_particle()
            self.spawn_timer = 0
        self.spawn_timer += dt
        self.master_clock += dt
        if self.master_clock > len(self.animation_array):
            self.master_clock = 0

        for i, particle in enumerate(self.particles):
            particle.position.x += particle.velocity.x * dt
            particle.position.y += particle.sine_offset * dt
            particle.timer -= particle.timer_decrement * dt
            particle.particle_clock += particle.particle_clock_increment * dt

            if particle.timer <= 0:
                self.particles.pop(i)
            if particle.particle_clock > len(self.animation_array):
                particle.particle_clock = 0

        return True

    def render(self, surf: pygame.Surface, offset):
        for particle in self.particles:
            # pygame.draw.circle(surf, (255, 255, 255), particle.position, particle.timer)
            if self.content_manager:
                surf.blit(self.animation_array[int(particle.particle_clock)], (particle.position.x - offset[0], particle.position.y - offset[1]))
            else:
                pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(particle.position.x - offset[0], particle.position.y - offset[1], 1, 1))
