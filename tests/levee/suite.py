import os
import unittest

def run_suite():    
    unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.discover(
            os.path.abspath(os.path.dirname(__file__)),
            pattern='test_*.py',
        )
    )

if __name__ == '__main__':
    run_suite()
