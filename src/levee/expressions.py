from inspect import Parameter, signature
from enum import Enum
from .exceptions import LeveeException

class Operator:

    def __init__(self, symbol, operands=1):
        self.symbol = symbol
        self.operands = operands

class ExpressionBase:
    calc = None
    _calc_kwargs = False

    def __init__(self, *args, **kwargs):
        self.Operators = self.__class__.Operators
    
    def __call__(self):
        return self

    @property
    def params(self):
        return set()
    
    @property
    def required_params(self):
        return set()

class ExpressionMeta(type):
    class Operators(Enum): pass

    def __init__(self, name, extends, attrs, **kwargs):
        """Create an Expression class, checking its calc() args"""
        allowed_kinds = [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]
        if self._calc_kwargs:
            allowed_kinds.append(Parameter.VAR_KEYWORD)
        
        if self.calc is not None:
            calc_fn = getattr(self, self.calc, None)
            if calc_fn is not None and any(
                param.kind not in allowed_kinds
                for param in signature(calc_fn).parameters.values()
            ):
                raise LeveeException(f'{name}: Parameters for `{self.calc}` must be must be passable by keyword and non-variable')

        return super().__init__(name, extends, attrs, **kwargs)
    
    def __str__(self):
        return self.__name__

class Equation(ExpressionBase):

    _calc_kwargs = True

    def __init__(self, *values, operator=None):
        super().__init__(self, *values, operator=None)
        if not all(
            isinstance(value, Equation)
            or issubclass(value, Operand)
            for value in values
        ):
            raise TypeError([type(value) for value in values])
        if operator is not None:
            if operator not in self.Operators:
                raise TypeError(type(operator))
            elif len(values) != operator.value.operands:
                raise ValueError(operator, values)
        self.operator = operator
        self.values = tuple(value() for value in values)
    
    def __bool__(self):
        return len(self.values) > 0
    
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

class Operand(ExpressionBase):

    @property
    def params(self):
        return set(
            param.name
            for param in signature(getattr(self, self.calc)).parameters.values()
            if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
        )
    
    @property
    def required_params(self):
        return set(
            param.name
            for param in signature(getattr(self, self.calc)).parameters.values()
            if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
            if param.default is Parameter.empty
        )