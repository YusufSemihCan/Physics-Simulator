import os
import json
import shutil
import pyray as pr
from typing import List, Optional, Union
from Simulation.sim_shapes import PhysicsShape
from Simulation.sim_controller import SimulationScene
from Simulation.sim_modes import SimulationMode
from Graphics.Rendering.render_colors import Colors

# Each domain stores scenarios in its own subdirectory to avoid cross-contamination
_MODE_DIRS = {
    SimulationMode.KINEMATICS_3D: "kinematics",
    SimulationMode.KINETIC_2D:    "kinematics",   # same format as 3D
    SimulationMode.CIRCUITS:      "circuits",
    SimulationMode.OPTICS:        "optics",
    SimulationMode.FIELDS:        "fields",
}

_BASE_DIR = "Simulation/scenarios"


class ScenarioManager:
    """Manages disk persistence, JSON serialization, and built-in preset simulation scenarios.

    Each simulation mode stores its scenarios in its own subdirectory under
    ``Simulation/scenarios/<mode>/``, preventing cross-domain file contamination.
    """

    def __init__(self, mode: Union[SimulationMode, str] = SimulationMode.KINEMATICS_3D, scenarios_dir: Optional[str] = None):
        is_custom_dir = False
        if isinstance(mode, str):
            self.scenarios_dir = mode
            self.mode = SimulationMode.KINEMATICS_3D
            is_custom_dir = True
        elif scenarios_dir is not None:
            self.scenarios_dir = scenarios_dir
            self.mode = mode
            is_custom_dir = True
        else:
            subfolder = _MODE_DIRS.get(mode, "kinematics")
            self.scenarios_dir = os.path.join(_BASE_DIR, subfolder)
            self.mode = mode

        if not is_custom_dir:
            self._migrate_legacy_files()
        self.ensure_presets()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _migrate_legacy_files(self) -> None:
        """Move any .json files sitting directly in the base directory into
        the kinematics subfolder (one-time migration from the old flat layout)."""
        if not os.path.exists(_BASE_DIR):
            return
        kinematics_dir = os.path.join(_BASE_DIR, "kinematics")
        os.makedirs(kinematics_dir, exist_ok=True)
        for entry in os.listdir(_BASE_DIR):
            full = os.path.join(_BASE_DIR, entry)
            if os.path.isfile(full) and entry.endswith(".json"):
                dest = os.path.join(kinematics_dir, entry)
                if not os.path.exists(dest):
                    shutil.move(full, dest)
                    print(f"[~] Migrated legacy scenario: {entry} -> kinematics/")

    def ensure_presets(self) -> None:
        """Creates the mode's scenarios directory and generates built-in presets if empty."""
        os.makedirs(self.scenarios_dir, exist_ok=True)
        files = [f for f in os.listdir(self.scenarios_dir) if f.endswith(".json")]
        if files:
            return

        match self.mode:
            case SimulationMode.KINEMATICS_3D | SimulationMode.KINETIC_2D:
                self._create_kinematics_presets()
            case SimulationMode.CIRCUITS:
                self._create_circuits_preset()
            case SimulationMode.OPTICS:
                self._create_optics_preset()
            case SimulationMode.FIELDS:
                self._create_fields_preset()

    def _create_kinematics_presets(self) -> None:
        s1 = SimulationScene("Single Sphere", "A demonstration bouncing sphere under normal gravity.")
        s1.shapes.append(PhysicsShape("ball_1", "sphere", pr.Vector3(0.0, 8.0, 0.0), pr.Vector3(3.0, 0.0, 2.0), pr.Vector3(2.0, 2.0, 2.0), 1.0, Colors.SHAPE_ACCENT, 2.0, 0.82))
        self.save_scenario("Single Sphere", s1)

        s2 = SimulationScene("Double Cascade", "Two spheres falling from staggered elevations.")
        s2.shapes.append(PhysicsShape("s_high", "sphere", pr.Vector3(-3.0, 11.0, 0.0), pr.Vector3(1.5, 0.0, 0.0), pr.Vector3(1.6, 1.6, 1.6), 0.8, pr.Color(86, 182, 194, 255), 1.6, 0.85))
        s2.shapes.append(PhysicsShape("s_low",  "sphere", pr.Vector3(3.0, 6.0, 0.0),  pr.Vector3(-1.5, 0.0, 0.0), pr.Vector3(2.4, 2.4, 2.4), 1.2, pr.Color(198, 120, 221, 255), 2.4, 0.75))
        self.save_scenario("Double Cascade", s2)

        s3 = SimulationScene("Cube & Sphere", "Mixed geometry rigid bodies interact.")
        s3.shapes.append(PhysicsShape("cube_1",   "cube",   pr.Vector3(0.0, 9.0, -2.0), pr.Vector3(0.0, 0.0, 1.5), pr.Vector3(2.0, 2.0, 2.0), 1.0, pr.Color(229, 115, 115, 255), 2.0, 0.7))
        s3.shapes.append(PhysicsShape("sphere_1", "sphere", pr.Vector3(0.0, 5.0, 2.0),  pr.Vector3(0.0, 0.0, -1.5), pr.Vector3(2.0, 2.0, 2.0), 1.0, Colors.SHAPE_ACCENT, 2.0, 0.8))
        self.save_scenario("Cube & Sphere", s3)

    def _create_circuits_preset(self) -> None:
        """Placeholder — circuit scenes are generated procedurally; no JSON preset needed."""
        pass

    def _create_optics_preset(self) -> None:
        """Placeholder — optics scenes are generated procedurally; no JSON preset needed."""
        pass

    def _create_fields_preset(self) -> None:
        """Placeholder — field scenes are generated procedurally; no JSON preset needed."""
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_scenarios(self) -> List[str]:
        if not os.path.exists(self.scenarios_dir):
            return []
        items: List[str] = []

        def _walk(current_rel: str) -> None:
            current_abs = os.path.join(self.scenarios_dir, current_rel) if current_rel else self.scenarios_dir
            if not os.path.exists(current_abs):
                return
            try:
                entries = os.listdir(current_abs)
            except OSError:
                return
            dirs  = sorted(e for e in entries if os.path.isdir(os.path.join(current_abs, e)))
            files = sorted(e[:-5] for e in entries if os.path.isfile(os.path.join(current_abs, e)) and e.endswith(".json"))
            for d in dirs:
                rel_d = (os.path.join(current_rel, d) if current_rel else d).replace("\\", "/")
                items.append(rel_d)
                _walk(rel_d)
            for f in files:
                rel_f = (os.path.join(current_rel, f) if current_rel else f).replace("\\", "/")
                items.append(rel_f)

        _walk("")
        return items

    def create_folder(self, folder_path: str) -> bool:
        full_path = os.path.join(self.scenarios_dir, folder_path)
        try:
            os.makedirs(full_path, exist_ok=True)
            with open(os.path.join(full_path, ".folder"), "w", encoding="utf-8") as f:
                f.write("directory marker")
            print(f"[+] Folder created: {full_path}")
            return True
        except Exception as e:
            print(f"[!] Error creating folder: {e}")
            return False

    def save_scenario(self, name: str, scene: SimulationScene) -> None:
        filepath = os.path.join(self.scenarios_dir, f"{name}.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        scene.name = name
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(scene.to_dict(), f, indent=4)
        print(f"[+] Scenario saved: {filepath}")

    def load_scenario(self, name: str) -> Optional[SimulationScene]:
        filepath = os.path.join(self.scenarios_dir, f"{name}.json")
        if not os.path.exists(filepath):
            print(f"[!] Scenario not found: {filepath}")
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SimulationScene.from_dict(data)

    def move_scenario(self, src_name: str, dest_folder: str) -> bool:
        """Moves a scenario file or folder into dest_folder (or root if dest_folder is empty)."""
        src_dir  = os.path.join(self.scenarios_dir, src_name)
        src_file = os.path.join(self.scenarios_dir, f"{src_name}.json")
        target_dir = os.path.join(self.scenarios_dir, dest_folder) if dest_folder else self.scenarios_dir
        os.makedirs(target_dir, exist_ok=True)
        try:
            if os.path.isdir(src_dir):
                dest_path = os.path.join(target_dir, os.path.basename(src_name))
                if os.path.normpath(src_dir) != os.path.normpath(dest_path):
                    shutil.move(src_dir, dest_path)
                    print(f"[+] Moved folder {src_dir} -> {dest_path}")
                return True
            elif os.path.exists(src_file):
                dest_path = os.path.join(target_dir, os.path.basename(src_name) + ".json")
                if os.path.normpath(src_file) != os.path.normpath(dest_path):
                    shutil.move(src_file, dest_path)
                    print(f"[+] Moved scenario {src_file} -> {dest_path}")
                return True
        except Exception as e:
            print(f"[!] Error moving scenario: {e}")
        return False

    def delete_scenario(self, name: str) -> bool:
        dirpath  = os.path.join(self.scenarios_dir, name)
        filepath = os.path.join(self.scenarios_dir, f"{name}.json")
        if os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
            print(f"[-] Folder deleted: {dirpath}")
            self.ensure_presets()
            return True
        elif os.path.exists(filepath):
            os.remove(filepath)
            print(f"[-] Scenario deleted: {filepath}")
            self.ensure_presets()
            return True
        return False

    def rename_scenario(self, old_name: str, new_name: str) -> bool:
        """Renames a scenario file or folder from old_name to new_name."""
        old_dir  = os.path.join(self.scenarios_dir, old_name)
        old_file = os.path.join(self.scenarios_dir, f"{old_name}.json")
        new_dir  = os.path.join(self.scenarios_dir, new_name)
        new_file = os.path.join(self.scenarios_dir, f"{new_name}.json")
        try:
            if os.path.isdir(old_dir):
                if os.path.exists(new_dir) or os.path.exists(new_file):
                    print("[!] Cannot rename: destination already exists.")
                    return False
                os.makedirs(os.path.dirname(new_dir), exist_ok=True)
                shutil.move(old_dir, new_dir)
                print(f"[+] Renamed folder {old_dir} -> {new_dir}")
                return True
            elif os.path.exists(old_file):
                if os.path.exists(new_file) or os.path.exists(new_dir):
                    print("[!] Cannot rename: destination already exists.")
                    return False
                os.makedirs(os.path.dirname(new_file), exist_ok=True)
                shutil.move(old_file, new_file)
                try:
                    with open(new_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data["name"] = os.path.basename(new_name)
                    with open(new_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                except Exception as e:
                    print(f"[!] Warning: could not update internal name field: {e}")
                print(f"[+] Renamed scenario {old_file} -> {new_file}")
                return True
        except Exception as e:
            print(f"[!] Error renaming scenario: {e}")
        return False
