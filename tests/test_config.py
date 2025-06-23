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
        """Test that config.json has all required template keys."""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = ['front_template', 'back_template', 'css']
        for key in required_keys:
            self.assertIn(key, config, f"Config should contain {key}")

    def test_templates_have_required_fields(self):
        """Test that templates contain the expected field placeholders."""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        # Front template should contain Word field
        self.assertIn('{{Word}}', config['front_template'], 
                     "Front template should contain {{Word}} field")
        
        # Back template should contain Definition field
        self.assertIn('{{Definition}}', config['back_template'],
                     "Back template should contain {{Definition}} field")


if __name__ == '__main__':
    unittest.main() 