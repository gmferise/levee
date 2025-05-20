from util.import_relative import enable_imports
enable_imports(__file__, '../../src')

import unittest
from levee import Chart, State, Condition
from levee.exceptions import TransitionNotAllowed, TransitionMissingArgs

class TestChart(Chart):
    class ALPHA(State): pass
    class BETA(State): pass
    class GAMMA(State): pass

    class Always(Condition):

        def eval(self):
            return True
        
    class Never(Condition):

        def eval(self):
            return False
    
    class Sometimes(Condition):

        def eval(self, sometimes):
            return sometimes
    
    class Maybe(Condition):

        def eval(self, maybe):
            return maybe if maybe else 'I guess not'

    chart = {
        ALPHA: {
            BETA (Always): ...,
            GAMMA (Never): ...,
        },
        BETA: {
            GAMMA (Sometimes): ...,
            ALPHA (~Sometimes): ...,
        },
        GAMMA: {
            ALPHA (Sometimes & Maybe): ...,
            BETA (Sometimes | Maybe): ...,
        },
    }

class TestConditions(unittest.TestCase):

    def setUp(self):
        self.data = { 'state': None }
        self.chart = TestChart(self.data)
    
    def test_always(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.assertEqual(self.chart.can(TestChart.BETA), True)
        self.chart.to(TestChart.BETA)
        self.assertEqual(self.chart.state, TestChart.BETA)
    
    def test_never(self):
        self.assertEqual(self.chart.state, TestChart.ALPHA)
        self.assertEqual(self.chart.can(TestChart.GAMMA), False)
        self.assertRaises(TransitionNotAllowed, self.chart.to, TestChart.GAMMA)
        self.assertEqual(self.chart.state, TestChart.ALPHA)
    
    def test_sometimes(self):
        self.chart.to(TestChart.BETA)
        self.assertEqual(self.chart.state, TestChart.BETA)
        self.assertRaises(TransitionMissingArgs, self.chart.can, TestChart.GAMMA)
        self.assertRaises(TransitionMissingArgs, self.chart.to, TestChart.GAMMA)
        self.assertEqual(self.chart.can(TestChart.GAMMA, sometimes=True), True)
        self.assertEqual(self.chart.can(TestChart.GAMMA, sometimes=False), False)
        self.assertEqual(self.chart.can(TestChart.ALPHA, sometimes=True), False)
        self.assertEqual(self.chart.can(TestChart.ALPHA, sometimes=False), True)
        self.assertEqual(
            ((TestChart.GAMMA.value, TestChart.GAMMA.pretty_value),),
            self.chart.choices(sometimes=True),
        )
        self.assertEqual(
            ((TestChart.ALPHA.value, TestChart.ALPHA.pretty_value),),
            self.chart.choices(sometimes=False),
        )
    
    def test_and(self):
        self.chart.to(TestChart.BETA)
        self.chart.to(TestChart.GAMMA, sometimes=True)
        self.assertEqual(self.chart.state, TestChart.GAMMA)
        self.assertEqual(self.chart.can(TestChart.ALPHA, sometimes=True, maybe=True), True)
        self.assertEqual(self.chart.can(TestChart.ALPHA, sometimes=True, maybe=False), False)
        self.assertEqual(self.chart.can(TestChart.ALPHA, sometimes=False, maybe=True), False)
        self.assertEqual(self.chart.can(TestChart.ALPHA, sometimes=False, maybe=False), False)

    def test_or(self):
        self.chart.to(TestChart.BETA)
        self.chart.to(TestChart.GAMMA, sometimes=True)
        self.assertEqual(self.chart.state, TestChart.GAMMA)
        self.assertEqual(self.chart.can(TestChart.BETA, sometimes=True, maybe=True), True)
        self.assertEqual(self.chart.can(TestChart.BETA, sometimes=True, maybe=False), True)
        self.assertEqual(self.chart.can(TestChart.BETA, sometimes=False, maybe=True), True)
        self.assertEqual(self.chart.can(TestChart.BETA, sometimes=False, maybe=False), False)
        