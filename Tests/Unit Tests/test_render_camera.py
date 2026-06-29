import unittest
from unittest.mock import patch
import math
import pyray as pr
from Graphics.Rendering.render_camera import CameraController

from Graphics.UI.ui_key_bindings import KeyBindingsManager

class TestCameraController(unittest.TestCase):
    """Tests orbital camera controller presets, dispatch table, and clamping behavior."""

    def setUp(self) -> None:
        KeyBindingsManager._instance = None
        self.cam = CameraController(pr.Vector3(0.0, 0.0, 0.0), 20.0)

    def test_dispatch_table_presets(self) -> None:
        """Verify that preset dispatch table maps keys correctly and handles fallbacks."""
        # Check known keys
        self.assertIn(pr.KeyboardKey.KEY_ONE, self.cam._preset_keys)
        self.assertIn(pr.KeyboardKey.KEY_TWO, self.cam._preset_keys)
        self.assertIn(pr.KeyboardKey.KEY_THREE, self.cam._preset_keys)
        self.assertIn(pr.KeyboardKey.KEY_FOUR, self.cam._preset_keys)

        # Execute preset top
        self.cam._preset_keys[pr.KeyboardKey.KEY_TWO]()
        self.assertAlmostEqual(self.cam.distance, 25.0)
        self.assertAlmostEqual(self.cam.yaw, 0.0)

        # Check unknown key fallback behavior
        handler = self.cam._preset_keys.get(pr.KeyboardKey.KEY_NINE, None)
        self.assertIsNone(handler)

    @patch('pyray.is_mouse_button_down', return_value=False)
    @patch('pyray.is_key_pressed')
    @patch('pyray.get_mouse_wheel_move')
    def test_zoom_clamping(self, mock_wheel, mock_key, mock_mouse) -> None:
        """Verify camera distance zooms and clamps between 2.0 and 150.0."""
        mock_key.return_value = False
        
        # Test zooming in beyond min distance (2.0)
        mock_wheel.return_value = 100.0
        self.cam.handle_input()
        self.assertAlmostEqual(self.cam.distance, 2.0)

        # Test zooming out beyond max distance (150.0)
        mock_wheel.return_value = -200.0
        self.cam.handle_input()
        self.assertAlmostEqual(self.cam.distance, 150.0)

    def test_pitch_clamping(self) -> None:
        """Verify camera pitch is clamped to +/- 89 degrees to prevent gimbal lock / flipping."""
        max_pitch = math.radians(89.0)

        # Test positive overflow
        self.cam.pitch = math.radians(120.0)
        self.cam.update_camera_vectors()
        self.assertAlmostEqual(self.cam.pitch, max_pitch)

        # Test negative overflow
        self.cam.pitch = -math.radians(120.0)
        self.cam.update_camera_vectors()
        self.assertAlmostEqual(self.cam.pitch, -max_pitch)

    @patch('pyray.is_mouse_button_down', return_value=False)
    @patch('pyray.get_mouse_wheel_move', return_value=0.0)
    @patch('pyray.get_frame_time', return_value=0.1)
    def test_keyboard_zoom(self, mock_dt, mock_wheel, mock_mouse) -> None:
        """Verify keyboard zoom actions modify camera distance."""
        mgr = KeyBindingsManager.get_instance()
        with patch.object(mgr, 'is_action_down', side_effect=lambda a: a == "zoom_in"):
            initial_dist = self.cam.distance
            self.cam.handle_input()
            self.assertLess(self.cam.distance, initial_dist)

    @patch('pyray.is_mouse_button_down', return_value=False)
    @patch('pyray.is_key_down', side_effect=lambda k: k == pr.KeyboardKey.KEY_LEFT_SHIFT)
    @patch('pyray.get_mouse_wheel_move', return_value=10.0)
    def test_zoom_ignored_when_shift_held(self, mock_wheel, mock_key, mock_mouse) -> None:
        """Verify mouse wheel zoom is disabled when holding Shift."""
        initial_dist = self.cam.distance
        self.cam.handle_input()
        self.assertAlmostEqual(self.cam.distance, initial_dist)

if __name__ == '__main__':
    unittest.main()
