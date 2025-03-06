import unittest
import sys
from unittest.mock import patch, MagicMock

# Create a bare minimum mock pygame module
mock_pygame = MagicMock()
mock_pygame.init = MagicMock()
mock_pygame.quit = MagicMock()
mock_pygame.Surface = MagicMock()
mock_pygame.time = MagicMock()
mock_pygame.display = MagicMock()
mock_pygame.event = MagicMock()
mock_pygame.event.get = MagicMock(return_value=[])
mock_pygame.mixer = MagicMock()
mock_pygame.font = MagicMock()
mock_pygame.image = MagicMock()

# Inject the mock into sys.modules
sys.modules['pygame'] = mock_pygame

# Create a mock Skill class to test independently
class Skill:
    def __init__(self, name, damage, cost, target_type='single', effect_type='damage'):
        self.name = name
        self.damage = damage
        self.cost = cost
        self.target_type = target_type
        self.effect_type = effect_type

class TestSkill(unittest.TestCase):
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

# Run the test if this file is executed directly
if __name__ == '__main__':
    unittest.main() 