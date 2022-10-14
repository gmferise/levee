from inspect import signature, Parameter
from levee.exceptions import LeveeException
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

    def __init__(self, name, extends, attrs, **kwargs):
        allowed_kinds = [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]
        if self._allow_kwargs:
            allowed_kinds.append(Parameter.VAR_KEYWORD)
        if any(
            param.kind not in allowed_kinds
            for param in signature(self.eval).parameters.values()
        ):
            raise LeveeException(f'{name}: Parameters for ``eval`` must be passable by keyword and non-variable')
        return super().__init__(name, extends, attrs, **kwargs)

    def __str__(self):
        return self.__name__

class Conditional(ConditionalOps, metaclass=ConditionalMeta):

    _allow_kwargs = False

    def eval(self):
        pass

    @property
    def params(self):
        return set()
    
    @property
    def required_params(self):
        return set()

class ConditionalExpression(Conditional):

    _allow_kwargs = True

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
            or len(values) > 1 and operator in UNARY_OPERATORS
            or len(values) < 2 and operator in BINARY_OPERATORS
        ):
            raise ValueError(operator, values)
        self.operator = operator
        self.values = tuple(value() for value in values)

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
    
    @property
    def params(self):
        params = set()
        for value in self.values:
            params |= value.params
        return params
    
    @property
    def required_params(self):
        required_params = set()
        for value in self.values:
            required_params |= value.required_params
        return required_params

    def __bool__(self):
        return len(self.values) > 0

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
    Extend this class and define a pass condition in its ``eval`` function.
    When calling ``Chart.to()``, any kwargs passed will be provided to ``eval``
    by name.

    ``Conditions`` can be combined like booleans with these operators:
    - `not` --> `~`
    - `and` --> `&`
    - `or` --> `|`

    ``Conditions`` can be added to a transition with this chart syntax:
    ```
    FROM_STATE: {
        TO_STATE (Condition1 & Condition2 | ~Condition3): ...
    }
    ```
    """

    def eval(self):
        """
        Return a value that is not True to block the transition
        """
        return True
    
    @property
    def params(self):
        return set(
            param.name
            for param in signature(self.eval).parameters.values()
            if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
        )
    
    @property
    def required_params(self):
        return set(
            param.name
            for param in signature(self.eval).parameters.values()
            if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
            if param.default is Parameter.empty
        )
