import unittest
from unittest.mock import patch, MagicMock
import pyray as pr
from Graphics.Rendering.render_window import SimulationRenderer

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

if __name__ == '__main__':
    unittest.main()
