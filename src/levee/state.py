from .condition import ConditionalExpression
from .effect import EffectChain

class StateMeta(type):
    
    def __getitem__(self, effect):
        return self()[effect]
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return self.__name__

class State(metaclass=StateMeta):
    to_enter = None
    to_exit = None
    on_enter = None
    on_exit = None
    
    def __init__(self, condition=None):
        self.condition = ConditionalExpression() if condition is None \
            else ConditionalExpression(condition)
        self.effect = EffectChain()
    
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