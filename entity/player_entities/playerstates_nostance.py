import pygame
from scripts.engine_core_funcs import *

from scripts.finitestate import FiniteState


class FiniteIdleState(FiniteState):
    """
    A state defining the Players behaviour idle behaviour
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'Idle'

    def enter_state(self) -> None:
        super().enter_state()
        self.entity_obj.set_animation('idle', True, "new_samurai")
        self.entity_obj.reset_fractions()
        self.entity_obj.velocity -= self.entity_obj.velocity

    def exit_state(self) -> None:
        super().exit_state()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)

        if self.entity_obj.h_dir != 0:
            self.state_machine.change_state(self.entity_obj.run_state)
            return

        elif self.entity_obj.input_jump:
            self.state_machine.change_state(self.entity_obj.jump_state)
            return

        elif not self.entity_obj.on_ground:
            self.state_machine.change_state(self.entity_obj.airborne_state)
            return

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        if not self.entity_obj.movement_suspended:
            self.entity_obj.horizontal_movement(self.entity_obj.game.window.dt, 0)


class FiniteRunState(FiniteState):
    """
    A state defining the Players run behaviour
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'Run'

    def enter_state(self) -> None:
        super().enter_state()
        self.entity_obj.set_animation('run', True, "new_samurai")
        self.entity_obj.reset_fractions()
        self.entity_obj.velocity -= self.entity_obj.velocity

    def exit_state(self) -> None:
        super().exit_state()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if self.entity_obj.h_dir == 0:
            self.state_machine.change_state(self.entity_obj.idle_state)
            return

        elif self.entity_obj.input_jump:
            self.state_machine.change_state(self.entity_obj.jump_state)
            return

        elif not self.entity_obj.on_ground:
            self.state_machine.change_state(self.entity_obj.airborne_state)
            return
        elif self.entity_obj.input_parry:
            pass
            # self.state_machine.change_state(self.entity_obj.parry_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        if not self.entity_obj.movement_suspended:
            self.entity_obj.horizontal_movement(self.entity_obj.game.window.dt, self.entity_obj.h_dir)


class FiniteJumpState(FiniteState):
    """
    A state defining the Players jump behaviour
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'Jump'

    def enter_state(self) -> None:
        super().enter_state()
        self.entity_obj.velocity[1] = self.entity_obj.jump_force

    def exit_state(self) -> None:
        super().exit_state()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        self.state_machine.change_state(self.entity_obj.airborne_state)
        self.entity_obj.position.y -= 1
        self.entity_obj.coyote_counter = 10000

    def physics_update(self, dt) -> None:
        super().physics_update(dt)


class FiniteAirborneState(FiniteState):
    """
    A state defining the Players airborne behaviour
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'Airborne'
        self.fastfall_applied = False
        self.changed_animation = False

    def enter_state(self) -> None:
        super().enter_state()
        if self.entity_obj.velocity.y > 0:
            self.entity_obj.set_animation('falling', True, "new_samurai")
            self.changed_animation = True
        else:
            self.entity_obj.set_animation('jump', True, "new_samurai")

    def exit_state(self) -> None:
        super().exit_state()
        self.fastfall_applied = False
        self.changed_animation = False

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if self.entity_obj.velocity.y > 0 and not self.changed_animation:
            self.entity_obj.set_animation('falling', True, "new_samurai")
            self.changed_animation = True

        self.entity_obj.coyote_counter += dt
        if self.entity_obj.on_ground and self.entity_obj.velocity[0] == 0:
            self.state_machine.change_state(self.entity_obj.idle_state)
            return

        elif self.entity_obj.on_ground and self.entity_obj.velocity[0] != 0:
            self.state_machine.change_state(self.entity_obj.run_state)
            return

        elif self.entity_obj.input_jump and self.entity_obj.coyote_counter < self.entity_obj.coyote_time:
            self.state_machine.change_state(self.entity_obj.jump_state)
            return

        # if self.entity_obj.on_wall:
        #  self.state_machine.change_state(self.entity_obj.wallslide_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        if not self.entity_obj.input_jump_hold and self.entity_obj.velocity[1] < 0 and not self.fastfall_applied:
            # self.entity_obj.velocity[1] = 0.50
            self.fastfall_applied = True
        if not self.entity_obj.movement_suspended:
            self.entity_obj.horizontal_movement(self.entity_obj.game.window.dt, self.entity_obj.h_dir)
            self.entity_obj.vertical_movement(dt, ignore_mult=self.state_machine.get_prev_state() != 'Jump')


class FinitePullState(FiniteState):

    def enter_state(self) -> None:
        super().enter_state()
        self.entity_obj.suspend_movement()
        self.entity_obj.velocity = pygame.Vector2(3 * self.entity_obj.face[0], 0)
        self.entity_obj.velocity_cache = pygame.Vector2(0, 0)
        self.name = 'Pull State'

    def exit_state(self) -> None:
        super().exit_state()
        self.entity_obj.continue_movement()
        self.entity_obj.pull_obj.alive = False

    def logic_update(self, dt) -> None:
        super().logic_update(dt)

        if self.entity_obj.input_jump:
            self.state_machine.change_state(self.entity_obj.ropejump_state)

        if self.entity_obj.on_wall:
            if self.entity_obj.on_ground:
                self.state_machine.change_state(self.entity_obj.idle_state)
            else:
                self.state_machine.change_state(self.entity_obj.airborne_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        # self.entity_obj.horizontal_movement(self.entity_obj.game.window.dt, self.entity_obj.face[0])

    def render_state(self, cam, surf) -> None:
        super().render_state(cam, surf)


class FiniteWallslideState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.wallslide_speed_mult = 1
        self.name = 'Wallslide'
        self.is_locked = True

    def enter_state(self) -> None:
        super().enter_state()
        self.entity_obj.velocity[1] = 0
        self.entity_obj.walljump_dir = self.entity_obj.h_dir
        self.entity_obj.set_animation('wallslide_loop', True, "aikkia")

    def exit_state(self) -> None:
        super().exit_state()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if self.entity_obj.input_jump:
            self.state_machine.change_state(self.entity_obj.walljump_state)
            return
        if self.entity_obj.on_ground:
            self.state_machine.change_state(self.entity_obj.idle_state)
            return
        if not self.entity_obj.on_wall and not self.entity_obj.on_ground:
            self.state_machine.change_state(self.entity_obj.airborne_state)
            return

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        # needs to be here for constant wallchecks in a range of 3 pixels
        self.entity_obj.velocity[0] = self.entity_obj.face[0] * 3

        y_vel = self.entity_obj.velocity[1]
        increment = (((y_vel + 4) ** (1 / 4) - 1.4) / 2) * dt
        self.entity_obj.velocity[1] = lerp(self.entity_obj.velocity[1], 3, increment)

    def print_state(self) -> None:
        super().print_state()


class FiniteRopeJump(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.timer = 0
        self.name = 'Ropejump'
        self.is_locked = True

    def enter_state(self) -> None:
        super().enter_state()
        self.entity_obj.velocity = pygame.Vector2(1.5 * self.entity_obj.face[0], -2)
        self.entity_obj.set_animation('jump', True, "new_samurai")

    def exit_state(self) -> None:
        super().exit_state()
        self.timer = 0

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if self.entity_obj.velocity.y > 0:
            self.entity_obj.set_animation('falling', True, "new_samurai")
        if self.timer > 12:
            self.state_machine.change_state(self.entity_obj.airborne_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        self.entity_obj.vertical_movement(dt, ignore_mult=True)
        self.timer += dt


class FiniteWallRunState(FiniteState):
    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)

    def enter_state(self) -> None:
        super().enter_state()
        self.entity_obj.velocity[1] = 0

    def exit_state(self) -> None:
        super().exit_state()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if self.entity_obj.h_dir == 0 or not self.entity_obj.can_wallrun:
            self.state_machine.change_state(self.entity_obj.airborne_state)
        if self.entity_obj.input_jump:
            self.state_machine.change_state(self.entity_obj.jump_state)
        if self.entity_obj.stamina <= 0:
            self.state_machine.change_state(self.entity_obj.airborne_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        self.entity_obj.stamina -= self.entity_obj.stamina_cost * dt
        self.entity_obj.horizontal_movement(self.entity_obj.game.window.dt, self.entity_obj.h_dir)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, cam, surf) -> None:
        super().render_state(cam, surf)
