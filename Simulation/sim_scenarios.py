import os
import json
import pyray as pr
from typing import List, Optional
from Simulation.sim_shapes import PhysicsShape
from Simulation.sim_controller import SimulationScene
from Graphics.Rendering.render_colors import Colors

class ScenarioManager:
    """Manages disk persistence, JSON serialization, and built-in preset simulation scenarios."""
    def __init__(self, scenarios_dir: str = "scenarios"):
        self.scenarios_dir = scenarios_dir
        self.ensure_presets()

    def ensure_presets(self) -> None:
        """Creates scenarios directory and generates built-in demonstration setups if empty."""
        os.makedirs(self.scenarios_dir, exist_ok=True)
        files = [f for f in os.listdir(self.scenarios_dir) if f.endswith(".json")]
        if files:
            return

        # Preset 1: Single Bouncing Sphere
        s1 = SimulationScene("Single Sphere", "A demonstration bouncing sphere under normal gravity.")
        s1.shapes.append(PhysicsShape("ball_1", "sphere", pr.Vector3(0.0, 8.0, 0.0), pr.Vector3(3.0, 0.0, 2.0), pr.Vector3(2.0, 2.0, 2.0), 1.0, Colors.SHAPE_ACCENT, 2.0, 0.82))
        self.save_scenario("Single Sphere", s1)

        # Preset 2: Double Cascade
        s2 = SimulationScene("Double Cascade", "Two spheres falling from staggered elevations.")
        s2.shapes.append(PhysicsShape("s_high", "sphere", pr.Vector3(-3.0, 11.0, 0.0), pr.Vector3(1.5, 0.0, 0.0), pr.Vector3(1.6, 1.6, 1.6), 0.8, pr.Color(86, 182, 194, 255), 1.6, 0.85))
        s2.shapes.append(PhysicsShape("s_low", "sphere", pr.Vector3(3.0, 6.0, 0.0), pr.Vector3(-1.5, 0.0, 0.0), pr.Vector3(2.4, 2.4, 2.4), 1.2, pr.Color(198, 120, 221, 255), 2.4, 0.75))
        self.save_scenario("Double Cascade", s2)

        # Preset 3: Cube & Sphere Collision
        s3 = SimulationScene("Cube & Sphere", "Mixed geometry rigid bodies interact.")
        s3.shapes.append(PhysicsShape("cube_1", "cube", pr.Vector3(0.0, 9.0, -2.0), pr.Vector3(0.0, 0.0, 1.5), pr.Vector3(2.0, 2.0, 2.0), 1.0, pr.Color(229, 115, 115, 255), 2.0, 0.7))
        s3.shapes.append(PhysicsShape("sphere_1", "sphere", pr.Vector3(0.0, 5.0, 2.0), pr.Vector3(0.0, 0.0, -1.5), pr.Vector3(2.0, 2.0, 2.0), 1.0, Colors.SHAPE_ACCENT, 2.0, 0.8))
        self.save_scenario("Cube & Sphere", s3)

    def list_scenarios(self) -> List[str]:
        if not os.path.exists(self.scenarios_dir):
            return []
        files = [f[:-5] for f in os.listdir(self.scenarios_dir) if f.endswith(".json")]
        return sorted(files)

    def save_scenario(self, name: str, scene: SimulationScene) -> None:
        os.makedirs(self.scenarios_dir, exist_ok=True)
        filepath = os.path.join(self.scenarios_dir, f"{name}.json")
        scene.name = name
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(scene.to_dict(), f, indent=4)
        print(f"[+] Scenario saved successfully: {filepath}")

    def load_scenario(self, name: str) -> Optional[SimulationScene]:
        filepath = os.path.join(self.scenarios_dir, f"{name}.json")
        if not os.path.exists(filepath):
            print(f"[!] Scenario not found: {filepath}")
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SimulationScene.from_dict(data)

    def delete_scenario(self, name: str) -> bool:
        filepath = os.path.join(self.scenarios_dir, f"{name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"[-] Scenario deleted: {filepath}")
            return True
        return False
