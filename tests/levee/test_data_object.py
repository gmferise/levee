from util.import_relative import enable_imports
enable_imports(__file__, '../../src')

import unittest
from levee import Chart, State

class DataObject:

    def __init__(self):
        self.state = None
        self.state2 = None

class TestChart(Chart):
    class ALPHA(State): pass
    class BETA(State): pass
    class GAMMA(State): pass

    chart = {
        ALPHA: {
            BETA: ...,
        },
        BETA: {
            ALPHA: ...,
        },
    }

class TestDataObject(unittest.TestCase):

    def setUp(self):
        self.data = { 'state': None, 'state2': None }
        self.dataObj = DataObject()
        self.chart1 = TestChart(self.data)
        self.chart2 = TestChart(self.data, 'state2')
        self.chart3 = TestChart(self.dataObj)
        self.chart4 = TestChart(self.dataObj, 'state2')
    
    def test_alternate_state(self):
        self.chart1.to(TestChart.BETA)
        self.assertEqual(self.data['state'], TestChart.BETA.value)
        self.assertEqual(self.data['state2'], TestChart.ALPHA.value)
        self.assertEqual(self.dataObj.state, TestChart.ALPHA.value)
        self.assertEqual(self.dataObj.state2, TestChart.ALPHA.value)
        self.chart2.to(TestChart.BETA)
        self.assertEqual(self.data['state'], TestChart.BETA.value)
        self.assertEqual(self.data['state2'], TestChart.BETA.value)
        self.assertEqual(self.dataObj.state, TestChart.ALPHA.value)
        self.assertEqual(self.dataObj.state2, TestChart.ALPHA.value)
        self.chart3.to(TestChart.BETA)
        self.assertEqual(self.data['state'], TestChart.BETA.value)
        self.assertEqual(self.data['state2'], TestChart.BETA.value)
        self.assertEqual(self.dataObj.state, TestChart.BETA.value)
        self.assertEqual(self.dataObj.state2, TestChart.ALPHA.value)
        self.chart4.to(TestChart.BETA)
        self.assertEqual(self.data['state'], TestChart.BETA.value)
        self.assertEqual(self.data['state2'], TestChart.BETA.value)
        self.assertEqual(self.dataObj.state, TestChart.BETA.value)
        self.assertEqual(self.dataObj.state2, TestChart.BETA.value)
    
    def test_state_mutation(self):
        self.data['state'] = TestChart.BETA.value
        self.assertEqual(self.chart1.state, TestChart.BETA)
        self.assertEqual(self.chart2.state, TestChart.ALPHA)
        self.assertEqual(self.chart3.state, TestChart.ALPHA)
        self.assertEqual(self.chart4.state, TestChart.ALPHA)
        self.data['state2'] = TestChart.BETA.value
        self.assertEqual(self.chart1.state, TestChart.BETA)
        self.assertEqual(self.chart2.state, TestChart.BETA)
        self.assertEqual(self.chart3.state, TestChart.ALPHA)
        self.assertEqual(self.chart4.state, TestChart.ALPHA)
        self.dataObj.state = TestChart.BETA.value
        self.assertEqual(self.chart1.state, TestChart.BETA)
        self.assertEqual(self.chart2.state, TestChart.BETA)
        self.assertEqual(self.chart3.state, TestChart.BETA)
        self.assertEqual(self.chart4.state, TestChart.ALPHA)
        self.dataObj.state2 = TestChart.BETA.value
        self.assertEqual(self.chart1.state, TestChart.BETA)
        self.assertEqual(self.chart2.state, TestChart.BETA)
        self.assertEqual(self.chart3.state, TestChart.BETA)
        self.assertEqual(self.chart4.state, TestChart.BETA)
