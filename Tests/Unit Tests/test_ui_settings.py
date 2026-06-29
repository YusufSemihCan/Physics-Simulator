import unittest
from unittest.mock import patch, MagicMock
import pyray as pr
from Graphics.UI.ui_settings import SettingsScreen
from Graphics.UI.ui_menu import AppScreen

class TestSettingsScreen(unittest.TestCase):
    """Tests resolution and display mode selection branches in SettingsScreen."""

    def setUp(self) -> None:
        self.mock_renderer = MagicMock()
        self.mock_renderer.resolutions = [(1280, 720), (1920, 1080)]
        self.mock_renderer.res_index = 0
        self.screen = SettingsScreen(self.mock_renderer)
        
        # Mock selectors so they don't invoke pyray drawing functions
        self.screen.sel_top_bar.update_and_draw = MagicMock(return_value=(False, 1))
        self.screen.sel_bot_bar.update_and_draw = MagicMock(return_value=(False, 1))
        self.screen.sel_sidebar.update_and_draw = MagicMock(return_value=(False, 0))

    @patch('pyray.get_screen_width', return_value=1280)
    @patch('pyray.get_screen_height', return_value=720)
    @patch('pyray.measure_text', return_value=100)
    @patch('pyray.draw_rectangle')
    @patch('pyray.draw_triangle')
    @patch('pyray.draw_rectangle_rounded')
    @patch('pyray.draw_rectangle_rounded_lines')
    @patch('pyray.draw_text')
    @patch('pyray.draw_line')
    @patch('pyray.set_window_size')
    @patch('pyray.is_window_fullscreen')
    @patch('pyray.is_window_state')
    @patch('pyray.toggle_borderless_windowed')
    @patch('pyray.toggle_fullscreen')
    def test_resolution_and_mode_branches(self, mock_toggle_fs, mock_toggle_bw, mock_state, mock_fs, mock_set_size, *args) -> None:
        """Verify changing resolution updates renderer and match/case display mode switches window state."""
        # Test 1: Resolution Change
        with patch.object(self.screen.sel_res, 'update_and_draw', return_value=(True, 1)):
            with patch.object(self.screen.sel_mode, 'update_and_draw', return_value=(False, 0)):
                with patch.object(self.screen.btn_back, 'update_and_draw', return_value=False):
                    res = self.screen.update_and_draw()
                    self.assertEqual(res, AppScreen.SETTINGS)
                    self.assertEqual(self.mock_renderer.res_index, 1)
                    mock_set_size.assert_called_with(1920, 1080)

        mock_set_size.reset_mock()

        # Test 2: Switch to Windowed when currently Fullscreen
        mock_fs.return_value = True
        mock_state.return_value = False
        with patch.object(self.screen.sel_res, 'update_and_draw', return_value=(False, 1)):
            with patch.object(self.screen.sel_mode, 'update_and_draw', return_value=(True, 0)): # 0 = Windowed
                with patch.object(self.screen.btn_back, 'update_and_draw', return_value=False):
                    self.screen.update_and_draw()
                    mock_toggle_fs.assert_called_once()
                    mock_set_size.assert_called_with(1920, 1080)

        mock_toggle_fs.reset_mock()
        mock_toggle_bw.reset_mock()

        # Test 3: Switch to Borderless Windowed when currently windowed
        mock_fs.return_value = False
        mock_state.return_value = False
        with patch.object(self.screen.sel_res, 'update_and_draw', return_value=(False, 1)):
            with patch.object(self.screen.sel_mode, 'update_and_draw', return_value=(True, 1)): # 1 = Borderless Windowed
                with patch.object(self.screen.btn_back, 'update_and_draw', return_value=False):
                    self.screen.update_and_draw()
                    mock_toggle_bw.assert_called_once()

if __name__ == '__main__':
    unittest.main()
