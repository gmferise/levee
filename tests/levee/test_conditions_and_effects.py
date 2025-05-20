from util.import_relative import enable_imports
enable_imports(__file__, '../../src')

import unittest
from unittest.mock import Mock, call
from levee import Chart, State, Condition, Effect
from levee.exceptions import TransitionMissingArgs, TransitionNotAllowed

mockFn = Mock()

class TestChart(Chart):
    class ALPHA(State): pass
    class BETA(State): pass

    class Sometimes(Condition):

        def eval(self, sometimes):
            return sometimes
    
    class Maybe(Condition):

        def eval(self, maybe):
            return maybe if maybe else 'I guess not'

    class CallMock(Effect):

        def exec(self, whatever):
            mockFn(whatever)

    chart = {
        ALPHA: {
            BETA (Sometimes) [CallMock]: ...,
        },
        BETA: {
            ALPHA (Sometimes & Maybe) [CallMock + CallMock]: ...,
        },
    }

class TestConditions(unittest.TestCase):

    def setUp(self):
        self.data = { 'state': None }
        self.chart = TestChart(self.data)
        self.mockFn = mockFn
        mockFn.reset_mock()
    
    def test_call_mock(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.mockFn.assert_not_called()
        self.assertRaises(TransitionMissingArgs, self.chart.can, TestChart.BETA)
        self.assertRaises(TransitionMissingArgs, self.chart.can, TestChart.BETA, sometimes=True)
        self.assertEqual(self.chart.can(TestChart.BETA, whatever='whatever', sometimes=True), True)
        self.assertEqual(self.chart.can(TestChart.BETA, whatever='whatever', sometimes=False), False)
        self.assertRaises(TransitionMissingArgs, self.chart.to, TestChart.BETA)
        self.assertRaises(TransitionMissingArgs, self.chart.to, TestChart.BETA, sometimes=True)
        self.assertRaises(TransitionMissingArgs, self.chart.to, TestChart.BETA, whatever='whatever')
        self.chart.to(TestChart.BETA, whatever='whatever', sometimes=True)
        self.mockFn.assert_called_once_with('whatever')
    
    def test_call_mock_multiple(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.mockFn.assert_not_called()
        self.chart.to(TestChart.BETA, whatever='once', sometimes=True)
        self.mockFn.assert_called_once_with('once')
        self.assertRaises(TransitionMissingArgs, self.chart.can, TestChart.ALPHA)
        self.assertRaises(TransitionMissingArgs, self.chart.can, TestChart.ALPHA, sometimes=True)
        self.assertRaises(TransitionMissingArgs, self.chart.can, TestChart.ALPHA, maybe=True)
        self.assertRaises(TransitionMissingArgs, self.chart.can, TestChart.ALPHA, whatever='twice')
        self.assertRaises(TransitionMissingArgs, self.chart.can, TestChart.ALPHA, sometimes=True, maybe=True)
        self.assertRaises(TransitionNotAllowed, self.chart.to, TestChart.ALPHA, sometimes=True, maybe=False, whatever='twice')
        self.assertEqual(self.chart.can(TestChart.ALPHA, sometimes=True, maybe=False, whatever='twice'), False)
        self.assertEqual(self.chart.can(TestChart.ALPHA, sometimes=True, maybe=True, whatever='twice'), True)
        self.chart.to(TestChart.ALPHA, whatever='twice', sometimes=True, maybe=True)
        self.mockFn.assert_has_calls((call('once'), call('twice'), call('twice')))