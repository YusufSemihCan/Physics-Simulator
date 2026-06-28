import unittest
import pyray as pr
from Graphics.Rendering.render_particles import TrailRenderer, ParticleSystem

class TestRenderingEffects(unittest.TestCase):
    def test_trail_renderer_add_and_clear(self):
        trails = TrailRenderer(max_points=5)
        pos = pr.Vector3(1.0, 2.0, 3.0)
        
        for i in range(10):
            trails.add_point("shape_1", pr.Vector3(pos.x + i, pos.y, pos.z))
            
        self.assertIn("shape_1", trails.trails)
        self.assertEqual(len(trails.trails["shape_1"]), 5)  # Clamped to max_points
        
        trails.clear()
        self.assertEqual(len(trails.trails), 0)

    def test_particle_system_emit(self):
        ps = ParticleSystem()
        pos = pr.Vector3(0.0, 0.0, 0.0)
        ps.emit_burst(pos, count=20)
        
        self.assertEqual(len(ps.particles), 20)
        for p in ps.particles:
            self.assertGreater(p.lifetime, 0.0)

if __name__ == "__main__":
    unittest.main()
