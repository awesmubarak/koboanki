"""Tests for addon configuration functionality."""

import json
import os
import unittest
from pathlib import Path


class TestConfig(unittest.TestCase):
    """Test configuration loading and template functionality."""

    def setUp(self):
        """Set up test paths."""
        self.project_root = Path(__file__).parent.parent
        self.addon_path = self.project_root / "koboanki"
        self.config_path = self.addon_path / "config.json"

    def test_config_json_exists(self):
        """Test that config.json exists and is valid JSON."""
        self.assertTrue(self.config_path.exists(), "config.json should exist")
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        self.assertIsInstance(config, dict, "Config should be a dictionary")

    def test_config_has_required_keys(self):
        """Test that config.json has all required keys for the new system."""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = ['deck_name', 'card_level']
        for key in required_keys:
            self.assertIn(key, config, f"Config should contain {key}")

    def test_card_level_is_valid(self):
        """Test that card_level is set to a valid value."""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        valid_levels = ['basic', 'intermediate', 'full']
        card_level = config.get('card_level')
        
        self.assertIn(card_level, valid_levels, 
                     f"card_level should be one of {valid_levels}, got {card_level}")

    def test_deck_name_is_string(self):
        """Test that deck_name is a non-empty string."""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        deck_name = config.get('deck_name')
        self.assertIsInstance(deck_name, str, "deck_name should be a string")
        self.assertTrue(len(deck_name) > 0, "deck_name should not be empty")


if __name__ == '__main__':
    unittest.main() 