# Physics Simulator — Automated Test Suite

This directory contains the automated unit and stability test suite for the **Physics Simulator**. All tests are designed to run headlessly using `pyray` (Raylib Python bindings) and Python's standard `unittest` framework.

---

## 🚀 Running the Tests

To run the entire test suite from the root directory:
```powershell
# Windows PowerShell
Get-ChildItem "Tests\test_*.py" | ForEach-Object { python -m unittest $_.FullName }
```
```bash
# Linux / macOS (or headless CI with xvfb)
python -m unittest discover -s "Tests" -p "test_*.py"
```

---

## 🧪 Test Suite Overview

| Test File | Primary Focus | Test Count | Key Components Tested |
| :--- | :--- | :---: | :--- |
| [`test_rendering_effects.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_rendering_effects.py) | VFX & Particle Systems | 2 | `TrailRenderer`, `ParticleSystem` |
| [`test_sim_circuits.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_sim_circuits.py) | DC Circuit Nodal Solver | 2 | `CircuitScene`, `CircuitSolver` |
| [`test_sim_controller.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_sim_controller.py) | Simulation Loop & Time Travel | 4 | `SimulationController`, Time-step buffer |
| [`test_sim_fields.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_sim_fields.py) | EM Vector Field Calculation | 1 | `FieldScene`, `FieldCalculator` |
| [`test_sim_optics.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_sim_optics.py) | Ray Tracing & Reflection | 2 | `OpticsScene`, `OpticsSolver` |
| [`test_sim_shapes.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_sim_shapes.py) | Physics Data Structures | 4 | `PhysicsShape`, Energy calculations |
| [`test_stability.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_stability.py) | Stress Testing & Crash Prevention | 3 | Overlapping collisions, NaN/Inf guards |
| [`test_ui_elements.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_ui_elements.py) | Interactive UI Widgets | 3 | `Slider`, `Toggle`, `NodeSelector` |
| [`test_ui_graph.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_ui_graph.py) | Real-time Telemetry Plotter | 3 | `GraphRenderer`, Ring buffer clamping |
| [`test_ui_load_scenario.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_ui_load_scenario.py) | Scenario I/O & File Tree | 4 | `ScenarioManager`, `LoadScenarioScreen` |
| [`test_ui_workspace.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_ui_workspace.py) | Inspector Panel & Picking | 6 | `WorkspaceUI`, Mode dispatch, Sliders |

---

## 📖 Detailed Test Explanations

### 1. Rendering & VFX ([`test_rendering_effects.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_rendering_effects.py))
Verifies visual feedback systems to ensure smooth rendering without memory leaks.
* `test_trail_renderer_add_and_clear`: Ensures object trajectory histories properly record positions, enforce maximum deque lengths (`max_points`), and clear successfully on reset.
* `test_particle_system_emit`: Validates collision spark generation, verifying burst counts and particle initial lifetimes.

### 2. DC Circuits Simulation ([`test_sim_circuits.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_sim_circuits.py))
Tests the iterative nodal relaxation solver for electrical circuits.
* `test_default_circuit_current`: Builds a standard 9V battery loop with a switch and bulb, verifying that computed Ohm's Law current matches expected values (~0.6A).
* `test_open_switch_zero_current`: Opens the circuit switch and ensures current drops immediately to $0.0\text{ A}$.

### 3. Simulation Controller ([`test_sim_controller.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_sim_controller.py))
Validates application flow, shape spawning, and time-travel rewind mechanics.
* `test_spawn_shape_at`: Verifies correct instantiation of rigid bodies with accurate initial positions, velocities, and dimensions.
* `test_playback_state_transitions`: Confirms cycle state transitions between `STOPPED`, `PLAYING`, and `PAUSED`.
* `test_physics_step_and_floor_bounce`: Executes integration steps to confirm gravity acceleration and restitution bounce velocity inversion.
* `test_rewind_history_buffer`: Steps simulation forward and executes a state rewind, verifying exact position restoration from historical frames.

### 4. Electromagnetic Fields ([`test_sim_fields.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_sim_fields.py))
Tests vector field strength calculations from charged point sources.
* `test_electric_dipole_field`: Places $+1\text{C}$ and $-1\text{C}$ charges along an axis and verifies that the resulting electric field vector at the exact midpoint aligns correctly along the positive X-axis.

### 5. Ray Optics ([`test_sim_optics.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_sim_optics.py))
Validates geometric ray propagation and reflection equations.
* `test_mirror_reflection_angle`: Traces a laser ray striking a $90^\circ$ vertical mirror, verifying accurate reflection vectors heading back along the negative X-axis.
* `test_default_scene_tracing`: Ensures scene presets generate multi-ray propagation paths without intersection failures.

### 6. Physics Shape Interface ([`test_sim_shapes.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_sim_shapes.py))
Tests core math and serialization methods on the `PhysicsShape` dataclass.
* `test_speed_and_kinetic_energy`: Verifies 3D speed magnitude and $KE = \frac{1}{2}mv^2$ calculation accuracy.
* `test_potential_and_total_energy`: Validates gravitational potential energy ($PE = mgh$) and mechanical energy conservation totals.
* `test_json_serialization`: Ensures full round-trip conversion between Python objects and JSON dictionaries without precision loss.
* `test_clone_independence`: Verifies deep-copy cloning so modifications to duplicate shapes do not mutate original objects.

### 7. Numerical Stability & Edge Cases ([`test_stability.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_stability.py))
Guards against simulation explosions, floating-point overflows, and invalid input.
* `test_overlapping_spheres_stability`: Spawns 10 identical overlapping spheres and runs 60 simulation frames, ensuring collision separation algorithms prevent `NaN` or `Inf` coordinates.
* `test_cube_collisions_stability`: Spawns multiple overlapping cubes and verifies zero state corruption.
* `test_graph_renderer_sanitization`: Injects `NaN` coordinates into telemetry graphers to confirm sanitization fallbacks prevent crash exceptions.

### 8. UI Widgets ([`test_ui_elements.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_ui_elements.py))
Tests standalone user interface input components.
* `test_slider_initialization_and_clamping`: Confirms initial slider values and tests boundary clamping when assigned out-of-range floats.
* `test_toggle_state`: Validates boolean state flipping upon user interactions.
* `test_node_selector_bounds`: Confirms indexed cycling through dropdown/carousel option lists.

### 9. Live Telemetry Graphing ([`test_ui_graph.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_ui_graph.py))
Tests real-time energy and altitude chart renderers.
* `test_add_sample_and_ring_buffer_clamping`: Feeds 350 continuous samples into a 300-point ring buffer, confirming automatic discarding of oldest frames without memory bloat.
* `test_clear_buffers`: Verifies complete chart erasure when clearing workspace data.
* `test_non_kinematics_shape_sampling_safety`: **(Bug Fix)** Verifies that sampling or drawing graph telemetry when a non-kinematics object (such as a circuit switch or lens) is selected gracefully aborts without throwing an `AttributeError`.

### 10. Scenario Management & I/O ([`test_ui_load_scenario.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_ui_load_scenario.py))
Tests local filesystem operations for saving, loading, and organizing project files.
* `test_main_menu_buttons_and_navigation`: Verifies button label configurations on main menu modals.
* `test_load_scenario_screen_initialization_and_selection`: Tests file tree list population and selection retrieval.
* `test_scenario_folder_management`: Validates folder creation (`.folder` markers), drag-and-drop scenario moving across directories, and recursive folder deletions.
* `test_scenario_renaming`: Verifies safe file renaming across disk storage.

### 11. Workspace Inspector & Selection ([`test_ui_workspace.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/test_ui_workspace.py))
Tests multi-domain object selection and the property workbench inspector panel.
* `test_workspace_ui_initialization_and_visibility`: Verifies initial panel layout positions and visibility flags.
* `test_is_over_ui_collision_detection`: Confirms UI bounding box collision checks differentiate between menu clicks and 3D viewport clicks.
* `test_optics_picking_and_removal`: Tests ray-casting pick threshold accuracy on optical lenses/emitters and verifies removal from scene lists.
* `test_fields_picking_and_removal`: Validates picking and removing charge sources on 2D/3D grids.
* `test_circuits_picking`: Verifies midpoint picking bounding areas for circuit wires and resistors.
* `test_inspector_kinematics_dispatch`: **(New Feature)** Confirms dynamic routing of rigid bodies into the Inspector workbench, verifying live synchronization of Mass and Restitution slider values.
* `test_inspector_circuits_switch_toggle`: **(New Feature)** Validates selection of circuit switch components and confirms interactive toggle state label generation (`CLOSED` / `OPEN`).
