class LeveeException(Exception):
    """Catch any exception generated by this package"""
    pass

class ChartError(LeveeException): pass
class ChartSyntaxError(ChartError): pass

class TransitionError(LeveeException): pass
class TransitionDoesNotExist(TransitionError): pass
class TransitionMissingData(TransitionError): pass
class TransitionNotAllowed(TransitionError): pass