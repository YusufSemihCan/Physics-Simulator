import math
import uuid
from typing import List, Tuple

class FieldSource:
    __slots__ = ('source_id', 'source_type', 'x', 'y', 'val', 'angle_deg')

    def __init__(self, source_type: str, x: float, y: float, val: float = 1.0, angle_deg: float = 0.0):
        self.source_id = str(uuid.uuid4())[:8]
        self.source_type = source_type  # 'charge', 'magnet'
        self.x = x
        self.y = y
        self.val = val          # Charge (Coulombs) or Magnetic strength
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

    def pick_source(self, x: float, y: float, threshold: float = 0.8):
        for src in self.sources:
            if math.hypot(src.x - x, src.y - y) <= threshold:
                return src
        return None

    def create_default_scene(self):
        self.clear()
        # Electric dipole (+1 C at left, -1 C at right)
        self.add_charge(-3.0, 0.0, 1.0)
        self.add_charge(3.0, 0.0, -1.0)

class FieldCalculator:
    @staticmethod
    def calculate_vector_at(scene: 'FieldScene', gx: float, gy: float) -> Tuple[float, float, float]:
        """Returns (vx, vy, magnitude) of the summed field at coordinate (gx, gy)."""
        fx, fy = 0.0, 0.0
        for s in scene.sources:
            dx = gx - s.x
            dy = gy - s.y
            dist_sq = max(0.1, dx * dx + dy * dy)
            dist    = dist_sq ** 0.5
            inv_dist = 1.0 / dist  # compute once, reuse below

            if s.source_type == 'charge':
                # Coulomb field E = k * q / r^2 * r_hat
                mag = (8.99 * s.val) / dist_sq
                fx += mag * dx * inv_dist
                fy += mag * dy * inv_dist
            elif s.source_type == 'magnet':
                # Dipole approximation B ~ 3r̂(m·r̂) - m
                m_rad = math.radians(s.angle_deg)
                mx = math.cos(m_rad) * s.val * 5.0
                my = math.sin(m_rad) * s.val * 5.0
                dot = mx * dx + my * dy
                r5 = dist_sq * dist_sq * dist
                fx += (3.0 * dx * dot - mx * dist_sq) / r5
                fy += (3.0 * dy * dot - my * dist_sq) / r5

        return (fx, fy, math.hypot(fx, fy))
