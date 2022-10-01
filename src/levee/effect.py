class ChainableOps():

    def __add__(self, other):
        return EffectChain(self, other)

class ChainableMeta(ChainableOps, type):
    
    def __str__(self):
        return self.__name__

class Chainable(ChainableOps, metaclass=ChainableMeta):

    def exec(self, **kwargs):
        pass

class EffectChain(Chainable):

    def __init__(self, *expression):
        self.values = []
        for operand in expression:
            if isinstance(operand, EffectChain):
                self.values.extend(operand.values)
            elif issubclass(operand, Effect):
                self.values.append(operand)
            else:
                raise TypeError(type(operand))
    
    def exec(self, **kwargs):
        for effect in self.values:
            effect.exec(**kwargs)
    
    def __str__(self):
        inner = ' + '.join(str(value) for value in self.values)
        return f'[{inner}]' if inner else ''

class Effect(Chainable):

    def exec(self, **kwargs):
        pass