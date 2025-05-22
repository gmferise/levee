from util.import_relative import enable_imports
enable_imports(__file__, '../../src')

import unittest
from unittest.mock import Mock, call
from levee import Chart, State, Effect
from levee.exceptions import TransitionMissingArgs

mockFn = Mock()

class TestChart(Chart):
    class ALPHA(State): pass
    class BETA(State): pass

    class CallMock(Effect):

        def exec(self, whatever):
            mockFn(whatever)

    chart = {
        ALPHA: {
            BETA [CallMock]: ...,
        },
        BETA: {
            ALPHA [CallMock + CallMock]: ...,
        },
    }

class Tests(unittest.TestCase):

    def setUp(self):
        self.data = { 'state': None }
        self.chart = TestChart(self.data)
        self.mockFn = mockFn
        mockFn.reset_mock()
    
    def test_call_mock(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.mockFn.assert_not_called()
        self.assertRaises(TransitionMissingArgs, self.chart.can, TestChart.BETA)
        self.assertEqual(self.chart.can(TestChart.BETA, whatever='whatever'), True)
        self.assertRaises(TransitionMissingArgs, self.chart.to, TestChart.BETA)
        self.chart.to(TestChart.BETA, whatever='whatever')
        self.mockFn.assert_called_once_with('whatever')
    
    def test_call_mock_multiple(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.mockFn.assert_not_called()
        self.chart.to(TestChart.BETA, whatever='once')
        self.mockFn.assert_called_once_with('once')
        self.chart.to(TestChart.ALPHA, whatever='twice')
        self.mockFn.assert_has_calls((call('once'), call('twice'), call('twice')))