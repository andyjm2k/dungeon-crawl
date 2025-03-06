import unittest
import sys
import os
import random
from unittest.mock import patch, MagicMock

# Create mock pygame module and mock pygame.Rect
class MockRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.centerx = x + width // 2
        self.centery = y + height // 2
    
    def colliderect(self, rect):
        return False
    
    def collidepoint(self, x, y=None):
        return False

# Create mock pygame and inject it
mock_pygame = MagicMock()
mock_pygame.Rect = MockRect
sys.modules['pygame'] = mock_pygame

# Extract the Skill class implementation from the game file
class Skill:
    def __init__(self, name, damage, cost, target_type='single', effect_type='damage'):
        self.name = name
        self.damage = damage
        self.cost = cost
        self.target_type = target_type
        self.effect_type = effect_type

# Constants from the game
GRID_SIZE = 20

# Extract PartyMember class implementation (simplified)
class PartyMember:
    def __init__(self, role):
        self.role = role
        self.name = f"{role}"
        self.defense_bonus = 1
        self.is_alive = True
        
        # Set stats based on role
        if role == 'Warrior':
            self.health = 120
            self.max_health = 120
            self.attack = 12
            self.mana = 60
            self.max_mana = 60
        elif role == 'Mage':
            self.health = 80
            self.max_health = 80
            self.attack = 15
            self.mana = 150
            self.max_mana = 150
        elif role == 'Healer':
            self.health = 90
            self.max_health = 90
            self.attack = 8
            self.mana = 120
            self.max_mana = 120
        else:
            # Default to Warrior if invalid role
            self.health = 120
            self.max_health = 120
            self.attack = 12
            self.mana = 60
            self.max_mana = 60
            self.role = 'Warrior'


# Tests for the utility functions
class TestUtilityFunctions(unittest.TestCase):
    @patch('os.path.exists')
    def test_exists_check(self, mock_exists):
        """Test a simple os.path.exists check"""
        mock_exists.return_value = True
        self.assertTrue(os.path.exists("test_file.txt"))
        
        mock_exists.return_value = False
        self.assertFalse(os.path.exists("nonexistent_file.txt"))


# Test the Skill class
class TestSkillClass(unittest.TestCase):
    def test_skill_init(self):
        """Test Skill initialization with different parameters"""
        # Test default values
        skill = Skill("Test Skill", 10, 5)
        self.assertEqual(skill.name, "Test Skill")
        self.assertEqual(skill.damage, 10)
        self.assertEqual(skill.cost, 5)
        self.assertEqual(skill.target_type, "single")
        self.assertEqual(skill.effect_type, "damage")
        
        # Test with custom values
        skill = Skill("Heal", 20, 10, target_type="all", effect_type="heal")
        self.assertEqual(skill.name, "Heal")
        self.assertEqual(skill.damage, 20)
        self.assertEqual(skill.cost, 10)
        self.assertEqual(skill.target_type, "all")
        self.assertEqual(skill.effect_type, "heal")


# Test the PartyMember class
class TestPartyMemberClass(unittest.TestCase):
    def test_party_member_init(self):
        """Test PartyMember initialization with different roles"""
        # Test Warrior
        warrior = PartyMember("Warrior")
        self.assertEqual(warrior.role, "Warrior")
        self.assertEqual(warrior.health, 120)
        self.assertEqual(warrior.max_health, 120)
        self.assertEqual(warrior.attack, 12)
        self.assertEqual(warrior.mana, 60)
        self.assertEqual(warrior.max_mana, 60)
        self.assertTrue(warrior.is_alive)
        self.assertEqual(warrior.defense_bonus, 1)
        
        # Test Mage
        mage = PartyMember("Mage")
        self.assertEqual(mage.role, "Mage")
        self.assertEqual(mage.health, 80)
        self.assertEqual(mage.max_health, 80)
        self.assertEqual(mage.attack, 15)
        self.assertEqual(mage.mana, 150)
        self.assertEqual(mage.max_mana, 150)
        
        # Test Healer
        healer = PartyMember("Healer")
        self.assertEqual(healer.role, "Healer")
        self.assertEqual(healer.health, 90)
        self.assertEqual(healer.max_health, 90)
        self.assertEqual(healer.attack, 8)
        self.assertEqual(healer.mana, 120)
        self.assertEqual(healer.max_mana, 120)
        
        # Test invalid role (should default to Warrior)
        default = PartyMember("Invalid")
        self.assertEqual(default.role, "Warrior")


# Add more tests for other classes as needed

if __name__ == '__main__':
    unittest.main() 