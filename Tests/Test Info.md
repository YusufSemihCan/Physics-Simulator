# Physics Simulator — Automated Test Suite

This directory contains the automated unit and stability test suite for the **Physics Simulator**. All tests are designed to run headlessly using `pyray` (Raylib Python bindings) and Python's standard `unittest` framework.

---

## 🚀 Running the Tests

To run the entire test suite from the root directory:
```powershell
# Windows PowerShell
Get-ChildItem "Tests\Unit Tests\test_*.py" | ForEach-Object { python -m unittest $_.FullName }
```
```bash
# Linux / macOS (or headless CI with xvfb)
python -m unittest discover -s "Tests" -p "test_*.py"
```

---

## 🧪 Test Suite Overview

| Test File | Primary Focus | Test Count | Key Components Tested |
| :--- | :--- | :---: | :--- |
| [`test_key_bindings.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_key_bindings.py) | Key Bindings & Remapping | 5 | `KeyBindingsManager`, Action queries, Remapping |
| [`test_render_camera.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_render_camera.py) | Orbital Camera Controller | 5 | `CameraController`, Presets dispatch table, Clamping, Shift zoom |
| [`test_render_window.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_render_window.py) | Simulation Renderer Dispatch | 6 | `SimulationRenderer`, Keyboard shortcuts dispatch table, Shift camera/shape height adjustment, Dropdown interaction locking |
| [`test_rendering_effects.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_rendering_effects.py) | VFX & Particle Systems | 2 | `TrailRenderer`, `ParticleSystem` |
| [`test_sim_circuits.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_circuits.py) | DC Circuit Nodal Solver | 2 | `CircuitScene`, `CircuitSolver` |
| [`test_sim_controller.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_controller.py) | Simulation Loop & Time Travel | 4 | `SimulationController`, Time-step buffer |
| [`test_sim_fields.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_fields.py) | EM Vector Field Calculation | 1 | `FieldScene`, `FieldCalculator` |
| [`test_sim_optics.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_optics.py) | Ray Tracing & Reflection | 2 | `OpticsScene`, `OpticsSolver` |
| [`test_sim_shapes.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_shapes.py) | Physics Data Structures | 4 | `PhysicsShape`, Energy calculations |
| [`test_sim_physics_bridge.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_physics_bridge.py) | OOP Physics Engine Bridge | 2 | `PhysicsEngineBridge`, `World`, `Body`, `verlet` |
| [`test_stability.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_stability.py) | Stress Testing & Crash Prevention | 3 | Overlapping collisions, NaN/Inf guards |
| [`test_ui_elements.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_elements.py) | Interactive UI Widgets | 3 | `Slider`, `Toggle`, `NodeSelector` |
| [`test_ui_graph.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_graph.py) | Real-time Telemetry Plotter | 3 | `GraphRenderer`, Ring buffer clamping |
| [`test_ui_load_scenario.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_load_scenario.py) | Scenario I/O & File Tree | 4 | `ScenarioManager`, `LoadScenarioScreen` |
| [`test_ui_menu.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_menu.py) | Main Menu & Modal Selection | 1 | `MainMenuScreen`, Simulation mode selection modal |
| [`test_ui_settings.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_settings.py) | Settings Screen Options | 1 | `SettingsScreen`, Resolution & Mode match branches |
| [`test_ui_workspace.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_workspace.py) | Inspector Panel & Picking | 6 | `WorkspaceUI`, Mode dispatch, Sliders |

---

## 📖 Detailed Test Explanations

### 1. Rendering & VFX ([`test_rendering_effects.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_rendering_effects.py))
Verifies visual feedback systems to ensure smooth rendering without memory leaks.
* `test_trail_renderer_add_and_clear`: Ensures object trajectory histories properly record positions, enforce maximum deque lengths (`max_points`), and clear successfully on reset.
* `test_particle_system_emit`: Validates collision spark generation, verifying burst counts and particle initial lifetimes.

### 2. DC Circuits Simulation ([`test_sim_circuits.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_circuits.py))
Tests the iterative nodal relaxation solver for electrical circuits.
* `test_default_circuit_current`: Builds a standard 9V battery loop with a switch and bulb, verifying that computed Ohm's Law current matches expected values (~0.6A).
* `test_open_switch_zero_current`: Opens the circuit switch and ensures current drops immediately to $0.0\text{ A}$.

### 3. Simulation Controller ([`test_sim_controller.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_controller.py))
Validates application flow, shape spawning, and time-travel rewind mechanics.
* `test_spawn_shape_at`: Verifies correct instantiation of rigid bodies with accurate initial positions, velocities, and dimensions.
* `test_playback_state_transitions`: Confirms cycle state transitions between `STOPPED`, `PLAYING`, and `PAUSED`.
* `test_physics_step_and_floor_bounce`: Executes integration steps to confirm gravity acceleration and restitution bounce velocity inversion.
* `test_rewind_history_buffer`: Steps simulation forward and executes a state rewind, verifying exact position restoration from historical frames.

### 4. Electromagnetic Fields ([`test_sim_fields.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_fields.py))
Tests vector field strength calculations from charged point sources.
* `test_electric_dipole_field`: Places $+1\text{C}$ and $-1\text{C}$ charges along an axis and verifies that the resulting electric field vector at the exact midpoint aligns correctly along the positive X-axis.

### 5. Ray Optics ([`test_sim_optics.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_optics.py))
Validates geometric ray propagation and reflection equations.
* `test_mirror_reflection_angle`: Traces a laser ray striking a $90^\circ$ vertical mirror, verifying accurate reflection vectors heading back along the negative X-axis.
* `test_default_scene_tracing`: Ensures scene presets generate multi-ray propagation paths without intersection failures.

### 6. Physics Shape Interface ([`test_sim_shapes.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_shapes.py))
Tests core math and serialization methods on the `PhysicsShape` dataclass.
* `test_speed_and_kinetic_energy`: Verifies 3D speed magnitude and $KE = \frac{1}{2}mv^2$ calculation accuracy.
* `test_potential_and_total_energy`: Validates gravitational potential energy ($PE = mgh$) and mechanical energy conservation totals.
* `test_json_serialization`: Ensures full round-trip conversion between Python objects and JSON dictionaries without precision loss.
* `test_clone_independence`: Verifies deep-copy cloning so modifications to duplicate shapes do not mutate original objects.

### 7. Numerical Stability & Edge Cases ([`test_stability.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_stability.py))
Guards against simulation explosions, floating-point overflows, and invalid input.
* `test_overlapping_spheres_stability`: Spawns 10 identical overlapping spheres and runs 60 simulation frames, ensuring collision separation algorithms prevent `NaN` or `Inf` coordinates.
* `test_cube_collisions_stability`: Spawns multiple overlapping cubes and verifies zero state corruption.
* `test_graph_renderer_sanitization`: Injects `NaN` coordinates into telemetry graphers to confirm sanitization fallbacks prevent crash exceptions.

### 8. UI Widgets ([`test_ui_elements.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_elements.py))
Tests standalone user interface input components.
* `test_slider_initialization_and_clamping`: Confirms initial slider values and tests boundary clamping when assigned out-of-range floats.
* `test_toggle_state`: Validates boolean state flipping upon user interactions.
* `test_node_selector_bounds`: Confirms indexed cycling through dropdown/carousel option lists.

### 9. Live Telemetry Graphing ([`test_ui_graph.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_graph.py))
Tests real-time energy and altitude chart renderers.
* `test_add_sample_and_ring_buffer_clamping`: Feeds 350 continuous samples into a 300-point ring buffer, confirming automatic discarding of oldest frames without memory bloat.
* `test_clear_buffers`: Verifies complete chart erasure when clearing workspace data.
* `test_non_kinematics_shape_sampling_safety`: **(Bug Fix)** Verifies that sampling or drawing graph telemetry when a non-kinematics object (such as a circuit switch or lens) is selected gracefully aborts without throwing an `AttributeError`.

### 10. Scenario Management & I/O ([`test_ui_load_scenario.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_load_scenario.py))
Tests local filesystem operations for saving, loading, and organizing project files.
* `test_main_menu_buttons_and_navigation`: Verifies button label configurations on main menu modals.
* `test_load_scenario_screen_initialization_and_selection`: Tests file tree list population and selection retrieval.
* `test_scenario_folder_management`: Validates folder creation (`.folder` markers), drag-and-drop scenario moving across directories, and recursive folder deletions.
* `test_scenario_renaming`: Verifies safe file renaming across disk storage.

### 11. Workspace Inspector & Selection ([`test_ui_workspace.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_workspace.py))
Tests multi-domain object selection and the property workbench inspector panel.
* `test_workspace_ui_initialization_and_visibility`: Verifies initial panel layout positions and visibility flags.
* `test_is_over_ui_collision_detection`: Confirms UI bounding box collision checks differentiate between menu clicks and 3D viewport clicks.
* `test_optics_picking_and_removal`: Tests ray-casting pick threshold accuracy on optical lenses/emitters and verifies removal from scene lists.
* `test_fields_picking_and_removal`: Validates picking and removing charge sources on 2D/3D grids.
* `test_circuits_picking`: Verifies midpoint picking bounding areas for circuit wires and resistors.
* `test_inspector_kinematics_dispatch`: Confirms dynamic routing of rigid bodies into the Inspector workbench, verifying live synchronization of Mass and Restitution slider values alongside real-time Kinetic, Potential, and Total Energy readouts.
* `test_inspector_circuits_switch_toggle`: **(New Feature)** Validates selection of circuit switch components and confirms interactive toggle state label generation (`CLOSED` / `OPEN`).

### 12. Orbital Camera Controller ([`test_render_camera.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_render_camera.py))
Tests orbital camera transformations, preset view positioning, and zoom/pitch boundary clamping.
* `test_camera_controller_initialization`: Verifies initial target position, distance, and yaw/pitch orientation.
* `test_preset_dispatch_table`: Tests camera preset view changes (`front`, `top`, `side`, `iso`) executed via dictionary dispatch table.
* `test_zoom_and_pitch_clamping`: Validates boundary enforcement ensuring camera distance stays within `[2.0, 150.0]` and pitch within `[-89.0, 89.0]` degrees.
* `test_keyboard_zoom`: Verifies keyboard zoom actions modify camera distance.
* `test_zoom_ignored_when_shift_held`: Verifies scroll wheel zoom is disabled when holding Shift to allow interactive height adjustments.
* **Key Details & Mocks**: Headless testing requires mocking `pyray` calls if viewport operations are performed.

### 13. Simulation Renderer Input Dispatch ([`test_render_window.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_render_window.py))
Tests global keyboard shortcut handling mapped through dictionary dispatch tables and mouse interaction modifiers.
* `test_key_actions_dispatch_table`: Confirms all registered hotkeys (`P`, `SPACE`, `S`, `G`, `V`, `T`, `F11`, `B`, `R`) exist in `_key_actions`, verifies correct execution (e.g. grid toggling, resolution cycling), and confirms safe `None` fallback for unregistered keys.
* `test_shift_mouse_wheel_height`: Verifies holding Shift and scrolling mouse wheel adjusts spawn height when in placement mode.
* `test_shift_mouse_wheel_camera_height`: Verifies holding Shift and scrolling mouse wheel adjusts camera target Y in 3D mode when no object is selected.
* `test_shift_mouse_wheel_selected_shape_height`: Verifies holding Shift and scrolling mouse wheel adjusts the Y position of a selected shape and resets vertical velocity.
* `test_build_screen_render_map`: Verifies lazy initialization and content structure of the screen rendering dispatch map (`_screen_render_map`).
* `test_dropdown_interaction_locking`: Verifies that hovering over open dropdown menus locks interactions (`UIState.block_interactions`) for underlying UI elements like buttons and sliders.
* **Key Details & Mocks**: Must patch `pyray.init_window`, `pyray.set_target_fps`, `pyray.set_window_size`, and `pyray.toggle_borderless_windowed` to prevent OpenGL window creation during initialization. Ensure `current_screen` is set to `SIMULATION` when testing viewport input.

### 14. Main Menu & Modal Selection ([`test_ui_menu.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_menu.py))
Tests main menu screen state transitions and simulation mode selection modals.
* `test_modal_navigation_and_selection`: Verifies opening the simulation selection modal and clicking simulation mode buttons (`Kinematics 3D`, `Optics Lab`, etc.) via list-based dispatch table properly sets simulation mode and navigates to the workspace.
* **Key Details & Mocks**: Patches screen dimension queries and text measurements (`get_screen_width`, `measure_text`) along with button drawing methods.

### 15. Settings Screen Options ([`test_ui_settings.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_ui_settings.py))
Tests resolution cycling and display mode changes in the configuration screen.
* `test_resolution_and_mode_branches`: Verifies changing resolution index updates window dimensions, and tests `match/case` branches switching between `Windowed`, `Borderless Windowed`, and `True Fullscreen` modes.
* **Key Details & Mocks**: Mocks selector `update_and_draw` methods and patches all `pyray` window state toggles (`toggle_fullscreen`, `toggle_borderless_windowed`) to ensure pure unit test isolation.

### 16. Key Bindings & Remapping ([`test_key_bindings.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_key_bindings.py))
Tests dynamic control remapping and action lookup queries.
* `test_singleton_identity`: Verifies that `KeyBindingsManager.get_instance()` reliably maintains singleton state.
* `test_is_action_pressed` & `test_is_action_down`: Verifies action queries inspect assigned multi-key arrays accurately.
* `test_remap_action`: Confirms dynamic remapping updates primary key assignments for actions.
* **Key Details & Mocks**: Patches `pyray.is_key_pressed` and `pyray.is_key_down` to simulate keyboard input without an open window. Must reset `KeyBindingsManager._instance = None` in `setUp` for test independence.

### 17. OOP Physics Engine Bridge ([`test_sim_physics_bridge.py`](file:///e:/Project%20Repo/Physics-Simulator/Tests/Unit%20Tests/test_sim_physics_bridge.py))
Tests the integration bridge mapping visual simulation shapes to the collaborator-owned OOP physics backend (`World`, `Body`, `Gravity`, `verlet`).
* `test_step_scene_advances_position`: Verifies that stepping the bridge advances falling rigid bodies under numerical Verlet gravity integration.
* `test_step_scene_empty_or_zero_dt`: Verifies clean short-circuit edge handling when passing empty scenes or zero time deltas.
* **Key Details & Mocks**: Pure headless numerical testing verifying numpy array translation back and forth without pyray rendering dependencies.
