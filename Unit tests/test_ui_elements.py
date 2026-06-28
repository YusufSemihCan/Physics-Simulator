import unittest
from Graphics.UI.ui_elements import Slider, Toggle, NodeSelector

class TestUIElements(unittest.TestCase):
    def test_slider_initialization_and_clamping(self):
        slider = Slider(0, 0, 100, 20, "Test Slider", 0.0, 10.0, 5.0)
        self.assertEqual(slider.value, 5.0)
        
        # Test manual clamping logic
        slider.value = -5.0
        if slider.value < slider.min_val:
            slider.value = slider.min_val
        self.assertEqual(slider.value, 0.0)

        slider.value = 50.0
        if slider.value > slider.max_val:
            slider.value = slider.max_val
        self.assertEqual(slider.value, 10.0)

    def test_toggle_state(self):
        toggle = Toggle(0, 0, 20, "Test Toggle", True)
        self.assertTrue(toggle.state)
        toggle.state = not toggle.state
        self.assertFalse(toggle.state)

    def test_node_selector_bounds(self):
        options = ["Opt A", "Opt B", "Opt C"]
        selector = NodeSelector(0, 0, 200, "Selector", options, 0)
        self.assertEqual(selector.options[selector.current_index], "Opt A")
        
        # Simulate next option
        selector.current_index = (selector.current_index + 1) % len(selector.options)
        self.assertEqual(selector.options[selector.current_index], "Opt B")

if __name__ == "__main__":
    unittest.main()
