import unittest
import pyray as pr
from Simulation.sim_controller import SimulationController, SimulationScene
from Simulation.sim_shapes import PhysicsShape

class TestSimController(unittest.TestCase):
    def setUp(self):
        self.ctrl = SimulationController()

    def test_spawn_shape_at(self):
        pos = pr.Vector3(1.0, 5.0, -2.0)
        vel = pr.Vector3(0.0, -1.0, 0.0)
        shape = self.ctrl.spawn_shape_at("sphere", pos, vel=vel, radius=1.2)
        
        self.assertEqual(len(self.ctrl.scene.shapes), 1)
        self.assertEqual(shape.shape_type, "sphere")
        self.assertEqual(shape.pos.y, 5.0)
        self.assertEqual(shape.vel.y, -1.0)
        self.assertEqual(shape.radius, 1.2)

    def test_playback_state_transitions(self):
        self.assertEqual(self.ctrl.state, "STOPPED")
        self.ctrl.toggle_play()
        self.assertEqual(self.ctrl.state, "PLAYING")
        self.ctrl.toggle_play()
        self.assertEqual(self.ctrl.state, "PAUSED")
        self.ctrl.stop()
        self.assertEqual(self.ctrl.state, "STOPPED")

    def test_physics_step_and_floor_bounce(self):
        pos = pr.Vector3(0.0, 1.1, 0.0)
        vel = pr.Vector3(0.0, -5.0, 0.0)
        shape = self.ctrl.spawn_shape_at("sphere", pos, vel=vel, radius=1.0)
        shape.restitution = 0.8
        self.ctrl.state = "PLAYING"

        self.ctrl.step(0.1, -10.0)
        self.assertEqual(shape.pos.y, 1.0)
        self.assertGreater(shape.vel.y, 0.0)

    def test_rewind_history_buffer(self):
        pos = pr.Vector3(0.0, 10.0, 0.0)
        shape = self.ctrl.spawn_shape_at("sphere", pos)
        self.ctrl.state = "PLAYING"

        for _ in range(5):
            self.ctrl.step(0.1, -10.0)

        self.assertLess(shape.pos.y, 10.0)
        self.ctrl.rewind(steps=5)
        self.assertEqual(self.ctrl.state, "PAUSED")
        self.assertAlmostEqual(shape.pos.y, 10.0)

if __name__ == "__main__":
    unittest.main()
