class FiniteStateMachine:
    """
    An object which handles the handling of StateClasses. This can be used inside of
    any class that needs a StateMachine
    """

    def __init__(self, debug=False):
        self.current_state = None
        self.debug = debug
        self.previous_state = None

    def change_state(self, new_state, trans_data=None) -> None:
        """
        Changes states of the statemachine
        :param new_state: The state the statemachine should change to
        :return: Nothing
        """
        self.previous_state = self.current_state
        self.current_state.exit_state()
        self.current_state = new_state
        self.current_state.enter_state()
        if self.debug:
            self.current_state.print_state()

    def change_previous(self) -> None:
        """
        Changes the state to the previously saved state
        :return: Nothing
        """
        self.current_state.exit_state()
        self.current_state = self.previous_state
        self.current_state.enter_state()
        if self.debug:
            self.current_state.print_state()

    def init_statemachine(self, starting_state=None) -> None:
        """
        Initializes the statemachine
        :param starting_state: The state which the statemachine should start in, can be None
        :return: Nothing
        """
        if starting_state is None:
            return
        self.current_state = starting_state
        self.current_state.enter_state()

    def get_state(self) -> str:
        """
        :return: the current_states name as string
        """
        return self.current_state.name

    def get_prev_state(self) -> str:
        """
        :return: the previous state as a string
        """
        return self.previous_state.name
