import math
import pyray as pr
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class PhysicsShape:
    """Represents an interactive 3D rigid body entity within the simulation backend."""
    shape_id: str
    shape_type: str       # 'sphere' or 'cube'
    pos: pr.Vector3
    vel: pr.Vector3
    size: pr.Vector3      # Dimensions for cube (w, h, d)
    radius: float         # Radius for sphere or bounding radius
    color: pr.Color
    mass: float = 1.0
    restitution: float = 0.8

    @property
    def speed(self) -> float:
        return math.sqrt(self.vel.x**2 + self.vel.y**2 + self.vel.z**2)

    def kinetic_energy(self) -> float:
        return 0.5 * self.mass * (self.speed ** 2)

    def potential_energy(self, gravity: float = -9.81) -> float:
        return self.mass * abs(gravity) * max(0.0, self.pos.y)

    def total_energy(self, gravity: float = -9.81) -> float:
        return self.kinetic_energy() + self.potential_energy(gravity)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes entity parameters to JSON dictionary."""
        return {
            "shape_id": self.shape_id,
            "shape_type": self.shape_type,
            "pos": [self.pos.x, self.pos.y, self.pos.z],
            "vel": [self.vel.x, self.vel.y, self.vel.z],
            "size": [self.size.x, self.size.y, self.size.z],
            "radius": self.radius,
            "color": [self.color.r, self.color.g, self.color.b, self.color.a],
            "mass": self.mass,
            "restitution": self.restitution
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhysicsShape':
        """Deserializes JSON dictionary into a live PhysicsShape object."""
        c = data["color"]
        return cls(
            shape_id=data["shape_id"],
            shape_type=data["shape_type"],
            pos=pr.Vector3(data["pos"][0], data["pos"][1], data["pos"][2]),
            vel=pr.Vector3(data["vel"][0], data["vel"][1], data["vel"][2]),
            size=pr.Vector3(data["size"][0], data["size"][1], data["size"][2]),
            radius=float(data["radius"]),
            color=pr.Color(c[0], c[1], c[2], c[3]),
            mass=float(data.get("mass", 1.0)),
            restitution=float(data.get("restitution", 0.8))
        )

    def clone(self) -> 'PhysicsShape':
        """Creates a completely independent deep copy of this shape."""
        return PhysicsShape(
            shape_id=self.shape_id,
            shape_type=self.shape_type,
            pos=pr.Vector3(self.pos.x, self.pos.y, self.pos.z),
            vel=pr.Vector3(self.vel.x, self.vel.y, self.vel.z),
            size=pr.Vector3(self.size.x, self.size.y, self.size.z),
            radius=self.radius,
            color=pr.Color(self.color.r, self.color.g, self.color.b, self.color.a),
            mass=self.mass,
            restitution=self.restitution
        )
