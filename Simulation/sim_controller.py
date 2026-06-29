import pyray as pr
import math
import random
import uuid
from collections import deque
from typing import Dict, List, Any, Optional
from Simulation.sim_shapes import PhysicsShape
from Simulation.sim_physics_bridge import PhysicsEngineBridge

# Colour palette shared by all spawned shapes — built once at import time
_SHAPE_PALETTE = [
    pr.Color(229, 192, 123, 255),
    pr.Color(86, 182, 194, 255),
    pr.Color(198, 120, 221, 255),
    pr.Color(229, 115, 115, 255),
    pr.Color(129, 199, 132, 255),
    pr.Color(100, 181, 246, 255),
    pr.Color(255, 183, 77, 255),
]

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
        self.state = "STOPPED"  # 'PLAYING', 'PAUSED', 'STOPPED'
        self.max_history = 600  # 10 seconds of time-travel snapshots at 60fps
        # deque with maxlen avoids O(n) pop(0) every frame when buffer is full
        self.history: deque[Dict[str, tuple]] = deque(maxlen=self.max_history)

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
        
        color = random.choice(_SHAPE_PALETTE)
        
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
        color = random.choice(_SHAPE_PALETTE)
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

        # Record snapshot for rewind buffer (deque maxlen handles overflow automatically)
        snapshot = {s.shape_id: ((s.pos.x, s.pos.y, s.pos.z), (s.vel.x, s.vel.y, s.vel.z))
                    for s in self.scene.shapes}
        self.history.append(snapshot)

        # Delegate physics computation to the OOP Physics backend bridge
        bounce_events = PhysicsEngineBridge.step_scene(self.scene.shapes, dt, gravity)

        # Handle UI rendering visual hooks (particles and trail rendering)
        if particle_system:
            for s, impact_vy in bounce_events:
                spark_pos = pr.Vector3(s.pos.x, 0.0, s.pos.z)
                spark_vel = pr.Vector3(s.vel.x * 0.4, abs(impact_vy) * 0.5, s.vel.z * 0.4)
                particle_system.emit_burst(spark_pos, count=14, base_vel=spark_vel)

        if trail_renderer:
            for s in self.scene.shapes:
                trail_renderer.add_point(s.shape_id, s.pos)
