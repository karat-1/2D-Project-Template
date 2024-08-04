from scripts.entity import Entity


class FiniteState:
    """
    A State Object which can encapsulate behaviour and is part of a StateMachine
    """
    def __init__(self, entity_obj, state_machine):
        """
        :param entity_obj: an Entity type object
        :param state_machine: The FiniteStateMachine Object corresponding to the entity that was passed in
        """
        self.entity_obj = entity_obj
        self.state_machine = state_machine
        self.exiting_state = None
        self.start_time = 0
        self.animation_finished = False
        self.name = 'Default'
        self.action_possible = False
        self.transitional_data = None
        self.is_locked = False

    def enter_state(self) -> None:
        """
        This function gets called when the StateMachine enters the current state for the first time
        :return: Nothing
        """
        self.exiting_state = False

    def exit_state(self) -> None:
        """
        This function gets called when the StateMachine exits the current state
        :return: Nothing
        """
        self.exiting_state = True

    def logic_update(self, dt) -> None:
        """
        This function gets called every frame. For encapsulation purposes, this function only should contain
        logical updates and state transitions
        :return: Nothing
        """
        pass

    def physics_update(self, dt) -> None:
        """
        This function gets called every frame. For encapsulation purposes, this function only should contain
        physiucal updates
        :return: Nothing
        """
        pass

    def late_physics_update(self, dt) -> None:
        """
        This function can be called during an entities late update. E.g. after its position has been updated
        :return: Nothing
        """
        pass

    def late_logic_update(self, dt) -> None:
        """
        This function can be called during an entities late update. E.g. after its position has been updated
        :return: Nothing
        """
        pass

    def print_state(self) -> None:
        print(self.name)

    def render_state(self, cam, surf) -> None:
        pass
