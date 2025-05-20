import sys, os

def enable_imports(file, relative):
    """
    Enable importing from a directory relative to the current __file__
    """
    sys.path.insert(
        0,
        os.path.abspath(
            os.path.join(
                os.path.dirname(file),
                *relative.split('/'),
            )
        )
    )