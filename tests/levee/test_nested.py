from util.import_relative import enable_imports
enable_imports(__file__, '../../src')

import unittest
from levee import Chart, State

class TestChart(Chart):
    class ALPHA(State): pass
    class BETA(State): pass
    class GAMMA(State): pass

    chart = {
        ALPHA: {
            BETA: {
                GAMMA: {
                    ALPHA: ...,
                },
            },
        },
    }

class TestNested(unittest.TestCase):

    def setUp(self):
        self.data = { 'state': None }
        self.chart = TestChart(self.data)
    
    def test_all_transitions(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.assertEqual(self.data['state'], 'ALPHA')
        self.chart.to(TestChart.BETA)
        self.assertEqual(self.chart.state, TestChart.BETA)
        self.assertEqual(self.data['state'], 'BETA')
        self.chart.to(TestChart.GAMMA)
        self.assertEqual(self.chart.state, TestChart.GAMMA)
        self.assertEqual(self.data['state'], 'GAMMA')
        self.chart.to(TestChart.ALPHA)
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.assertEqual(self.data['state'], 'ALPHA')
