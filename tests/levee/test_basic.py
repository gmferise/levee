from util.import_relative import enable_imports
enable_imports(__file__, '../../src')

import unittest
from levee import Chart, State
from levee.exceptions import TransitionError

class TestChart(Chart):
    class ALPHA(State): pass
    class BETA(State): pass
    class GAMMA(State): pass

    chart = {
        ALPHA: {
            ALPHA: ...,
            BETA: ...,
        },
        BETA: {
            GAMMA: ...,
        },
        GAMMA: {
            ALPHA: ...,
        },
    }

class TestBasic(unittest.TestCase):

    def setUp(self):
        self.data = { 'state': None }
        self.chart = TestChart(self.data)
    
    def test_all_transitions(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.assertEqual(self.data['state'], TestChart.ALPHA.value)
        result = self.chart.to(TestChart.ALPHA)
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.assertEqual(result, self.chart.state)
        self.assertEqual(self.data['state'], TestChart.ALPHA.value)
        result = self.chart.to(TestChart.BETA)
        self.assertEqual(self.chart.state, TestChart.BETA)
        self.assertEqual(result, self.chart.state)
        self.assertEqual(self.data['state'], TestChart.BETA.value)
        result = self.chart.to(TestChart.GAMMA)
        self.assertEqual(self.chart.state, TestChart.GAMMA)
        self.assertEqual(result, self.chart.state)
        self.assertEqual(self.data['state'], TestChart.GAMMA.value)
        result = self.chart.to(TestChart.ALPHA)
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.assertEqual(result, self.chart.state)
        self.assertEqual(self.data['state'], TestChart.ALPHA.value)
    
    def test_string_transition(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.chart.to('BETA')
        self.assertEqual(self.chart.state, TestChart.BETA)
    
    def test_invalid_transition(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.assertRaises(TransitionError, self.chart.to, TestChart.GAMMA)
        self.assertEqual(self.chart.state, TestChart.ALPHA)
    
    def test_invalid_string(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.assertRaises(TransitionError, self.chart.to, 'DELTA')
        self.assertEqual(self.chart.state, TestChart.ALPHA)
