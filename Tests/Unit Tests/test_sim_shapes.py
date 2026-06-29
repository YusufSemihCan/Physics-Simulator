import unittest
import pyray as pr
from Simulation.sim_shapes import PhysicsShape

class TestSimShapes(unittest.TestCase):
    def setUp(self):
        self.shape = PhysicsShape(
            shape_id="test_ball",
            shape_type="sphere",
            pos=pr.Vector3(0.0, 10.0, 0.0),
            vel=pr.Vector3(3.0, 4.0, 0.0),
            size=pr.Vector3(2.0, 2.0, 2.0),
            radius=1.0,
            color=pr.Color(255, 0, 0, 255),
            mass=2.0,
            restitution=0.8
        )

    def test_speed_and_kinetic_energy(self):
        # speed = sqrt(3^2 + 4^2 + 0^2) = 5.0
        self.assertAlmostEqual(self.shape.speed, 5.0)
        # KE = 0.5 * mass * speed^2 = 0.5 * 2.0 * 25 = 25.0 J
        self.assertAlmostEqual(self.shape.kinetic_energy(), 25.0)

    def test_potential_and_total_energy(self):
        # PE = mass * |gravity| * height = 2.0 * 9.81 * 10.0 = 196.2 J
        self.assertAlmostEqual(self.shape.potential_energy(-9.81), 196.2)
        # Total = KE + PE = 25.0 + 196.2 = 221.2 J
        self.assertAlmostEqual(self.shape.total_energy(-9.81), 221.2)

    def test_json_serialization(self):
        data = self.shape.to_dict()
        self.assertEqual(data["shape_id"], "test_ball")
        self.assertEqual(data["pos"], [0.0, 10.0, 0.0])
        self.assertEqual(data["color"], [255, 0, 0, 255])

        restored = PhysicsShape.from_dict(data)
        self.assertEqual(restored.shape_id, self.shape.shape_id)
        self.assertEqual(restored.pos.y, 10.0)
        self.assertEqual(restored.mass, 2.0)

    def test_clone_independence(self):
        clone = self.shape.clone()
        clone.pos.y = 999.0
        clone.vel.x = -50.0
        self.assertEqual(self.shape.pos.y, 10.0)
        self.assertEqual(self.shape.vel.x, 3.0)

if __name__ == "__main__":
    unittest.main()
