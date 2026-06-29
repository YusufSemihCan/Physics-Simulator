import numpy as np

from Physics.body import Body


class World:
    """ Advances time one step at a time by dt. Basically the simulator."""

    def __init__(self, integrator):
        self.bodies = []
        self.forces = []
        self.integrator = integrator
        self.time = 0.0

    def add_body(self, body):
        self.bodies.append(body)
        return body

    def add_force(self, force):
        self.forces.append(force)
        return force

    def step(self, dt):
        if getattr(self.integrator, "world_level", False):
            self.integrator(self, dt)
        else:
            self.compute_forces()
            for body in self.bodies:
                self.integrator(body, dt, self)
            self.time += dt

    def compute_forces(self):
        for body in self.bodies:
            body.clear_force()
        for force in self.forces:
            force.apply_force(self)

    def __repr__(self):
        return f"World(bodies={self.bodies}, forces={self.forces}, time={self.time})"