import unittest
import pyray as pr
from unittest.mock import MagicMock, patch
from Graphics.UI.ui_workspace import WorkspaceUI
from Simulation.sim_modes import SimulationMode
from Simulation.sim_optics import OpticsScene
from Simulation.sim_fields import FieldScene
from Simulation.sim_circuits import CircuitScene

class TestWorkspaceUIAndMultiMode(unittest.TestCase):
    def setUp(self):
        # Create a mock application instance simulating SimulationRenderer
        self.mock_app = MagicMock()
        self.mock_app.sim_mode = SimulationMode.KINEMATICS_3D
        self.mock_app.placement_mode = None
        self.mock_app.selected_shape = None
        
        # Scenes
        self.optics_scene = OpticsScene("Test Optics")
        self.fields_scene = FieldScene("Test Fields")
        self.circuit_scene = CircuitScene("Test Circuits")
        
        self.mock_app.optics_scene = self.optics_scene
        self.mock_app.fields_scene = self.fields_scene
        self.mock_app.circuit_scene = self.circuit_scene

    def test_workspace_ui_initialization_and_visibility(self):
        ui = WorkspaceUI(self.mock_app)
        self.assertTrue(ui.show_top_bar)
        self.assertTrue(ui.show_bottom_bar)
        self.assertTrue(ui.show_sidebar)
        self.assertEqual(ui.sidebar_position, 'left')
        self.assertIsNone(ui.active_dropdown)

    def test_is_over_ui_collision_detection(self):
        ui = WorkspaceUI(self.mock_app)
        
        # Test Top Bar (y < 40)
        self.assertTrue(ui.is_over_ui(pr.Vector2(500, 20)))
        
        # Test Sidebar (left side x < 250)
        self.assertTrue(ui.is_over_ui(pr.Vector2(100, 300)))
        
        # Test Open Canvas area (center of 1280x720 screen)
        self.assertFalse(ui.is_over_ui(pr.Vector2(600, 300)))
        
        # Test hiding sidebar makes canvas spot clickable
        ui.show_sidebar = False
        self.assertFalse(ui.is_over_ui(pr.Vector2(100, 300)))

    def test_optics_picking_and_removal(self):
        em = self.optics_scene.add_emitter(-5.0, 2.0, 0.0)
        mir = self.optics_scene.add_mirror(2.0, 2.0, 45.0, 3.0)
        
        # Pick element near (-5.0, 2.0)
        picked = self.optics_scene.pick_element(-4.9, 2.1)
        self.assertEqual(picked, em)
        
        # Pick element near (2.0, 2.0)
        picked_mir = self.optics_scene.pick_element(2.05, 1.95)
        self.assertEqual(picked_mir, mir)
        
        # Remove element
        self.optics_scene.emitters.remove(em)
        self.assertIsNone(self.optics_scene.pick_element(-5.0, 2.0))

    def test_fields_picking_and_removal(self):
        ch = self.fields_scene.add_charge(3.0, -1.0, 1.0)
        mag = self.fields_scene.add_magnet(-3.0, -1.0, 2.0, 0.0)
        
        picked = self.fields_scene.pick_source(3.1, -0.9)
        self.assertEqual(picked, ch)
        
        picked_mag = self.fields_scene.pick_source(-3.0, -1.1)
        self.assertEqual(picked_mag, mag)
        
        self.fields_scene.sources.remove(ch)
        self.assertIsNone(self.fields_scene.pick_source(3.0, -1.0))

    def test_circuits_picking(self):
        n1 = self.circuit_scene.add_node(0.0, 0.0)
        n2 = self.circuit_scene.add_node(4.0, 0.0)
        res = self.circuit_scene.add_component('resistor', n1, n2, 10.0)
        
        # Midpoint is at (2.0, 0.0)
        picked = self.circuit_scene.pick_component(2.1, 0.1)
        self.assertEqual(picked, res)
        
        self.assertIsNone(self.circuit_scene.pick_component(10.0, 10.0))

    @patch('Graphics.UI.ui_elements.Slider.update_and_draw', lambda self: self.value)
    @patch('Graphics.UI.ui_elements.Button.update_and_draw', lambda self, *args: False)
    @patch('pyray.draw_text')
    def test_inspector_kinematics_dispatch(self, *args):
        ui = WorkspaceUI(self.mock_app)
        shape = MagicMock()
        shape.mass = 5.0
        shape.restitution = 0.8
        shape.pos = pr.Vector3(1.0, 2.0, 0.0)
        shape.speed = 10.0
        self.mock_app.selected_shape = shape
        self.mock_app.sim_mode = SimulationMode.KINEMATICS_3D
        
        ui._draw_inspector(10, 10)
        self.assertEqual(ui.slider_prop1.value, 5.0)
        self.assertEqual(ui.slider_prop2.value, 0.8)

    @patch('Graphics.UI.ui_elements.Slider.update_and_draw', lambda self: self.value)
    @patch('Graphics.UI.ui_elements.Button.update_and_draw', lambda self, *args: False)
    @patch('pyray.draw_text')
    def test_inspector_circuits_switch_toggle(self, *args):
        ui = WorkspaceUI(self.mock_app)
        n1 = self.circuit_scene.add_node(0, 0)
        n2 = self.circuit_scene.add_node(1, 1)
        switch = self.circuit_scene.add_component('switch', n1, n2, 1.0)
        switch.state = True # Closed
        self.mock_app.selected_shape = switch
        self.mock_app.sim_mode = SimulationMode.CIRCUITS
        
        ui._draw_inspector(10, 10)
        self.assertIn("CLOSED", ui.btn_toggle_state.text)

    def test_circuits_removal_cleanup(self):
        ui = WorkspaceUI(self.mock_app)
        n1 = self.circuit_scene.add_node(0, 0)
        n2 = self.circuit_scene.add_node(2, 2)
        res = self.circuit_scene.add_component('resistor', n1, n2, 10.0)
        n1.fixed_voltage = True
        n1.voltage = 9.0
        self.mock_app.selected_shape = res
        ui._remove_selected_object(SimulationMode.CIRCUITS, res)
        self.assertNotIn(res, self.circuit_scene.components)
        self.assertEqual(len(self.circuit_scene.nodes), 0) # Orphaned nodes cleaned up
        self.assertIsNone(self.mock_app.selected_shape)

    @patch('Graphics.UI.ui_elements.Slider.update_and_draw', lambda self: self.value)
    @patch('Graphics.UI.ui_elements.Button.update_and_draw', lambda self, *args: False)
    @patch('pyray.draw_text')
    def test_inspector_optics(self, *args):
        ui = WorkspaceUI(self.mock_app)
        lens = self.optics_scene.add_lens(0.0, 0.0, 5.0, 4.0)
        self.mock_app.selected_shape = lens
        self.mock_app.sim_mode = SimulationMode.OPTICS
        ui._draw_inspector(10, 10)
        self.assertEqual(lens.param1, 5.0)

    def test_picker_inactive_scene_safeguard(self):
        # When in FIELDS mode, optics_scene is None. Verify match/case dispatch avoids AttributeError.
        self.mock_app.sim_mode = SimulationMode.FIELDS
        self.mock_app.optics_scene = None
        ch = self.fields_scene.add_charge(0.0, 0.0, 1.0)
        picked = None
        match self.mock_app.sim_mode:
            case SimulationMode.OPTICS:
                if self.mock_app.optics_scene:
                    picked = self.mock_app.optics_scene.pick_element(0.0, 0.0)
            case SimulationMode.FIELDS:
                if self.mock_app.fields_scene:
                    picked = self.mock_app.fields_scene.pick_source(0.0, 0.0)
        self.assertEqual(picked, ch)

    @patch('pyray.draw_rectangle_rounded')
    @patch('pyray.draw_rectangle_rounded_lines')
    @patch('pyray.measure_text', return_value=50)
    @patch('pyray.draw_text')
    def test_uistate_interaction_blocking(self, *args):
        from Graphics.UI.ui_elements import Button, UIState
        btn = Button(0, 0, 100, 30, "Test")
        UIState.block_interactions = True
        with patch('pyray.get_mouse_position', return_value=pr.Vector2(50, 15)):
            with patch('pyray.check_collision_point_rec', return_value=True):
                with patch('pyray.is_mouse_button_pressed', return_value=True):
                    self.assertFalse(btn.update_and_draw())
        UIState.block_interactions = False

if __name__ == '__main__':
    unittest.main()
