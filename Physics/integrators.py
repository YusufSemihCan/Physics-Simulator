import numpy as np




def symplectic_euler(body, dt, world=None):
    """Advance body by dt using symplectic Euler integration.
        The three lines are for the whole integrator are
        a = F/m
        v += a * dt (update velocity first)
        x += v * dt (then move using the new velocity)
        The whole trick is updating velocity before position,
        and using just updated velocity for position update.
        This makes this method symplectic"""
    acceleration = body.force / body.mass
    body.velocity += acceleration * dt
    body.position += body.velocity * dt

def verlet(world, dt):
    old_accel = []
    for body in world.bodies:
        a = body.force / body.mass
        old_accel.append(a)
        body.position += body.velocity * dt + 0.5 * a * dt**2

    world.compute_forces()

    for body, a_old in zip(world.bodies, old_accel):
        a_new = body.force / body.mass
        body.velocity += 0.5 * (a_new + a_old) * dt

    world.time += dt

verlet.world_level = True

