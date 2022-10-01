from enum import Enum

class Operator(Enum):
    NONE = ''
    NOT = 'not'
    OR = 'or'
    AND = 'and'

UNARY_OPERATORS = [
    Operator.NONE,
    Operator.NOT,
]

BINARY_OPERATORS = [
    Operator.OR,
    Operator.AND,
]

class ConditionalOps():

    def __or__(self, other):
        return ConditionalExpression(self, other, operator=Operator.OR)
    
    def __and__(self, other):
        return ConditionalExpression(self, other, operator=Operator.AND)
    
    def __invert__(self):
        return ConditionalExpression(self, operator=Operator.NOT)

class ConditionalMeta(ConditionalOps, type):
    
    def __str__(self):
        return self.__name__

class Conditional(ConditionalOps, metaclass=ConditionalMeta):

    def eval(self, **kwargs):
        pass

class ConditionalExpression(Conditional):

    def __init__(self, *values, operator=Operator.NONE):
        if not isinstance(operator, Operator):
            raise TypeError(type(operator))
        if not all(
            isinstance(value, ConditionalExpression)
            or issubclass(value, Condition)
            for value in values
        ):
            raise TypeError([type(value) for value in values])
        if (
            len(values) == 0 and operator is not Operator.NONE
            or len(values) != 1 and operator in UNARY_OPERATORS
            or len(values) != 2 and operator in BINARY_OPERATORS
        ):
            raise ValueError(values)
        self.operator = operator
        self.values = tuple(values)
    
    def eval(self, **kwargs):
        if self.operator is Operator.NONE:
            if len(self.values):
                return self.values[0].eval(**kwargs)
        elif self.operator is Operator.NOT:
            return not self.values[0].eval(**kwargs)
        elif self.operator is Operator.OR:
            return self.values[0].eval(**kwargs) or self.values[1].eval(**kwargs)
        elif self.operator is Operator.AND:
            return self.values[0].eval(**kwargs) and self.values[1].eval(**kwargs)
    
    def __str__(self):
        if self.operator is Operator.NONE:
            if len(self.values):
                return str(self.values[0])
            return ''
        elif self.operator is Operator.NOT:
            return f'~{self.values[0]}'
        elif self.operator is Operator.OR:
            return f'({self.values[0]} | {self.values[1]})'
        elif self.operator is Operator.AND:
            return f'({self.values[0]} & {self.values[1]})'

class Condition(Conditional):
    """
    Extend this class and redefine its eval() method to create a condition
    You can add non-fallback arguments to your eval() method and they will be
    required as inputs for Chart.to(). They will be passed by name.

    Conditions can be combined like boolean expressions via the following operators:
    - `not` --> `~`
    - `and` --> `&`
    - `or` --> `|`
    """
    
    def eval(self, **kwargs):
        """
        Return a value that is not True to block the transition
        """
        return True