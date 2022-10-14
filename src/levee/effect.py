from inspect import Parameter, signature, isclass
from levee.exceptions import LeveeException

class ChainableOps():

    def __add__(self, other):
        return EffectChain(self, other)

class ChainableMeta(ChainableOps, type):

    def __init__(self, name, extends, attrs, **kwargs):
        allowed_kinds = [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]
        if self._allow_kwargs:
            allowed_kinds.append(Parameter.VAR_KEYWORD)
        if any(
            param.kind not in allowed_kinds
            for param in signature(self.exec).parameters.values()
        ):
            raise LeveeException(f'{name}: Parameters for ``exec`` must be must be passable by keyword and non-variable')
        return super().__init__(name, extends, attrs, **kwargs)

    def __str__(self):
        return self.__name__

class Chainable(ChainableOps, metaclass=ChainableMeta):

    _allow_kwargs = False

    def exec(self):
        pass

    @property
    def params(self):
        return set()
    
    @property
    def required_params(self):
        return set()

class EffectChain(Chainable):

    _allow_kwargs = True

    def __init__(self, *expression):
        self.values = []
        for operand in expression:
            if isinstance(operand, EffectChain):
                self.values.extend(operand.values)
            elif isclass(operand) and issubclass(operand, Effect):
                self.values.append(operand())
            else:
                raise TypeError(type(operand))

    def exec(self, **kwargs):
        for effect in self.values:
            effect.exec(**kwargs)
    
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
        inner = ' + '.join(str(value) for value in self.values)
        return f'[{inner}]' if inner else ''

class Effect(Chainable):
    """
    Extend this class and define logic in its ``exec`` function.
    Named arguments can be added to the ``exec`` signature to require these
    arguments to be provided when calling ``Chart.to()``.

    ``Effects`` can be added to a transition with this chart syntax:
    ```
    FROM_STATE: {
        TO_STATE [Effect1 + Effect2 + Effect3]: ...
    }
    ```
    """

    def exec(self):
        pass

    @property
    def params(self):
        return set(
            param.name
            for param in signature(self.exec).parameters.values()
            if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
        )
    
    @property
    def required_params(self):
        return set(
            param.name
            for param in signature(self.exec).parameters.values()
            if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
            if param.default is Parameter.empty
        )