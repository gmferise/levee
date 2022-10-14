from inspect import isclass
from .exceptions import ChartSyntaxError, LeveeException, TransitionDoesNotExist, TransitionMissingData, TransitionNotAllowed
from .state import State

class ChartMeta(type):

    def __init__(self, name, extends, attrs, **kwargs):
        state_classes = []
        for key, value in attrs.items():
            if isclass(value) and issubclass(value, State):
                if key != value.__name__:
                    raise ChartSyntaxError(f'{name}: State {key} differs from its class name')
                state_classes.append(value)
        self.states = tuple(state_classes)
        self.choices = tuple((cls.value, cls.value.replace('_', ' ').title()) for cls in state_classes)

        def get_state_const(transition):
            if not isinstance(transition, State) and not issubclass(transition, State):
                raise ChartSyntaxError(f'{name}: All transition keys must be States')
            try:
                return self.states[self.states.index(transition.state)]
            except ValueError:
                raise ChartSyntaxError(f'{name}: State for transition {transition} is not defined in class body')

        self.transitions = {}
        chart = attrs.get('chart', {})
        if any(value is Ellipsis for value in chart.values()):
            raise ChartSyntaxError(f'{name}: Ellipsis ``...`` not allowed at root level')
        for key in chart:
            get_state_const(key)
        if any(key.condition for key in chart if not isclass(key)):
            raise ChartSyntaxError(f'{name}: Conditions ``()`` not allowed at root level')
        if any(key.effect for key in chart if not isclass(key)):
            raise ChartSyntaxError(f'{name}: Effects ``[]`` not allowed at root level')
        flattened = [(k, v) for k, v in chart.items()]
        while len(flattened) > 0:
            key, value = flattened.pop(0)
            from_state = get_state_const(key)
            if type(value) is dict:
                state_mapping = self.transitions.get(from_state, {})
                for to_state in value.keys():
                    cls = get_state_const(to_state)
                    state_mapping[cls] = to_state(allow_empty=True) if isclass(to_state) else to_state
                self.transitions[from_state] = state_mapping
                flattened.extend((k, v) for k, v in value.items())
            elif value is not Ellipsis:
                raise ChartSyntaxError(f'{name}: All transition values must be ``...`` or ``{{}}``')

        possible_to_states = set()
        for to_states in self.transitions.values():
            possible_to_states |= set(get_state_const(state) for state in to_states)
        for to_state in possible_to_states:
            if to_state not in self.transitions:
                raise ChartSyntaxError(f'{name}: Missing ``{{}}`` entry for State {to_state}')

        return super().__init__(name, extends, attrs, **kwargs)

class Chart(metaclass=ChartMeta):
    """
    Extend this class and define possible ``States`` inside.
    Then, use those ``States`` in the ``chart`` to declare how they can be
    transitioned between.

    The first state placed in the chart is your initial state. Any object
    with None for its state value will be initialized to it.

    To your transitions, you can add ``Conditions`` with parenthesis and
    ``Effects`` with square brackets.

    The transitions away from a state can only be defined in one place
    for readability, so in other transitions that change to that state,
    use Ellipses ``...`` to reference it.

    ```
    class FROM_STATE(State): pass
    class TO_STATE(State): pass

    FROM_STATE: {
        TO_STATE (IfConditionIsTrue) [ThenTriggerThisEffect]: ...
    },
    TO_STATE: {},
    ```
    """
    chart = {}

    def __init__(self, stateful_object, state_attribute, is_key=False):
        self.obj = stateful_object
        self.attribute = state_attribute
        self.is_key = is_key
        if self.state is None and len(self.transitions.keys()) > 0:
            self.state = list(self.transitions.keys())[0]

    @property
    def state(self):
        value = self.obj[self.attribute] if self.is_key \
            else getattr(self.obj, self.attribute)
        if value is None:
            return None
        try:
            return [cls for cls in self.states if cls.value == value][0]
        except IndexError:
            raise LeveeException(f'{self.obj}: Read unknown state "{value}"')

    @state.setter
    def state(self, value):
        if value not in self.states and value not in (cls.value for cls in self.states):
            raise LeveeException(f'{self.obj}: Refusing to set unknown state "{value}"')
        value = value.value if value in self.states else value
        if self.is_key:
            self.obj[self.attribute] = value
        else:
            setattr(self.obj, self.attribute, value)

    def to(self, state, **kwargs):
        # Potential: State expression?
        # Like (A > B) | (B > C) OOPs is | then >
        # Or A >> B | B >> C OOPs is >> then |
        # TODO: Transition logic and error handling
        try:
            new_state = [cls for cls in self.states if cls.value == state][0] \
                if state not in self.states else state
        except IndexError:
            raise LeveeException(f'Unknown state "{state}"')
        
        try:
            transition = self.transitions[self.state][new_state]
        except KeyError:
            raise TransitionDoesNotExist(f'{self.state} to {new_state}')
        
        required_params = set()
        condition = transition.condition
        if condition:
            required_params |= condition.required_params
        effect = transition.effect
        if effect:
            required_params |= effect.required_params
        for param in required_params:
            if param not in kwargs:
                raise TransitionMissingData(param)
        
        if condition:
            condition_result = condition.eval(**{
                key: value
                for key, value in kwargs.items()
                if key in condition.params
            })
            if condition_result != True:
                raise TransitionNotAllowed(condition_result)
        
        self.state = new_state

        if effect:
            effect.exec(**{
                key: value
                for key, value in kwargs.items()
                if key in effect.params
            })
        
        return new_state