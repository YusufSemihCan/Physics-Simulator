import numpy as np

class Body:
    def __init__(self, mass, position, velocity = None):
        if mass <= 0:
            raise ValueError("Mass must be positive")

        self.mass = float(mass)
        self.position = np.array(position)
        self.velocity = (np.zeros_like(self.position)
                         if velocity is None else np.array(velocity))

        self.force = np.zeros_like(self.position)

    def apply_force(self, force):
        self.force += np.asarray(force, dtype=float)

    def clear_forces(self):
        self.force = np.zeros_like(self.position)

    def acceleration(self):
        return self.force / self.mass

    def __repr__(self):
        return f"Body(mass={self.mass}, position={self.position}, velocity={self.velocity})"