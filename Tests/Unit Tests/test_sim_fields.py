import unittest
from Simulation.sim_fields import FieldScene, FieldCalculator

class TestFieldSimulation(unittest.TestCase):
    def test_electric_dipole_field(self):
        scene = FieldScene()
        scene.create_default_scene() # +1 at (-3, 0), -1 at (3, 0)
        
        # Midway between charges (0, 0), field from + charge points right (+X), field from - charge points right (+X)
        vx, vy, mag = FieldCalculator.calculate_vector_at(scene, 0.0, 0.0)
        self.assertGreater(vx, 0.0)
        self.assertAlmostEqual(vy, 0.0, places=2)

if __name__ == "__main__":
    unittest.main()
