import unittest
import os
import shutil
from Graphics.UI.ui_menu import MainMenuScreen, AppScreen
from Graphics.UI.ui_load_scenario import LoadScenarioScreen
from Simulation.sim_scenarios import ScenarioManager

class DummyApp:
    def __init__(self, scenarios):
        self.scenarios = scenarios

class TestUILoadScenario(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_scenarios_ui"
        os.makedirs(self.test_dir, exist_ok=True)
        self.scenarios = ScenarioManager(self.test_dir)
        self.app = DummyApp(self.scenarios)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_main_menu_buttons_and_navigation(self):
        menu = MainMenuScreen()
        self.assertTrue(hasattr(menu, 'btn_load'))
        self.assertEqual(menu.btn_load.text, "Load Scenario (Browse & Preview)")

    def test_load_scenario_screen_initialization_and_selection(self):
        screen = LoadScenarioScreen(self.app)
        options = screen.selector.options
        self.assertGreaterEqual(len(options), 1)
        
        selected = screen.get_selected_scenario()
        self.assertIn(selected, options)

        # Test refresh logic
        screen.refresh_list()
        self.assertIsNone(screen.last_selected_name)

if __name__ == "__main__":
    unittest.main()
