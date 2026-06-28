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
        self.assertEqual(menu.btn_load.text, "Load Scenario File Tree")

    def test_load_scenario_screen_initialization_and_selection(self):
        screen = LoadScenarioScreen(self.app)
        options = screen.selector.options
        self.assertGreaterEqual(len(options), 1)
        
        selected = screen.get_selected_scenario()
        self.assertIn(selected, options)

        # Test refresh logic
        screen.refresh_list()
        self.assertIsNone(screen.last_selected_name)

    def test_scenario_folder_management(self):
        screen = LoadScenarioScreen(self.app)
        self.assertTrue(hasattr(screen, 'btn_new_folder'))
        
        # Test folder creation
        self.scenarios.create_folder("Classroom")
        marker_file = os.path.join(self.test_dir, "Classroom", ".folder")
        self.assertTrue(os.path.exists(marker_file))
        screen.refresh_list()
        self.assertIn("Classroom", screen.selector.options)
        self.assertTrue(screen.is_item_folder("Classroom"))

        # Test move scenario (drag and drop rearrangement)
        res = self.scenarios.move_scenario("Single Sphere", "Classroom")
        self.assertTrue(res)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "Classroom", "Single Sphere.json")))
        # Move back to root
        self.scenarios.move_scenario("Classroom/Single Sphere", "")
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "Single Sphere.json")))

        # Test folder deletion
        self.scenarios.delete_scenario("Classroom")
        screen.refresh_list()
        self.assertNotIn("Classroom", screen.selector.options)

    def test_scenario_renaming(self):
        screen = LoadScenarioScreen(self.app)
        self.assertTrue(hasattr(screen, 'btn_rename'))
        
        # Test renaming file
        res = self.scenarios.rename_scenario("Single Sphere", "Renamed Sphere")
        self.assertTrue(res)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "Renamed Sphere.json")))
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, "Single Sphere.json")))
        
        # Rename back
        self.scenarios.rename_scenario("Renamed Sphere", "Single Sphere")

if __name__ == "__main__":
    unittest.main()
