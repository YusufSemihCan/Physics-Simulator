import pyray as pr
import random
from collections import deque
from dataclasses import dataclass
from typing import Dict, List
from Graphics.Rendering.render_colors import Colors

@dataclass
class Particle:
    pos: pr.Vector3
    vel: pr.Vector3
    color: pr.Color
    size: float
    lifetime: float
    max_lifetime: float

class TrailRenderer:
    """Renders fading motion trajectories behind moving physics entities."""
    def __init__(self, max_points: int = 50):
        self.max_points = max_points
        # deque per entity avoids O(n) pop(0) on every frame
        self.trails: Dict[str, deque] = {}
        self.enabled = True

    def add_point(self, entity_id: str, pos: pr.Vector3) -> None:
        if not self.enabled:
            return
        if entity_id not in self.trails:
            self.trails[entity_id] = deque(maxlen=self.max_points)
        self.trails[entity_id].append(pr.Vector3(pos.x, pos.y, pos.z))

    def draw_3d(self) -> None:
        if not self.enabled:
            return
        for entity_id, pts in self.trails.items():
            n = len(pts)
            if n < 2:
                continue
            for i in range(n - 1):
                # Calculate fading alpha from oldest (0) to newest (255)
                alpha_ratio = (i + 1) / n
                alpha = int(255 * alpha_ratio)
                color = pr.Color(Colors.TRAIL_DEFAULT.r, Colors.TRAIL_DEFAULT.g, Colors.TRAIL_DEFAULT.b, alpha)
                pr.draw_line_3d(pts[i], pts[i+1], color)

    def clear(self) -> None:
        self.trails.clear()


class ParticleSystem:
    """Manages and renders GPU/CPU particle bursts for collisions and thrusters."""
    def __init__(self):
        self.particles: List[Particle] = []
        self.enabled = True

    def emit_burst(self, pos: pr.Vector3, count: int = 15, base_vel: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0), color: pr.Color = Colors.PARTICLE_SPARK) -> None:
        if not self.enabled:
            return
        for _ in range(count):
            # Generate random cone velocity burst
            vx = base_vel.x + random.uniform(-4.0, 4.0)
            vy = base_vel.y + random.uniform(2.0, 8.0)
            vz = base_vel.z + random.uniform(-4.0, 4.0)
            lifetime = random.uniform(0.3, 0.8)
            size = random.uniform(0.08, 0.18)
            
            p = Particle(
                pos=pr.Vector3(pos.x, pos.y, pos.z),
                vel=pr.Vector3(vx, vy, vz),
                color=pr.Color(color.r, color.g, color.b, 255),
                size=size,
                lifetime=lifetime,
                max_lifetime=lifetime
            )
            self.particles.append(p)

    def update_and_draw(self, dt: float) -> None:
        if not self.enabled:
            return
        next_particles: List[Particle] = []
        for p in self.particles:
            p.lifetime -= dt
            if p.lifetime <= 0:
                continue

            # Kinematic integration + floor bounce
            p.vel.y -= 9.81 * dt
            p.pos.x += p.vel.x * dt
            p.pos.y += p.vel.y * dt
            p.pos.z += p.vel.z * dt
            if p.pos.y < 0.0:
                p.pos.y = 0.0
                p.vel.y *= -0.5
                p.vel.x *= 0.8
                p.vel.z *= 0.8

            # Fade alpha and shrink size proportionally to remaining lifetime
            ratio = p.lifetime / p.max_lifetime
            alpha = int(255 * ratio)
            draw_color = pr.Color(p.color.r, p.color.g, p.color.b, alpha)
            pr.draw_cube(p.pos, p.size * ratio, p.size * ratio, p.size * ratio, draw_color)
            next_particles.append(p)

        self.particles = next_particles
