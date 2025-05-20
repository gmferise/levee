from inspect import isclass
from .exceptions import ChartSyntaxError, LeveeException, TransitionError, TransitionDoesNotExist, TransitionMissingArgs, TransitionNotAllowed
from .state import State

class ChartMeta(type):

    def __init__(self, chart_name, class_extends, class_attrs, **kwargs):
        # Extract the possible States from the Chart class body, with validation
        state_classes = []
        for key, value in class_attrs.items():
            if isclass(value) and issubclass(value, State):        
                if not value.value.isupper():
                    raise ChartSyntaxError(f'State {value} should be all uppercase')
                if key != value.__name__:
                    raise ChartSyntaxError(f'{chart_name}: State {key} differs from its class name, you must use `{value.__name__} = {value.__name__}`')
                state_classes.append(value)
        
        # States ref and pretty version for choice generation
        self.states = tuple(state_classes)
        self.state_values = tuple(state_class.value for state_class in state_classes)

        # Extract the possible transitions from the Chart class body, with validation
        self.transitions = {}
        chart = class_attrs.get('chart', {})
        if type(chart) is not dict:
            raise ChartSyntaxError(f'{chart_name}: chart must be a dict, not a {type(chart)}')
        if any(from_state is Ellipsis for from_state in chart):
            raise ChartSyntaxError(f'{chart_name}: Ellipsis `...` does nothing at the root level')
        if any(from_state.condition for from_state in chart if not isclass(from_state)):
            raise ChartSyntaxError(f'{chart_name}: Conditions `()` do nothing at the root level')
        if any(from_state.effect for from_state in chart if not isclass(from_state)):
            raise ChartSyntaxError(f'{chart_name}: Effects `[]` do nothing at the root level')
        
        # Process chart structure deeply into transitions, with validation
        all_to_states = set()
        deep_chart = [(k, v) for k, v in chart.items()]
        while len(deep_chart) > 0:
            from_state, to_states = deep_chart.pop(0)
            if not isinstance(from_state, State) and not issubclass(from_state, State):
                raise ChartSyntaxError(f'{chart_name}: All from states must be a State class or object')
            if from_state.state not in self.states:
                raise ChartSyntaxError(f'{chart_name}: State {from_state.value} is not defined in Chart class body')
            if type(to_states) is dict:
                if any(from_state.state == transition_state.state for transition_state in self.transitions):
                    raise ChartSyntaxError(f'{chart_name}: Duplicate transitions entry `{"{}"}` for State {from_state.state}. Combine your transition entries into a single one at the root level and reference it with Ellipsis')
                all_to_states |= set(to_state.value for to_state in to_states)
                # Realize class States into object States when they are conditionless
                self.transitions[from_state] = {
                    to_state.value: to_state(conditionless=True) if isclass(to_state) else to_state
                    for to_state in to_states
                }
                deep_chart.extend((k, v) for k, v in to_states.items())
            elif to_states is not Ellipsis:
                raise ChartSyntaxError(f'{chart_name}: All to states must be Ellipsis `...` or a transition entry `{"{}"}`')
        
        # Verify every to_state was once declared as a from_state    
        for state_name in all_to_states:
            transition_names = [transition.value for transition in self.transitions.keys()]
            if state_name not in transition_names:
                raise ChartSyntaxError(f'{chart_name}: Missing transition entry `{"{}"}` for State {state_name}')

        return super().__init__(chart_name, class_extends, class_attrs, **kwargs)

class Chart(metaclass=ChartMeta):
    """
    Extend this class and define possible `States` inside.
    Then, use those `States` in the `chart` to declare how they can be
    transitioned between.

    The first state placed in the chart is your initial state. Any object
    with None for its state value will be initialized to it.

    To your transitions, you can add `Conditions` with parenthesis and
    `Effects` with square brackets.

    The transitions away from a state can only be defined in one place
    for readability, so in other transitions that change to that state,
    use Ellipses `...` to reference it.

    ```python
    class Example(Chart):
        class ALPHA(State): pass
        class BETA(State): pass

        chart = {
            ALPHA: {
                BETA (IfConditionIsTrue) [ThenTriggerThisEffect]: ...
            },
            BETA: {},
        }
    ```
    """
    chart = {}

    def __init__(self, stateful_object, state_attribute='state'):
        """
        Create a new Chart to transform the external state of an object or dict.
        The external state will be initialized to the first State in the Chart if it has not been set.
        """
        def obj_getter():
            return getattr(stateful_object, state_attribute)
        def obj_setter(value):
            setattr(stateful_object, state_attribute, value)
        
        def dict_getter():
            return stateful_object[state_attribute]
        def dict_setter(value):
            stateful_object[state_attribute] = value
        
        self.getter = dict_getter if type(stateful_object) is dict else obj_getter
        self.setter = dict_setter if type(stateful_object) is dict else obj_setter
        if self.state is None and len(self.transitions.keys()) > 0:
            self.state = list(self.transitions.keys())[0]
        
        self.obj = stateful_object

    @property
    def state(self):
        """
        Get the current state in hydrated form, with validation to ensure it is a possible state
        """
        value = self.getter()
        if value is None:
            return value
        try:
            return self.states[self.state_values.index(value)]
        except ValueError:
            raise LeveeException(f'{self.obj}: Refusing to get unknown state "{value}"')
        
    @state.setter
    def state(self, value):
        """
        Set the current state to the dehydrated form
        """
        self.setter(value.value)
    
    def transition(self, state, dry_run, **kwargs):
        try:
            new_state = self.states[self.state_values.index(str(state))]
        except ValueError:
            raise TransitionError(f'Unknown state "{state}"')
        
        try:
            transition = self.transitions[self.state][new_state.value]
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
                raise TransitionMissingArgs(param)
        
        if condition:
            condition_result = condition.eval(**{
                key: value
                for key, value in kwargs.items()
                if key in condition.params
            })
            if condition_result != True: # Strings used in error message
                raise TransitionNotAllowed(condition_result)
        
        if not dry_run:
            self.state = new_state
            if effect:
                effect.exec(**{
                    key: value
                    for key, value in kwargs.items()
                    if key in effect.params
                })
            
        return new_state
    
    def to(self, state, **kwargs):
        return self.transition(state, False, **kwargs)

    def can(self, state, **kwargs):
        try:
            self.transition(state, True, **kwargs)
        except TransitionNotAllowed:
            return False
        return True
    
    def choices(self, **kwargs):
        return tuple(
            (state_class.value, state_class.pretty_value)
            for state_class in self.transitions[self.state].values()
            if self.can(state_class.value, **kwargs)
        )