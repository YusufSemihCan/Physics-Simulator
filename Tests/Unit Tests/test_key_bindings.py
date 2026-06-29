import unittest
from unittest.mock import patch
import pyray as pr
from Graphics.UI.ui_key_bindings import (
    KeyBindingsManager,
    ACTION_PLAY_PAUSE,
    ACTION_STOP,
    ACTION_ZOOM_IN,
)


class TestKeyBindingsManager(unittest.TestCase):
    """Tests unit behavior of KeyBindingsManager including singleton access, queries, and remapping."""

    def setUp(self) -> None:
        # Reset singleton instance before each test to guarantee test independence
        KeyBindingsManager._instance = None
        self.mgr = KeyBindingsManager.get_instance()

    def test_singleton_identity(self) -> None:
        """Verify get_instance always returns the same object instance."""
        second_instance = KeyBindingsManager.get_instance()
        self.assertIs(self.mgr, second_instance)

    @patch("pyray.is_key_pressed")
    def test_is_action_pressed(self, mock_is_pressed) -> None:
        """Verify action pressed query checks assigned keys accurately."""
        # Setup mock so KEY_P returns True, others False
        mock_is_pressed.side_effect = lambda key: key == pr.KeyboardKey.KEY_P
        self.assertTrue(self.mgr.is_action_pressed(ACTION_PLAY_PAUSE))
        self.assertFalse(self.mgr.is_action_pressed(ACTION_STOP))

    @patch("pyray.is_key_down")
    def test_is_action_down(self, mock_is_down) -> None:
        """Verify action down query checks assigned keys accurately."""
        mock_is_down.side_effect = lambda key: key == pr.KeyboardKey.KEY_EQUAL
        self.assertTrue(self.mgr.is_action_down(ACTION_ZOOM_IN))

    def test_remap_action(self) -> None:
        """Verify remapping updates primary key assigned to an action."""
        self.mgr.remap_action(ACTION_STOP, pr.KeyboardKey.KEY_X)
        keys = self.mgr.get_action_keys(ACTION_STOP)
        self.assertEqual(keys, [pr.KeyboardKey.KEY_X])

    def test_get_key_name(self) -> None:
        """Verify friendly names are generated for known key codes."""
        self.assertEqual(self.mgr.get_key_name(pr.KeyboardKey.KEY_SPACE), "SPACE")
        self.assertEqual(self.mgr.get_key_name(pr.KeyboardKey.KEY_A), "A")


if __name__ == "__main__":
    unittest.main()
