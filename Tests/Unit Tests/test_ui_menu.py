import unittest
from unittest.mock import patch, MagicMock
import pyray as pr
from Graphics.UI.ui_menu import MainMenuScreen, AppScreen
from Simulation.sim_modes import SimulationMode

class TestMainMenuScreen(unittest.TestCase):
    """Tests MainMenuScreen UI navigation and modal simulation selection."""

    def setUp(self) -> None:
        self.screen = MainMenuScreen()

    @patch('pyray.get_screen_width', return_value=1024)
    @patch('pyray.get_screen_height', return_value=768)
    @patch('pyray.measure_text', return_value=100)
    @patch('pyray.draw_rectangle')
    @patch('pyray.draw_rectangle_rounded')
    @patch('pyray.draw_rectangle_rounded_lines')
    @patch('pyray.draw_text')
    @patch('pyray.draw_line')
    def test_modal_navigation(self, *args) -> None:
        """Verify opening modal and selecting simulation mode returns correct intent."""
        mock_app = MagicMock()

        # Initially modal is closed
        self.assertFalse(self.screen.show_new_sim_modal)

        # Simulate clicking 'New Simulation' button
        with patch.object(self.screen.btn_new_sim, 'update_and_draw', return_value=True):
            res = self.screen.update_and_draw(mock_app)
            self.assertEqual(res, AppScreen.MAIN_MENU)
            self.assertTrue(self.screen.show_new_sim_modal)

        # Simulate clicking '3D Kinematics' modal option
        with patch.object(self.screen.btn_m_3d, 'update_and_draw', return_value=True):
            with patch.object(self.screen.btn_m_2d, 'update_and_draw', return_value=False):
                res = self.screen.update_and_draw(mock_app)
                self.assertEqual(res, AppScreen.SIMULATION)
                self.assertFalse(self.screen.show_new_sim_modal)
                mock_app.switch_mode.assert_called_once_with(SimulationMode.KINEMATICS_3D)

if __name__ == '__main__':
    unittest.main()
