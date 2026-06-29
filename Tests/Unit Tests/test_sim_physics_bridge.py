import unittest
import pyray as pr
from Simulation.sim_shapes import PhysicsShape
from Simulation.sim_physics_bridge import PhysicsEngineBridge


class TestPhysicsEngineBridge(unittest.TestCase):
    """Tests the bridge module connecting simulation entities with the OOP physics engine."""

    def setUp(self):
        self.shape1 = PhysicsShape(
            shape_id="s1",
            shape_type="sphere",
            pos=pr.Vector3(0.0, 10.0, 0.0),
            vel=pr.Vector3(0.0, 0.0, 0.0),
            size=pr.Vector3(2.0, 2.0, 2.0),
            radius=1.0,
            color=pr.Color(255, 0, 0, 255),
            mass=2.0,
            restitution=0.8
        )

    def test_step_scene_advances_position(self):
        """Verifies that step_scene advances falling objects under gravitational acceleration."""
        dt = 0.1
        gravity = -9.81
        initial_y = self.shape1.pos.y

        PhysicsEngineBridge.step_scene([self.shape1], dt, gravity)

        # Under gravity, velocity becomes negative and position decreases
        self.assertLess(self.shape1.vel.y, 0.0)
        self.assertLess(self.shape1.pos.y, initial_y)

    def test_step_scene_empty_or_zero_dt(self):
        """Verifies that passing empty list or dt=0 does not modify objects or crash."""
        events = PhysicsEngineBridge.step_scene([], 0.1, -9.81)
        self.assertEqual(len(events), 0)

        initial_y = self.shape1.pos.y
        PhysicsEngineBridge.step_scene([self.shape1], 0.0, -9.81)
        self.assertAlmostEqual(self.shape1.pos.y, initial_y, places=5)


if __name__ == "__main__":
    unittest.main()
