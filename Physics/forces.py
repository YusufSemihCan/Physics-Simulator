import numpy as np

class Gravity:
    def __init__(self, g):
        self.g = np.array([0.0, -9.81]) if g is None else np.array(g, dtype=float)

    def apply_gravitational_force(self, world):
        for body in world.bodies:
            body.apply_force(body.mass * self.g)


class NewtonianGravity:
    """The universal law of gravitation is F = G * M * m / r^2
        The reason there is a softening, when the distance is very small
        between two bodies, the force goes to infinity,
        so the denominator never reaches zero"""
    def __init__(self, G=6.6743e-11, softening = 0.0):
        self.G = G
        self.softening = softening

    def apply_gravitational_force(self, world):
        bodies = world.bodies
        n = len(bodies)
        for i in range(n):
            for j in range(i+1, n):
                a, b = bodies[i], bodies[j]

                offset = b.position - a.position
                dist_sq = offset @ offset + self.softening**2
                distance = np.sqrt(dist_sq)
                direction = offset / distance

                magnitude = self.G * a.mass * b.mass / dist_sq
                force = magnitude * direction
                a.apply_force(force)
                b.apply_force(-force)