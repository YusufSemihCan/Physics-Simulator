import numpy as np

class Body:
    """
    Represents a physical rigid body (a circle/particle) in 2D space.
    Uses NumPy arrays for vector calculations.
    """
    def __init__(self, position, velocity, mass=1.0, radius=15.0, elasticity=0.8, is_static=False):
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.acceleration = np.array([0.0, 0.0], dtype=np.float64)
        self.force = np.array([0.0, 0.0], dtype=np.float64)
        self.mass = float(mass)
        self.inv_mass = 0.0 if is_static or mass <= 0 else 1.0 / mass
        self.radius = float(radius)
        self.elasticity = float(elasticity)
        self.is_static = bool(is_static)

    def apply_force(self, force):
        """Applies a continuous force to the body."""
        if not self.is_static:
            self.force += np.array(force, dtype=np.float64)

    def clear_forces(self):
        """Clears all accumulated forces."""
        self.force = np.array([0.0, 0.0], dtype=np.float64)


class PhysicsEngine:
    """
    Manages physical updates, integration, and collisions.
    Operates independently of any graphics pipeline.
    """
    def __init__(self, gravity=(0.0, 980.0), drag=0.01):
        self.bodies = []
        self.gravity = np.array(gravity, dtype=np.float64)
        self.drag = float(drag)

    def add_body(self, body):
        """Registers a body in the physical simulation."""
        self.bodies.append(body)

    def step(self, dt, width=800, height=600):
        """
        Advances the simulation by dt seconds.
        Performs integration, boundary checks, and collision resolution.
        """
        if dt <= 0:
            return

        # 1. Integration & Drag
        for body in self.bodies:
            if body.is_static:
                continue

            # Apply gravity as a force: F_g = m * g
            body.apply_force(body.mass * self.gravity)

            # Apply a simple velocity-dependent drag force
            drag_force = -self.drag * body.velocity
            body.apply_force(drag_force)

            # Acceleration = Force / Mass (F = m * a)
            body.acceleration = body.force * body.inv_mass

            # Update velocity: v = v + a * dt
            body.velocity += body.acceleration * dt

            # Update position: p = p + v * dt
            body.position += body.velocity * dt

            # Clear forces for next iteration
            body.clear_forces()

        # 2. Boundary Collision Resolution (Screen boundaries)
        for body in self.bodies:
            if body.is_static:
                continue

            # Left/Right bounds
            if body.position[0] - body.radius < 0:
                body.position[0] = body.radius
                body.velocity[0] = -body.velocity[0] * body.elasticity
            elif body.position[0] + body.radius > width:
                body.position[0] = width - body.radius
                body.velocity[0] = -body.velocity[0] * body.elasticity

            # Top/Bottom bounds
            if body.position[1] - body.radius < 0:
                body.position[1] = body.radius
                body.velocity[1] = -body.velocity[1] * body.elasticity
            elif body.position[1] + body.radius > height:
                body.position[1] = height - body.radius
                body.velocity[1] = -body.velocity[1] * body.elasticity

        # 3. Simple Body-on-Body Collision Resolution (Elastic Circles)
        self._resolve_collisions()

    def _resolve_collisions(self):
        """Resolves collisions between pairs of circular bodies."""
        num_bodies = len(self.bodies)
        for i in range(num_bodies):
            for j in range(i + 1, num_bodies):
                b1 = self.bodies[i]
                b2 = self.bodies[j]

                # Don't resolve collision between two static bodies
                if b1.is_static and b2.is_static:
                    continue

                # Vector from b1 to b2
                disp = b2.position - b1.position
                distance = np.linalg.norm(disp)
                min_distance = b1.radius + b2.radius

                if distance < min_distance and distance > 0:
                    # Normal vector of collision
                    normal = disp / distance

                    # 1. Penetration Resolution (Position correction to prevent sticking)
                    penetration = min_distance - distance
                    # Share correction based on inverse masses
                    total_inv_mass = b1.inv_mass + b2.inv_mass
                    if total_inv_mass > 0:
                        correction = (penetration / total_inv_mass) * normal * 0.8  # 80% positional correction
                        b1.position -= correction * b1.inv_mass
                        b2.position += correction * b2.inv_mass

                    # 2. Impulse Resolution (Velocity change)
                    # Relative velocity
                    rel_vel = b2.velocity - b1.velocity
                    # Relative velocity along normal
                    vel_along_normal = np.dot(rel_vel, normal)

                    # Do not resolve if velocities are separating
                    if vel_along_normal < 0:
                        # Coefficient of restitution (elasticity)
                        e = min(b1.elasticity, b2.elasticity)

                        # Calculate impulse scalar
                        impulse_scalar = -(1 + e) * vel_along_normal
                        impulse_scalar /= total_inv_mass

                        # Apply impulse to each body
                        b1.velocity -= impulse_scalar * b1.inv_mass * normal
                        b2.velocity += impulse_scalar * b2.inv_mass * normal
