#!/usr/bin/env python3
"""
Test suite for the GEDCOM parser
"""

import unittest
import sys
import os

# Add src to path so we can import the parser
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from gedcom_parser import GEDCOMParser, GenealogyQueryEngine

class TestGEDCOMParser(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Use relative path from tests directory
        gedcom_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'Arbre 31_08_2025.ged')
        self.parser = GEDCOMParser(gedcom_path)
        
    def test_parser_initialization(self):
        """Test that parser initializes correctly"""
        expected_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'Arbre 31_08_2025.ged')
        expected_path = os.path.normpath(expected_path)
        actual_path = os.path.normpath(self.parser.gedcom_file)
        self.assertEqual(actual_path, expected_path)
        self.assertEqual(self.parser.individuals, {})
        self.assertEqual(self.parser.families, {})
        self.assertEqual(self.parser.lines, [])
        
    def test_parse_returns_dict(self):
        """Test that parse method returns a dictionary"""
        result = self.parser.parse()
        self.assertIsInstance(result, dict)
        
    def test_parse_has_individuals_and_families(self):
        """Test that parsed data has individuals and families"""
        result = self.parser.parse()
        self.assertIn('individuals', result)
        self.assertIn('families', result)
        
    def test_query_engine_initialization(self):
        """Test that query engine initializes correctly"""
        data = self.parser.parse()
        query_engine = GenealogyQueryEngine(data)
        self.assertEqual(query_engine.data, data)
        self.assertEqual(query_engine.individuals, data['individuals'])
        self.assertEqual(query_engine.families, data['families'])

if __name__ == '__main__':
    unittest.main()