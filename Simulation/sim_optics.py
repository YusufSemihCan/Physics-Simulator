import math
import uuid
from typing import List, Tuple, Optional

class OpticalElement:
    def __init__(self, elem_type: str, x: float, y: float, param1: float = 0.0, param2: float = 0.0):
        self.elem_id = str(uuid.uuid4())[:8]
        self.elem_type = elem_type # 'mirror', 'lens', 'prism'
        self.x = x
        self.y = y
        self.param1 = param1 # Angle or Width or Focal length
        self.param2 = param2 # Length or Height or Refractive index

class LaserEmitter:
    def __init__(self, x: float, y: float, angle_deg: float = 0.0):
        self.emitter_id = str(uuid.uuid4())[:8]
        self.x = x
        self.y = y
        self.angle_deg = angle_deg
        self.active = True

class RaySegment:
    def __init__(self, x1: float, y1: float, x2: float, y2: float, intensity: float = 1.0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.intensity = intensity

class OpticsScene:
    def __init__(self, name: str = "Optics & Lenses Lab"):
        self.name = name
        self.elements: List[OpticalElement] = []
        self.emitters: List[LaserEmitter] = []

    def add_mirror(self, x: float, y: float, angle_deg: float, length: float = 4.0) -> OpticalElement:
        elem = OpticalElement('mirror', x, y, angle_deg, length)
        self.elements.append(elem)
        return elem

    def add_lens(self, x: float, y: float, focal_length: float = 3.0, height: float = 4.0) -> OpticalElement:
        elem = OpticalElement('lens', x, y, focal_length, height)
        self.elements.append(elem)
        return elem

    def add_emitter(self, x: float, y: float, angle_deg: float = 0.0) -> LaserEmitter:
        em = LaserEmitter(x, y, angle_deg)
        self.emitters.append(em)
        return em

    def clear(self):
        self.elements.clear()
        self.emitters.clear()

    def pick_element(self, x: float, y: float, threshold: float = 0.8):
        for em in self.emitters:
            if math.hypot(em.x - x, em.y - y) <= threshold:
                return em
        for el in self.elements:
            if math.hypot(el.x - x, el.y - y) <= threshold:
                return el
        return None

    def create_default_scene(self):
        self.clear()
        # Horizontal laser from left hitting a 45-degree mirror pointing up, then a lens
        self.add_emitter(-8.0, 0.0, 0.0)               # Pointing right (+X)
        self.add_mirror(0.0, 0.0, 135.0, 3.0)          # 135 deg mirror deflects +X upward (+Y)
        self.add_lens(0.0, 5.0, focal_length=2.5, height=3.5) # Converging lens

class OpticsSolver:
    @staticmethod
    def _intersect_line(rx: float, ry: float, rdx: float, rdy: float, x1: float, y1: float, x2: float, y2: float) -> Optional[Tuple[float, float, float]]:
        # Ray: (rx, ry) + t*(rdx, rdy). Line seg: (x1, y1) to (x2, y2)
        dx = x2 - x1
        dy = y2 - y1
        det = rdx * dy - rdy * dx
        if abs(det) < 1e-6:
            return None
        t = ((x1 - rx) * dy - (y1 - ry) * dx) / det
        u = ((x1 - rx) * rdy - (y1 - ry) * rdx) / det
        if t > 0.001 and 0.0 <= u <= 1.0:
            ix = rx + t * rdx
            iy = ry + t * rdy
            return (t, ix, iy)
        return None

    @classmethod
    def trace_rays(cls, scene: OpticsScene, max_bounces: int = 8) -> List[RaySegment]:
        segments: List[RaySegment] = []
        for em in scene.emitters:
            if not em.active: continue
            curr_x, curr_y = em.x, em.y
            angle_rad = math.radians(em.angle_deg)
            rdx = math.cos(angle_rad)
            rdy = math.sin(angle_rad)
            intensity = 1.0

            for _ in range(max_bounces):
                closest_hit = None
                hit_elem = None
                min_t = 100.0

                for el in scene.elements:
                    if el.elem_type == 'mirror':
                        m_rad = math.radians(el.param1)
                        half_l = el.param2 / 2.0
                        mx = math.cos(m_rad) * half_l
                        my = math.sin(m_rad) * half_l
                        res = cls._intersect_line(curr_x, curr_y, rdx, rdy, el.x - mx, el.y - my, el.x + mx, el.y + my)
                        if res and res[0] < min_t:
                            min_t = res[0]
                            closest_hit = (res[1], res[2])
                            hit_elem = el
                    elif el.elem_type == 'lens':
                        # Thin vertical lens segment
                        half_h = el.param2 / 2.0
                        res = cls._intersect_line(curr_x, curr_y, rdx, rdy, el.x, el.y - half_h, el.x, el.y + half_h)
                        if res and res[0] < min_t:
                            min_t = res[0]
                            closest_hit = (res[1], res[2])
                            hit_elem = el

                if closest_hit and hit_elem:
                    hx, hy = closest_hit
                    segments.append(RaySegment(curr_x, curr_y, hx, hy, intensity))
                    curr_x, curr_y = hx, hy

                    if hit_elem.elem_type == 'mirror':
                        m_rad = math.radians(hit_elem.param1)
                        # Normal vector to mirror
                        nx = -math.sin(m_rad)
                        ny = math.cos(m_rad)
                        dot = rdx * nx + rdy * ny
                        rdx = rdx - 2 * dot * nx
                        rdy = rdy - 2 * dot * ny
                        intensity *= 0.92 # Subtle reflection loss
                    elif hit_elem.elem_type == 'lens':
                        f = hit_elem.param1
                        # Distance from optical axis (lens center y)
                        dy = hy - hit_elem.y
                        # Angular deflection theta_out = theta_in - dy / f
                        curr_angle = math.atan2(rdy, rdx)
                        new_angle = curr_angle - (dy / max(0.1, abs(f))) * (1.0 if f > 0 else -1.0)
                        rdx = math.cos(new_angle)
                        rdy = math.sin(new_angle)
                        intensity *= 0.95
                else:
                    # Ray escapes out to boundary (length 25)
                    segments.append(RaySegment(curr_x, curr_y, curr_x + rdx * 25.0, curr_y + rdy * 25.0, intensity))
                    break

        return segments
