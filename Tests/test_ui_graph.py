import unittest
import pyray as pr
from Graphics.UI.ui_graph import GraphRenderer
from Simulation.sim_shapes import PhysicsShape

class MockApp:
    pass

class TestUIGraph(unittest.TestCase):
    def setUp(self):
        self.app = MockApp()
        self.graph = GraphRenderer(self.app)
        self.shape = PhysicsShape("g_ball", "sphere", pr.Vector3(0, 10, 0), pr.Vector3(0, -2, 0), pr.Vector3(2, 2, 2), 1.0, pr.Color(255, 255, 255, 255), 1.0)

    def test_add_sample_and_ring_buffer_clamping(self):
        self.assertEqual(len(self.graph.history_h), 0)
        
        # Add 350 samples (exceeds max_points = 300)
        for i in range(350):
            self.shape.pos.y = float(i)
            self.graph.add_sample(self.shape, -9.81)

        # Verify ring buffer clamped to exactly 300 samples
        self.assertEqual(len(self.graph.history_h), 300)
        self.assertEqual(len(self.graph.history_ke), 300)
        self.assertEqual(self.graph.history_h[-1], 349.0)

    def test_clear_buffers(self):
        self.graph.add_sample(self.shape, -9.81)
        self.assertEqual(len(self.graph.history_h), 1)
        self.graph.clear()
        self.assertEqual(len(self.graph.history_h), 0)

if __name__ == "__main__":
    unittest.main()
