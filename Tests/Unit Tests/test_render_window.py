import unittest
from unittest.mock import patch, MagicMock
import pyray as pr
from Graphics.Rendering.render_window import SimulationRenderer
from Graphics.UI.ui_menu import AppScreen

class TestRenderWindowDispatch(unittest.TestCase):
    """Tests keyboard dispatch table in SimulationRenderer to ensure reliable hotkey handling."""

    @patch('pyray.init_window')
    @patch('pyray.set_target_fps')
    @patch('pyray.set_window_size')
    @patch('pyray.toggle_borderless_windowed')
    def test_key_actions_dispatch_table(self, mock_borderless, mock_set_size, mock_fps, mock_init) -> None:
        """Verify key actions table mappings, execution of actions, and unknown key fallbacks."""
        app = SimulationRenderer()

        # Check known keys are present
        known_keys = [
            pr.KeyboardKey.KEY_P,
            pr.KeyboardKey.KEY_SPACE,
            pr.KeyboardKey.KEY_S,
            pr.KeyboardKey.KEY_G,
            pr.KeyboardKey.KEY_V,
            pr.KeyboardKey.KEY_T,
            pr.KeyboardKey.KEY_F11,
            pr.KeyboardKey.KEY_B,
            pr.KeyboardKey.KEY_R,
        ]
        for key in known_keys:
            self.assertIn(key, app._key_actions)

        # Verify unknown key falls back cleanly
        self.assertIsNone(app._key_actions.get(pr.KeyboardKey.KEY_Z, None))

        # Test G key toggles grid
        initial_grid = app.grid.show_grid
        app._key_actions[pr.KeyboardKey.KEY_G]()
        self.assertNotEqual(app.grid.show_grid, initial_grid)

        # Test R key cycles resolution
        initial_res = app.res_index
        app._key_actions[pr.KeyboardKey.KEY_R]()
        self.assertNotEqual(app.res_index, initial_res)
        mock_set_size.assert_called()

        # Test F11 calls toggle_borderless_windowed
        app._key_actions[pr.KeyboardKey.KEY_F11]()
        mock_borderless.assert_called_once()

    @patch('pyray.init_window')
    @patch('pyray.set_target_fps')
    @patch('pyray.get_mouse_position')
    @patch('pyray.is_key_down')
    @patch('pyray.get_mouse_wheel_move')
    @patch('pyray.is_mouse_button_pressed')
    @patch('pyray.is_mouse_button_down')
    def test_shift_mouse_wheel_height(self, mock_mb_down, mock_mb_pressed, mock_wheel, mock_key_down, mock_mouse_pos, *args) -> None:
        """Verify holding Shift and scrolling mouse wheel adjusts spawn height."""
        app = SimulationRenderer()
        app.current_screen = AppScreen.SIMULATION
        mock_mouse_pos.return_value = pr.Vector2(100, 100)
        mock_key_down.return_value = True
        mock_wheel.return_value = 2.0
        mock_mb_pressed.return_value = False
        mock_mb_down.return_value = False

        initial_spawn_h = app.spawn_height
        app.handle_input()
        self.assertAlmostEqual(app.spawn_height, initial_spawn_h + 1.0)

    @patch('pyray.init_window')
    @patch('pyray.set_target_fps')
    @patch('pyray.get_mouse_position')
    @patch('pyray.is_key_down')
    @patch('pyray.get_mouse_wheel_move')
    @patch('pyray.is_mouse_button_pressed')
    @patch('pyray.is_mouse_button_down')
    def test_shift_mouse_wheel_selected_shape_height(self, mock_mb_down, mock_mb_pressed, mock_wheel, mock_key_down, mock_mouse_pos, *args) -> None:
        """Verify holding Shift and scrolling mouse wheel adjusts selected shape Y position."""
        app = SimulationRenderer()
        app.current_screen = AppScreen.SIMULATION
        mock_mouse_pos.return_value = pr.Vector2(100, 100)
        mock_key_down.return_value = True
        mock_wheel.return_value = -2.0
        mock_mb_pressed.return_value = False
        mock_mb_down.return_value = False

        mock_shape = MagicMock()
        mock_shape.pos = pr.Vector3(0.0, 10.0, 0.0)
        mock_shape.vel = pr.Vector3(0.0, -5.0, 0.0)
        app.selected_shape = mock_shape

        app.handle_input()
        self.assertAlmostEqual(mock_shape.pos.y, 9.0)
        self.assertAlmostEqual(mock_shape.vel.y, 0.0)

if __name__ == '__main__':
    unittest.main()
