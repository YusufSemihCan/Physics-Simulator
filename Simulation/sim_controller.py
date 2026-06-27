import pyray as pr
import random
import uuid
from typing import Dict, List, Any, Optional
from Simulation.sim_shapes import PhysicsShape
from Graphics.Rendering.render_colors import Colors

class SimulationScene:
    """Stores configuration and entity collection for a named simulation scenario."""
    def __init__(self, name: str = "Default Scenario", description: str = ""):
        self.name = name
        self.description = description
        self.shapes: List[PhysicsShape] = []

    def clone(self) -> 'SimulationScene':
        copy_scene = SimulationScene(self.name, self.description)
        copy_scene.shapes = [s.clone() for s in self.shapes]
        return copy_scene

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "shapes": [s.to_dict() for s in self.shapes]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationScene':
        scene = cls(data.get("name", "Untitled"), data.get("description", ""))
        scene.shapes = [PhysicsShape.from_dict(s) for s in data.get("shapes", [])]
        return scene


class SimulationController:
    """Manages active simulation execution, time-travel frame rewinding, and shape spawning."""
    def __init__(self):
        self.scene = SimulationScene("Live Workspace")
        self.initial_scene = self.scene.clone()
        self.state = "STOPPED" # 'PLAYING', 'PAUSED', 'STOPPED'
        self.history: List[Dict[str, tuple]] = []
        self.max_history = 600 # 10 seconds of time-travel snapshots at 60fps

    def load_scene(self, scene: SimulationScene) -> None:
        self.scene = scene.clone()
        self.initial_scene = scene.clone()
        self.history.clear()
        self.state = "STOPPED"

    def toggle_play(self) -> None:
        if self.state == "PLAYING":
            self.state = "PAUSED"
        else:
            if self.state == "STOPPED":
                self.initial_scene = self.scene.clone()
            self.state = "PLAYING"

    def stop(self) -> None:
        self.state = "STOPPED"
        self.scene = self.initial_scene.clone()
        self.history.clear()

    def rewind(self, steps: int = 60) -> None:
        """Reverses time by popping historical state snapshots."""
        self.state = "PAUSED"
        for _ in range(steps):
            if not self.history:
                break
            snapshot = self.history.pop()
            for s in self.scene.shapes:
                if s.shape_id in snapshot:
                    pos_data, vel_data = snapshot[s.shape_id]
                    s.pos = pr.Vector3(pos_data[0], pos_data[1], pos_data[2])
                    s.vel = pr.Vector3(vel_data[0], vel_data[1], vel_data[2])

    def spawn_shape(self, shape_type: str, pos: Optional[pr.Vector3] = None) -> PhysicsShape:
        """Spawns a dynamic sphere or cube into the active workspace."""
        if pos is None:
            pos = pr.Vector3(random.uniform(-4.0, 4.0), random.uniform(6.0, 12.0), random.uniform(-4.0, 4.0))
        
        vel = pr.Vector3(random.uniform(-2.0, 2.0), 0.0, random.uniform(-2.0, 2.0))
        
        palette = [
            Colors.SHAPE_ACCENT,
            Colors.VECTOR_VELOCITY,
            Colors.VECTOR_ACCEL,
            pr.Color(229, 115, 115, 255),
            pr.Color(129, 199, 132, 255),
            pr.Color(100, 181, 246, 255),
            pr.Color(255, 183, 77, 255)
        ]
        color = random.choice(palette)
        
        radius = random.uniform(0.6, 1.4)
        size = pr.Vector3(radius * 2, radius * 2, radius * 2)
        
        shape = PhysicsShape(
            shape_id=str(uuid.uuid4())[:8],
            shape_type=shape_type,
            pos=pos,
            vel=vel,
            size=size,
            radius=radius,
            color=color,
            mass=radius * 2.0,
            restitution=0.78
        )
        
        self.scene.shapes.append(shape)
        if self.state == "STOPPED":
            self.initial_scene = self.scene.clone()
        return shape

    def spawn_shape_at(self, shape_type: str, pos: pr.Vector3, vel: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0), radius: float = 1.0) -> PhysicsShape:
        """Spawns a dynamic sphere or cube at a specific exact 3D coordinate."""
        palette = [
            Colors.SHAPE_ACCENT,
            Colors.VECTOR_VELOCITY,
            Colors.VECTOR_ACCEL,
            pr.Color(229, 115, 115, 255),
            pr.Color(129, 199, 132, 255),
            pr.Color(100, 181, 246, 255),
            pr.Color(255, 183, 77, 255)
        ]
        color = random.choice(palette)
        size = pr.Vector3(radius * 2, radius * 2, radius * 2)

        shape = PhysicsShape(
            shape_id=str(uuid.uuid4())[:8],
            shape_type=shape_type,
            pos=pr.Vector3(pos.x, pos.y, pos.z),
            vel=pr.Vector3(vel.x, vel.y, vel.z),
            size=size,
            radius=radius,
            color=color,
            mass=radius * 2.0,
            restitution=0.78
        )
        self.scene.shapes.append(shape)
        if self.state == "STOPPED":
            self.initial_scene = self.scene.clone()
        return shape

    def clear_shapes(self) -> None:
        self.scene.shapes.clear()
        self.initial_scene.shapes.clear()
        self.history.clear()

    def step(self, dt: float, gravity: float, particle_system=None, trail_renderer=None) -> None:
        if self.state != "PLAYING":
            return

        # Record snapshot for rewind buffer
        snapshot = {}
        for s in self.scene.shapes:
            snapshot[s.shape_id] = ((s.pos.x, s.pos.y, s.pos.z), (s.vel.x, s.vel.y, s.vel.z))
        self.history.append(snapshot)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        # Advance physics integration
        for s in self.scene.shapes:
            s.vel.y += gravity * dt
            s.pos.x += s.vel.x * dt
            s.pos.y += s.vel.y * dt
            s.pos.z += s.vel.z * dt

            # Floor collision response
            if s.pos.y < s.radius:
                s.pos.y = s.radius
                if abs(s.vel.y) > 1.5 and particle_system:
                    spark_pos = pr.Vector3(s.pos.x, 0.0, s.pos.z)
                    spark_vel = pr.Vector3(s.vel.x * 0.4, abs(s.vel.y) * 0.5, s.vel.z * 0.4)
                    particle_system.emit_burst(spark_pos, count=14, base_vel=spark_vel)
                s.vel.y *= -s.restitution
                s.vel.x *= 0.95
                s.vel.z *= 0.95

            # Bounding wall constraints (-14 to 14)
            for axis in ('x', 'z'):
                val = getattr(s.pos, axis)
                vel = getattr(s.vel, axis)
                if val > 14.0 or val < -14.0:
                    setattr(s.pos, axis, max(-14.0, min(14.0, val)))
                    setattr(s.vel, axis, -vel * 0.85)

            if trail_renderer:
                trail_renderer.add_point(s.shape_id, s.pos)
