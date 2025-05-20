from enum import Enum
from .expressions import ExpressionMeta, Operator, Equation, Operand


class EffectMeta(ExpressionMeta):
    class Operators(Enum):
        PLUS = Operator('+', 2)
    
    def __add__(self, other):
        return EffectExpression(self, other, operator=self.Operators.PLUS)

class EffectExpression(Equation, metaclass=EffectMeta):
    calc = 'exec'

    def exec(self, **kwargs):
        if len(self.values) == 0:
            return
        exec_operand = lambda operand: operand.exec(**{
            k: v
            for k, v in kwargs.items()
            if k in operand.params
        })
        if self.operator is None:
            exec_operand(self.values[0])
            return
        if self.operator is self.Operators.PLUS:
            exec_operand(self.values[0])
            exec_operand(self.values[1])
            return

    def __str__(self):
        if len(self.values) == 0:
            return ''
        if self.operator is None:
            return str(self.values[0])
        if self.operator is self.Operators.PLUS:
            return f'{self.values[0]} {self.Operators.PLUS} {self.values[1]}'

class Effect(Operand, metaclass=EffectMeta):
    """
    Extend this class and define logic in its `exec` function.
    Named arguments can be added to the `exec` signature to require these
    arguments to be provided when calling `Chart.to()`.

    `Effects` can be added to a transition with this chart syntax:
    ```
    FROM_STATE: {
        TO_STATE [Effect1 + Effect2 + Effect3]: ...
    }
    ```
    """
    calc = 'exec'

    def exec(self):
        pass