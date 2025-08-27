import unittest
from django.test import TestCase
from .tools import SettlementCalculator, TerzaghiBearingCapacity
from .knowledge_base import KnowledgeBase
from .agent import TechnicalAgent

class TestSettlementCalculator(TestCase):
    def setUp(self):
        self.calc = SettlementCalculator()
    
    def test_basic_settlement_calculation(self):
        result = self.calc.calculate(100, 25000)
        expected = 100 / 25000
        self.assertAlmostEqual(result['settlement'], expected, places=6)
        self.assertEqual(result['inputs']['load'], 100)
        self.assertEqual(result['inputs']['youngs_modulus'], 25000)
    
    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.calc.calculate(100, 0)  # Zero modulus
        
        with self.assertRaises(ValueError):
            self.calc.calculate(-50, 25000)  # Negative load

class TestTerzaghiBearingCapacity(TestCase):
    def setUp(self):
        self.calc = TerzaghiBearingCapacity()
    
    def test_bearing_capacity_calculation(self):
        # Test with known values
        result = self.calc.calculate(B=2, gamma=18, Df=1.5, friction_angle=30)
        
        # For 30°: Nq ≈ 18.4, Nr ≈ 15.1
        expected = 18 * 1.5 * 18.4 + 0.5 * 18 * 2 * 15.1
        
        self.assertAlmostEqual(result['ultimate_bearing_capacity'], expected, places=1)
        self.assertEqual(result['factors']['Nq'], 18.4)
        self.assertEqual(result['factors']['Nr'], 15.1)
    
    def test_interpolation(self):
        # Test interpolation between known values
        result = self.calc.calculate(B=1, gamma=20, Df=1, friction_angle=32.5)
        self.assertIsInstance(result['ultimate_bearing_capacity'], float)
        self.assertTrue(result['ultimate_bearing_capacity'] > 0)
    
    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.calc.calculate(B=0, gamma=18, Df=1.5, friction_angle=30)  # Zero width
        
        with self.assertRaises(ValueError):
            self.calc.calculate(B=2, gamma=18, Df=1.5, friction_angle=50)  # Invalid angle

class TestKnowledgeBase(TestCase):
    def setUp(self):
        self.kb = KnowledgeBase()
    
    def test_search_functionality(self):
        results = self.kb.search("CPT analysis settlement", k=2)
        self.assertLessEqual(len(results), 2)
        self.assertTrue(all('score' in result for result in results))
        self.assertTrue(all(result['score'] >= 0 for result in results))
    
    def test_document_structure(self):
        self.assertTrue(len(self.kb.documents) >= 5)
        for doc in self.kb.documents:
            self.assertIn('id', doc)
            self.assertIn('title', doc)
            self.assertIn('content', doc)
            self.assertIn('filename', doc)