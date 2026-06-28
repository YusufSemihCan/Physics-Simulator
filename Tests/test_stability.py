import unittest
import pyray as pr
import math
from Simulation.sim_controller import SimulationController
from Graphics.UI.ui_graph import GraphRenderer

class DummyApp:
    pass

class TestPhysicsStability(unittest.TestCase):
    def setUp(self):
        self.sim = SimulationController()

    def test_overlapping_spheres_stability(self):
        """Verify that spawning multiple overlapping spheres at identical positions does not produce NaN or Inf."""
        pos = pr.Vector3(0.0, 5.0, 0.0)
        for _ in range(10):
            self.sim.spawn_shape_at("sphere", pos, radius=1.0)

        self.sim.toggle_play()
        for _ in range(60): # Simulate 1 second at 60 FPS
            self.sim.step(1.0 / 60.0, -9.81)

        for s in self.sim.scene.shapes:
            self.assertFalse(math.isnan(s.pos.x) or math.isinf(s.pos.x))
            self.assertFalse(math.isnan(s.pos.y) or math.isinf(s.pos.y))
            self.assertFalse(math.isnan(s.pos.z) or math.isinf(s.pos.z))
            self.assertFalse(math.isnan(s.vel.x) or math.isinf(s.vel.x))
            self.assertFalse(math.isnan(s.vel.y) or math.isinf(s.vel.y))
            self.assertFalse(math.isnan(s.vel.z) or math.isinf(s.vel.z))

    def test_cube_collisions_stability(self):
        """Verify that spawning overlapping cubes does not crash or corrupt state."""
        pos = pr.Vector3(2.0, 5.0, 2.0)
        for _ in range(5):
            self.sim.spawn_shape_at("cube", pos, radius=1.2)

        self.sim.toggle_play()
        for _ in range(30):
            self.sim.step(1.0 / 60.0, -9.81)

        for s in self.sim.scene.shapes:
            self.assertFalse(math.isnan(s.pos.y) or math.isinf(s.pos.y))

    def test_graph_renderer_sanitization(self):
        """Verify GraphRenderer handles zero / corrupted samples safely."""
        app = DummyApp()
        graph = GraphRenderer(app)
        shape = self.sim.spawn_shape_at("sphere", pr.Vector3(0.0, float('nan'), 0.0))
        graph.add_sample(shape, -9.81)
        self.assertEqual(graph.history_h[-1], 0.0)

if __name__ == "__main__":
    unittest.main()
