import math
from typing import List, Tuple, Any
import numpy as np

from Physics.body import Body
from Physics.world import World
from Physics.forces import Gravity
from Physics.integrators import verlet


class BridgeGravityForce:
    """Wrapper adapting collaborator force classes to match World.compute_forces expectations."""
    def __init__(self, gravity_vec: List[float]):
        self._grav = Gravity(gravity_vec)

    def apply_force(self, world: World):
        if hasattr(self._grav, 'apply_force'):
            self._grav.apply_force(world)
        elif hasattr(self._grav, 'apply_gravitational_force'):
            self._grav.apply_gravitational_force(world)


class PhysicsEngineBridge:
    """Bridges simulation entities with the collaborator-authored OOP physics engine backend."""

    @staticmethod
    def step_scene(shapes: List[Any], dt: float, gravity: float) -> List[Tuple[Any, float]]:
        """Advances physics simulation using the OOP World/Verlet engine alongside boundary collision enforcement."""
        if not shapes or dt <= 0.0:
            return []

        world = World(integrator=verlet)
        grav_force = BridgeGravityForce([0.0, gravity, 0.0])
        world.add_force(grav_force)

        for s in shapes:
            body = Body(
                mass=getattr(s, 'mass', 1.0),
                position=[s.pos.x, s.pos.y, s.pos.z],
                velocity=[s.vel.x, s.vel.y, s.vel.z]
            )
            world.add_body(body)

        world.compute_forces()
        world.step(dt)

        for s, body in zip(shapes, world.bodies):
            s.pos.x = float(body.position[0])
            s.pos.y = float(body.position[1])
            s.pos.z = float(body.position[2])
            s.vel.x = float(body.velocity[0])
            s.vel.y = float(body.velocity[1])
            s.vel.z = float(body.velocity[2])

            # Apply subtle atmospheric drag damping matching existing behavior
            drag = max(0.0, 1.0 - 0.05 * dt)
            s.vel.x *= drag
            s.vel.z *= drag

        bounce_events = PhysicsEngineBridge._resolve_collisions_and_bounds(shapes)
        return bounce_events

    @staticmethod
    def _resolve_collisions_and_bounds(shapes: List[Any]) -> List[Tuple[Any, float]]:
        num_shapes = len(shapes)
        for i in range(num_shapes):
            s1 = shapes[i]
            for j in range(i + 1, num_shapes):
                s2 = shapes[j]
                dx = s2.pos.x - s1.pos.x
                dy = s2.pos.y - s1.pos.y
                dz = s2.pos.z - s1.pos.z
                dist_sq = dx*dx + dy*dy + dz*dz
                min_dist = getattr(s1, 'radius', 1.0) + getattr(s2, 'radius', 1.0)
                if dist_sq < min_dist * min_dist:
                    if dist_sq < 1e-12:
                        dist = 0.001
                        nx, ny, nz = 1.0, 0.1, 0.0
                    else:
                        dist = dist_sq ** 0.5
                        nx, ny, nz = dx / dist, dy / dist, dz / dist
                    overlap = min(min_dist - dist, 0.4)
                    s1.pos.x -= nx * overlap * 0.5
                    s1.pos.y -= ny * overlap * 0.5
                    s1.pos.z -= nz * overlap * 0.5
                    s2.pos.x += nx * overlap * 0.5
                    s2.pos.y += ny * overlap * 0.5
                    s2.pos.z += nz * overlap * 0.5
                    kx = s1.vel.x - s2.vel.x
                    ky = s1.vel.y - s2.vel.y
                    kz = s1.vel.z - s2.vel.z
                    p = 2.0 * (nx * kx + ny * ky + nz * kz) / max(0.001, getattr(s1, 'mass', 1.0) + getattr(s2, 'mass', 1.0))
                    if p > 0:
                        rest = min(getattr(s1, 'restitution', 0.8), getattr(s2, 'restitution', 0.8))
                        impulse = p * (1.0 + rest) * 0.5
                        m2 = getattr(s2, 'mass', 1.0)
                        m1 = getattr(s1, 'mass', 1.0)
                        s1.vel.x -= impulse * m2 * nx
                        s1.vel.y -= impulse * m2 * ny
                        s1.vel.z -= impulse * m2 * nz
                        s2.vel.x += impulse * m1 * nx
                        s2.vel.y += impulse * m1 * ny
                        s2.vel.z += impulse * m1 * nz

        bounce_events: List[Tuple[Any, float]] = []
        for s in shapes:
            if any(math.isnan(val) or math.isinf(val) for val in (s.pos.x, s.pos.y, s.pos.z, s.vel.x, s.vel.y, s.vel.z)):
                s.pos.x, s.pos.y, s.pos.z = 0.0, 5.0, 0.0
                s.vel.x, s.vel.y, s.vel.z = 0.0, 0.0, 0.0

            r = getattr(s, 'radius', 1.0)
            if s.pos.y < r:
                s.pos.y = r
                impact_vy = s.vel.y
                if abs(impact_vy) > 1.5:
                    bounce_events.append((s, impact_vy))
                s.vel.y *= -getattr(s, 'restitution', 0.8)
                s.vel.x *= 0.95
                s.vel.z *= 0.95
                if abs(s.vel.y) < 0.2:
                    s.vel.y = 0.0

            for axis in ('x', 'z'):
                val = getattr(s.pos, axis)
                vel = getattr(s.vel, axis)
                if val > 14.0 or val < -14.0:
                    setattr(s.pos, axis, max(-14.0, min(14.0, val)))
                    setattr(s.vel, axis, -vel * 0.85)
        return bounce_events

    @staticmethod
    def kinetic_energy(s: Any) -> float:
        """Computes kinetic energy using OOP Body representation."""
        body = Body(getattr(s, 'mass', 1.0), [s.pos.x, s.pos.y, s.pos.z], [s.vel.x, s.vel.y, s.vel.z])
        speed_sq = float(np.sum(body.velocity ** 2))
        return 0.5 * body.mass * speed_sq

    @staticmethod
    def potential_energy(s: Any, gravity: float = -9.81) -> float:
        """Computes gravitational potential energy using OOP Body representation."""
        body = Body(getattr(s, 'mass', 1.0), [s.pos.x, s.pos.y, s.pos.z], [s.vel.x, s.vel.y, s.vel.z])
        return body.mass * abs(gravity) * max(0.0, float(body.position[1]))

    @staticmethod
    def total_energy(s: Any, gravity: float = -9.81) -> float:
        """Computes total mechanical energy via OOP backend."""
        return PhysicsEngineBridge.kinetic_energy(s) + PhysicsEngineBridge.potential_energy(s, gravity)
