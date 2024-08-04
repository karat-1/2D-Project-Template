import uuid

import pygame
import math
import copy
import uuid
from scripts.finitestatemachine import FiniteStateMachine
from entity.player_entities.playerstates_nostance import *
from scripts.engine_core_funcs import *
from scripts.actor import Actor
from entity.decals.decal import ActorDecals
from entity.player_entities.hook import Hook


class Player(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # objects and helpers
        self.parry = None
        self.attack = None
        self.block = None
        self.dash_dir = 0

        # inputs
        self.h_dir = 0
        self.h_dir_single = 0
        self.v_dir = 0
        self.v_dir_single = 0
        self.input_jump = 0
        self.input_jump_hold = 0
        self.input_attack = 0
        self.input_projectile = 0
        self.input_parry = 0
        self.input_dash = 0
        self.input_wallrun = 0
        self.map = None

        # physics
        self.apply_gravity = True
        self.collision_types = None
        self.max_y_velocity = 4
        self.max_x_velocity = 0
        self.decceleration = .30
        self.impulse = [0, 0]
        self.friction = .25
        self.air_friction = -.12
        self.run_speed = 0.75
        self.wallrun_speed = 1.5
        self.jump_force = -1.65
        self.dash_speed = pygame.Vector2(4, 0)
        self.grav_mult = 0
        self.grav_threshold = 0.5
        self.gravity = .04
        self.fractals = pygame.Vector2(0, 0)
        self.velocity_cache = pygame.Vector2(0, 0)

        # gameplay relative
        self.health = 100
        self.coyote_time = 152
        self.coyote_counter = 0
        self.counter = 0
        self.on_wall_right = False
        self.on_wall_left = False
        self.on_wall = False
        self.walljump_dir = 0
        self.can_grapple = True
        self.air_jump = False
        self.attack_timer = 15
        self.attack_cooldown = 10
        self.attack_duration = 0
        self.can_attack = False
        self.is_hooked = False
        self.wall_pos = [0, 0]
        self.input_angle = 0
        self.sword_charges = 0
        self.tell_me = 0
        self.can_wallrun = False
        self.can_slide = False
        self.can_dash = False
        self.stamina = 100
        self.stamina_cost = 1
        self.dash_buffer = 30
        self.dash_buffer_counter = 0
        self.dash_input_counter = 0
        self.movement_suspended = False
        self.pull_obj = None
        self.lock_face = False
        self.can_hook = True

        # Statemachine and States
        self.state_machine = FiniteStateMachine(debug=True)

        self.idle_state = FiniteIdleState(self, self.state_machine)
        self.run_state = FiniteRunState(self, self.state_machine)
        self.jump_state = FiniteJumpState(self, self.state_machine)
        self.airborne_state = FiniteAirborneState(self, self.state_machine)
        self.wallslide_state = FiniteWallslideState(self, self.state_machine)
        self.ropejump_state = FiniteRopeJump(self, self.state_machine)
        self.wallrun_state = FiniteWallRunState(self, self.state_machine)
        self.pull_state = FinitePullState(self, self.state_machine)
        # TODO: add stateobjects below

        self.state_machine.init_statemachine(self.idle_state)

    def update(self, dt) -> bool:
        r = super().update(dt)
        if not r:
            return r

        self.parse_input()

        if self.h_dir == 1 and not self.movement_suspended:
            self.flip[0] = 0
            self.face[0] = 1
        elif self.h_dir == -1 and not self.movement_suspended:
            self.flip[0] = 1
            self.face[0] = -1

        self.state_machine.current_state.logic_update(dt)
        self.state_machine.current_state.physics_update(dt)

        self.collision_types = self.move(dt)

        if self.input_attack and self.attack_duration >= self.attack_cooldown:
            self.hb_manager.create_hitbox(self, self.position, pygame.Vector2(8, 8), duration=5)
            self.attack_duration = 0
            attack_decal = ActorDecals(creator=self, width=25, height=12, game=self.game, position=self.position, sprite_name='samurai_attack', sprite_animation='default_animation')
            attack_decal.render_priority = 1
            attack_decal.set_direction(self.face, self.flip)
            self.em.add_entity(attack_decal)

        if self.input_parry and self.can_hook:
            self.can_hook = False
            hook = Hook(creator=self, width=4, height=4,
                        id=uuid.uuid4().int, rotation=0,
                        velocity=pygame.Vector2(self.face[0], 0),
                        game=self.game, position=self.position)
            self.em.add_entity(hook)
            self.suspend_movement()

        if self.attack_duration < self.attack_cooldown:
            self.attack_duration += 0.5*dt

        if not self.on_ground:
            self.coyote_counter += dt

        if self.collision_types['top']:
            self.velocity[1] = 0

        if self.collision_types['left'] or self.collision_types['right']:
            self.reset_fractions()
            self.on_wall = True
        else:
            self.on_wall = False

        if self.on_ground:
            self.coyote_counter = 0
            self.stamina = 100

        self.check_water_collisions()
        self.check_rope_collisions()
        # entity is alive
        return True

    def horizontal_movement(self, dt, direction) -> None:
        # calculating the velocity
        if direction == 1:
            self.velocity[0] += 0.9 * dt
        elif direction == -1:
            self.velocity[0] -= 0.9 * dt
        elif direction == 0 or self.velocity[0] > 0:
            self.velocity[0] = approach(self.velocity[0], 0, self.decceleration * dt)
        self.velocity[0] = clamp(self.velocity[0], -self.run_speed, self.run_speed)

    def vertical_movement(self, dt, ignore_mult=False) -> None:
        if not self.on_ground and ignore_mult:
            self.velocity[1] += self.gravity * 3 * dt
            if self.velocity[1] > self.max_y_velocity:
                self.velocity[1] = self.max_y_velocity
        else:
            if self.input_jump_hold and self.velocity[1] <= 2.5:
                self.grav_mult = 2
            elif not self.input_jump_hold or self.velocity[1] > 2.5:
                self.grav_mult = 4
            self.velocity[1] = approach(self.velocity[1], self.max_y_velocity, self.gravity * self.grav_mult * dt)
            if self.velocity[1] > self.max_y_velocity:
                self.velocity[1] = self.max_y_velocity

    def set_pos(self, position):
        self.position = position

    def suspend_movement(self):
        self.velocity_cache = self.velocity
        self.velocity = pygame.Vector2(0, 0)
        self.movement_suspended = True

    def continue_movement(self):
        self.velocity = self.velocity_cache
        self.movement_suspended = False
        self.can_hook = True

    def pull_player(self, pull_obj):
        self.pull_obj = pull_obj
        self.state_machine.change_state(self.pull_state)

    def render(self, surf: pygame.Surface, offset=(0, 0)) -> None:
        """
        most of the stuff here is just for debugging purposes
        :param surf:
        :param offset:
        :return:
        """
        super().render(surf, offset)
        # stamina_bar = pygame.Rect(10, 10, self.stamina, 3)
        # pygame.draw.rect(surf, (0, 255, 125), stamina_bar)
        # cam = pygame.Vector2(self.game.world.camera.pos)  # cameras position
        rect = pygame.Rect(self.rect.x - self.game.world.render_scroll[0], self.rect.y - self.game.world.render_scroll[1], self.size[0], self.size[1])
        # wallrect = pygame.Rect(self.wall_pos[0] - cam.x, self.wall_pos[1] - cam.y, 3, 3)
        # pygame.draw.rect(surf, (0, 255, 0), wallrect)
        # collision hitbox
        # pygame.draw.rect(surf, (255, 0, 0), rect, 1)
        # grounded check
        # pygame.draw.rect(surf, (0, 255, 0), rect.move(0, 1), 1)
        # self.state_machine.current_state.render_state(cam, surf)

    def parse_input(self):
        if self.game.input.input_method == 'gamepad':
            self.h_dir = self.game.input.dpad[0]
            self.v_dir = self.game.input.dpad[1] * -1

            self.h_dir_single = self.game.input.dpad_single[0]
            self.v_dir_single = self.game.input.dpad_single[1] * -1
        else:
            self.h_dir = self.game.input.states['move_right'] - self.game.input.states['move_left']
            self.v_dir = self.game.input.states['move_down'] - self.game.input.states['move_up']

        self.input_jump = self.game.input.states['jump']
        self.input_jump_hold = self.game.input.states['jump_hold']
        self.input_attack = self.game.input.states['attack']
        self.input_projectile = self.game.input.states['projectile']
        self.input_parry = self.game.input.states['parry']
        self.input_dash = self.game.input.states['dash']
        self.input_wallrun = self.game.input.states['wallrun']

        # get sword direction in shitty radians
        self.input_angle = math.atan2(self.v_dir, self.h_dir)
        # translate this shit to degrees
        self.input_angle = 180 * self.input_angle / math.pi
        # translate from 180 -180 degrees to 0 - 360 taking pygames degrees into account
        self.input_angle = (360 + round(self.input_angle)) % 360

        if self.input_angle == 0:
            if self.face[0] == -1:
                self.input_angle = 180
            elif self.face[1] == 1:
                self.input_angle = 0
