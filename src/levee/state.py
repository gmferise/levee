from inspect import isclass
from .exceptions import ChartSyntaxError
from .condition import ConditionalExpression
from .effect import EffectExpression

class StateMeta(type):

    def __init__(self, name, extends, attrs, **kwargs):
        return super().__init__(name, extends, attrs, **kwargs)

    def __getitem__(self, effect):
        return self(conditionless=True)[effect]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.__name__
    
    def __hash__(self):
        return self.value.__hash__()
    
    @property
    def state(self):
        return self

    @property
    def value(self):
        return self.__name__
    
    @property
    def pretty_value(self):
        return self.__name__.replace('_', ' ').title()

class State(metaclass=StateMeta):
    """
    Extend this class and optionally define `Conditions` or `Effects` that
    will always be used for transitions involving this state via `to_enter`,
    `to_exit`, `on_enter`, and `on_exit`.
    """
    to_enter = None
    to_exit = None
    on_enter = None
    on_exit = None

    def __init__(self, condition=None, **kwargs):
        if condition is None and not kwargs.get('conditionless', False):
            raise ChartSyntaxError('Empty Condition `()` not allowed')
        self.condition = ConditionalExpression() if condition is None \
            else ConditionalExpression(condition)
        self.effect = EffectExpression()

    def __call__(self, *args, **kwargs):
        raise ChartSyntaxError('Conditions `()` cannot come after Effects `[]`')

    def __getitem__(self, effect):
        self.effect = EffectExpression(effect)
        return self

    def __repr__(self):
        return str(self)

    def __str__(self):
        condition = str(self.condition)
        if condition and not (condition.startswith('(') and condition.endswith(')')):
            condition = f'({condition})'
        effect = str(self.effect)
        if effect and not (effect.startswith('[') and effect.endswith(']')):
            effect = f'[{effect}]'
        return ' '.join(string for string in (
            str(self.__class__),
            condition,
            effect,
        ) if string)
    
    def __hash__(self):
        return self.value.__hash__()

    @property
    def state(self):
        return self.__class__

    @property
    def value(self):
        return self.state.value
    
    @property
    def pretty_value(self):
        return self.state.pretty_value