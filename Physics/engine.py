import pyray as pr
import math
from typing import List, Tuple, Any

def step_physics(shapes: List[Any], dt: float, gravity: float) -> List[Tuple[Any, float]]:
    """
    Temporary physics calculation engine to simulate kinematic motion, collisions,
    and environmental boundaries. Returns a list of (shape, impact_vy) tuples for shapes
    that experienced a significant floor bounce.
    """
    # Advance physics integration using high-precision Velocity Verlet
    for s in shapes:
        # Position update incorporating acceleration (0.5 * a * dt^2)
        s.pos.x += s.vel.x * dt
        s.pos.y += s.vel.y * dt + 0.5 * gravity * (dt ** 2)
        s.pos.z += s.vel.z * dt

        # Velocity update
        s.vel.y += gravity * dt

        # Subtle atmospheric drag damping to prevent perpetual drift
        drag = max(0.0, 1.0 - 0.05 * dt)
        s.vel.x *= drag
        s.vel.z *= drag

    # Inter-object collision detection and elastic impulse resolution (Spheres & Cubes)
    num_shapes = len(shapes)
    for i in range(num_shapes):
        s1 = shapes[i]
        for j in range(i + 1, num_shapes):
            s2 = shapes[j]

            dx = s2.pos.x - s1.pos.x
            dy = s2.pos.y - s1.pos.y
            dz = s2.pos.z - s1.pos.z
            dist_sq = dx*dx + dy*dy + dz*dz
            min_dist = s1.radius + s2.radius

            if dist_sq < min_dist * min_dist:
                if dist_sq < 1e-12:
                    dist = 0.001
                    nx, ny, nz = 1.0, 0.1, 0.0
                else:
                    dist = dist_sq ** 0.5
                    nx = dx / dist
                    ny = dy / dist
                    nz = dz / dist

                # Position penetration correction (clamped per frame to prevent numeric explosion)
                overlap = min(min_dist - dist, 0.4)
                s1.pos.x -= nx * overlap * 0.5
                s1.pos.y -= ny * overlap * 0.5
                s1.pos.z -= nz * overlap * 0.5
                s2.pos.x += nx * overlap * 0.5
                s2.pos.y += ny * overlap * 0.5
                s2.pos.z += nz * overlap * 0.5

                # Elastic impulse exchange
                kx = s1.vel.x - s2.vel.x
                ky = s1.vel.y - s2.vel.y
                kz = s1.vel.z - s2.vel.z
                p = 2.0 * (nx * kx + ny * ky + nz * kz) / max(0.001, s1.mass + s2.mass)

                if p > 0:
                    rest = min(s1.restitution, s2.restitution)
                    impulse = p * (1.0 + rest) * 0.5
                    s1.vel.x -= impulse * s2.mass * nx
                    s1.vel.y -= impulse * s2.mass * ny
                    s1.vel.z -= impulse * s2.mass * nz
                    s2.vel.x += impulse * s1.mass * nx
                    s2.vel.y += impulse * s1.mass * ny
                    s2.vel.z += impulse * s1.mass * nz

    bounce_events = []

    # Environmental constraint enforcement & NaN/Inf protection
    for s in shapes:
        # NaN / Inf protection
        if any(math.isnan(val) or math.isinf(val) for val in (s.pos.x, s.pos.y, s.pos.z, s.vel.x, s.vel.y, s.vel.z)):
            s.pos = pr.Vector3(0.0, 5.0, 0.0)
            s.vel = pr.Vector3(0.0, 0.0, 0.0)

        # Floor collision response
        if s.pos.y < s.radius:
            s.pos.y = s.radius
            impact_vy = s.vel.y
            if abs(impact_vy) > 1.5:
                bounce_events.append((s, impact_vy))
            s.vel.y *= -s.restitution
            s.vel.x *= 0.95
            s.vel.z *= 0.95

            # Rest threshold to eliminate micro-jittering when settled
            if abs(s.vel.y) < 0.2:
                s.vel.y = 0.0

        # Bounding wall constraints (-14 to 14)
        for axis in ('x', 'z'):
            val = getattr(s.pos, axis)
            vel = getattr(s.vel, axis)
            if val > 14.0 or val < -14.0:
                setattr(s.pos, axis, max(-14.0, min(14.0, val)))
                setattr(s.vel, axis, -vel * 0.85)

    return bounce_events
