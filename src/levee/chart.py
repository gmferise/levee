from inspect import isclass, signature

class ChartMeta(type):
    
    def __init__(self, name, extends, attrs, **kwargs):
        # TODO: Parse States and diagram
        return super().__init__(name, extends, attrs, **kwargs)

class Chart(metaclass=ChartMeta):
    """
    Extend this class and define possible ``States`` inside.
    Then, use those ``States`` in a ``diagram`` to declare how they can be
    transitioned between.

    To your transitions, you can add ``Conditions`` with parenthesis and
    ``Effects`` with square brackets.

    ``Conditions`` and ``Effects`` for ``States`` at the root level of the
    ``diagram`` will always be used when that state is transitioned to.
    """
    diagram = {}