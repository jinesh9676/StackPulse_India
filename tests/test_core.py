import unittest
from utils.calculations import calculate
class TestCore(unittest.TestCase):
    def test_loss(self):
        x=calculate(2,3000,2500)
        self.assertEqual(x['profit'],-1000)
        self.assertAlmostEqual(x['required_gain'],20)
    def test_missing(self): self.assertIsNone(calculate(1,100,None)['value'])
    def test_profit(self): self.assertEqual(calculate(2,100,120)['profit'],40)
