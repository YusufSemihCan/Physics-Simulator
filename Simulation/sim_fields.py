import math
import uuid
from typing import List, Tuple

class FieldSource:
    def __init__(self, source_type: str, x: float, y: float, val: float = 1.0, angle_deg: float = 0.0):
        self.source_id = str(uuid.uuid4())[:8]
        self.source_type = source_type # 'charge', 'magnet'
        self.x = x
        self.y = y
        self.val = val # Charge (Coulombs) or Magnetic strength
        self.angle_deg = angle_deg

class FieldScene:
    def __init__(self, name: str = "Electromagnetic Fields Lab"):
        self.name = name
        self.sources: List[FieldSource] = []

    def add_charge(self, x: float, y: float, charge: float = 1.0) -> FieldSource:
        src = FieldSource('charge', x, y, charge)
        self.sources.append(src)
        return src

    def add_magnet(self, x: float, y: float, strength: float = 2.0, angle_deg: float = 0.0) -> FieldSource:
        src = FieldSource('magnet', x, y, strength, angle_deg)
        self.sources.append(src)
        return src

    def clear(self):
        self.sources.clear()

    def create_default_scene(self):
        self.clear()
        # Electric dipole (+1 C at left, -1 C at right)
        self.add_charge(-3.0, 0.0, 1.0)
        self.add_charge(3.0, 0.0, -1.0)

class FieldCalculator:
    @staticmethod
    def calculate_vector_at(scene: FieldScene, gx: float, gy: float) -> Tuple[float, float, float]:
        """Returns (vx, vy, magnitude) of the field at coordinate (gx, gy)."""
        fx, fy = 0.0, 0.0
        for s in scene.sources:
            dx = gx - s.x
            dy = gy - s.y
            dist_sq = dx*dx + dy*dy
            if dist_sq < 0.1:
                dist_sq = 0.1
            dist = dist_sq ** 0.5

            if s.source_type == 'charge':
                # Coulomb field E = k * q / r^2 * r_hat
                mag = (8.99 * s.val) / dist_sq
                fx += mag * (dx / dist)
                fy += mag * (dy / dist)
            elif s.source_type == 'magnet':
                # Dipole approximation m = strength * (cos, sin)
                m_rad = math.radians(s.angle_deg)
                mx = math.cos(m_rad) * s.val * 5.0
                my = math.sin(m_rad) * s.val * 5.0
                dot = mx * dx + my * dy
                # B ~ 3 * r_hat * (m . r_hat) - m
                r5 = dist_sq * dist_sq * dist
                fx += (3.0 * dx * dot - mx * dist_sq) / r5
                fy += (3.0 * dy * dot - my * dist_sq) / r5

        mag = math.hypot(fx, fy)
        return (fx, fy, mag)
