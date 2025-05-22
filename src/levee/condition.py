from enum import Enum
from .expressions import ExpressionMeta, Operator, Equation, Operand


class ConditionMeta(ExpressionMeta):
    class Operators(Enum):
        NOT = Operator('~')
        OR = Operator('|', 2)
        AND = Operator('&', 2)

    def __or__(self, other):
        return ConditionalExpression(self, other, operator=self.Operators.OR)

    def __and__(self, other):
        return ConditionalExpression(self, other, operator=self.Operators.AND)

    def __invert__(self):
        return ConditionalExpression(self, operator=self.Operators.NOT)  

class ConditionalExpression(Equation, metaclass=ConditionMeta):
    calc = 'eval'

    def eval(self, **kwargs):
        if len(self.values) == 0:
            return
        eval_operand = lambda operand: operand.eval(**{
            k: v
            for k, v in kwargs.items()
            if k in operand.params
        })
        if self.operator is None:
            return eval_operand(self.values[0])
        if self.operator is self.Operators.NOT:
            return eval_operand(self.values[0]) != True
        if self.operator is self.Operators.OR:
            left_value = eval_operand(self.values[0])
            right_value = eval_operand(self.values[1])
            if left_value != True and right_value != True:
                return f'{left_value} and {right_value}'
            if left_value == True:
                return left_value
            return right_value
        if self.operator is self.Operators.AND:
            left_value = eval_operand(self.values[0])
            right_value = eval_operand(self.values[1])
            if left_value != True and right_value != True:
                return f'{left_value} and {right_value}'
            if left_value != True:
                return left_value
            return right_value
            

    def __str__(self):
        if len(self.values) == 0:
            return ''
        if self.operator is None:
            return str(self.values[0])
        if self.operator is self.Operators.NOT:
            return f'{self.Operators.NOT}{self.values[0]}'
        if self.operator is self.Operators.OR:
            return f'({self.values[0]} {self.Operators.OR} {self.values[1]})'
        if self.operator is self.Operators.AND:
            return f'({self.values[0]} {self.Operators.AND} {self.values[1]})'

class Condition(Operand, metaclass=ConditionMeta):
    """
    Extend this class and define a pass condition in its `eval` function.
    When calling `Chart.to()`, any kwargs passed will be provided to `eval`
    by name.

    `Conditions` can be combined like booleans with these operators:
    - `not` --> `~`
    - `and` --> `&`
    - `or` --> `|`

    `Conditions` can be added to a transition with this chart syntax:
    ```
    FROM_STATE: {
        TO_STATE (Condition1 & Condition2 | ~Condition3): ...
    }
    ```
    """
    calc = 'eval'

    def eval(self):
        """
        Return a value that is not True to block the transition
        """
        return True
