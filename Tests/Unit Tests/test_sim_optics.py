import unittest
import math
from Simulation.sim_optics import OpticsScene, OpticsSolver

class TestOpticsSimulation(unittest.TestCase):
    def test_mirror_reflection_angle(self):
        scene = OpticsScene()
        # Laser pointing right (+X) hits a vertical 90-deg mirror at x=0
        scene.add_emitter(-5.0, 0.0, angle_deg=0.0)
        scene.add_mirror(0.0, 0.0, angle_deg=90.0, length=4.0)

        rays = OpticsSolver.trace_rays(scene)
        self.assertEqual(len(rays), 2)
        # First ray goes from (-5, 0) to (0, 0)
        self.assertAlmostEqual(rays[0].x2, 0.0, places=2)
        self.assertAlmostEqual(rays[0].y2, 0.0, places=2)
        # Second ray reflects back to (-25, 0)
        self.assertLess(rays[1].x2, -10.0)
        self.assertAlmostEqual(rays[1].y2, 0.0, places=2)

    def test_default_scene_tracing(self):
        scene = OpticsScene()
        scene.create_default_scene()
        rays = OpticsSolver.trace_rays(scene)
        self.assertGreaterEqual(len(rays), 2)

if __name__ == "__main__":
    unittest.main()
