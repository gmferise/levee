from .exceptions import ChartSyntaxError
from .condition import ConditionalExpression
from .effect import EffectChain

class StateMeta(type):

    def __init__(self, name, extends, attrs, **kwargs):
        if len(extends) > 0 and not name.isupper():
            raise ChartSyntaxError(f'State {name} should be all uppercase')
        return super().__init__(name, extends, attrs, **kwargs)

    def __getitem__(self, effect):
        return self(effect_only=True)[effect]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.__name__
    
    @property
    def state(self):
        return self

    @property
    def value(self):
        return self.__name__

class State(metaclass=StateMeta):
    to_enter = None
    to_exit = None
    on_enter = None
    on_exit = None
    """
    Extend this class and optionally define ``Conditions`` or ``Effects`` that
    will always be used for transitions involving this state via ``to_enter``,
    ``to_exit``, ``on_enter``, and ``on_exit``.
    """

    def __init__(self, condition=None, **kwargs):
        if condition is None and not kwargs.get('allow_empty', False):
            raise ChartSyntaxError('Empty Condition ``()`` not allowed')
        self.condition = ConditionalExpression() if condition is None \
            else ConditionalExpression(condition)
        self.effect = EffectChain()

    def __call__(self, *args, **kwargs):
        raise ChartSyntaxError('Conditions ``()`` cannot come after Effects ``[]``')

    def __getitem__(self, effect):
        self.effect = EffectChain(effect)
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
    
    @property
    def state(self):
        return self.__class__

    @property
    def value(self):
        return self.__class__.__name__