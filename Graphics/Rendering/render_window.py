import pyray as pr
import math
from typing import Callable, Dict, Tuple
from Graphics.UI.ui_key_bindings import (
    KeyBindingsManager,
    ACTION_PLAY_PAUSE,
    ACTION_STOP,
    ACTION_TOGGLE_GRID,
    ACTION_TOGGLE_VECTORS,
    ACTION_TOGGLE_TRAILS,
    ACTION_BORDERLESS,
    ACTION_CYCLE_RES,
    ACTION_ZOOM_IN,
    ACTION_ZOOM_OUT,
    ACTION_PAN_UP,
    ACTION_PAN_DOWN,
    ACTION_PAN_LEFT,
    ACTION_PAN_RIGHT,
)
from Graphics.Rendering.render_colors import Colors
from Graphics.Rendering.render_grid import GridRenderer
from Graphics.Rendering.render_camera import CameraController
from Graphics.Rendering.render_particles import TrailRenderer, ParticleSystem
from Graphics.Rendering.render_vectors import VectorRenderer
from Graphics.UI.ui_axis_indicator import AxisIndicator
from Graphics.UI.ui_menu import AppScreen, MainMenuScreen
from Graphics.UI.ui_settings import SettingsScreen
from Graphics.UI.ui_load_scenario import LoadScenarioScreen
from Graphics.UI.ui_graph import GraphRenderer
from Simulation.sim_controller import SimulationController
from Simulation.sim_scenarios import ScenarioManager
from Simulation.sim_modes import SimulationMode
from Simulation.sim_circuits import CircuitScene
from Simulation.sim_optics import OpticsScene
from Simulation.sim_fields import FieldScene
from Graphics.Rendering.render_circuits import CircuitRenderer
from Graphics.Rendering.render_optics import OpticsRenderer
from Graphics.Rendering.render_fields import FieldsRenderer
from Graphics.UI.ui_workspace import WorkspaceUI

class SimulationRenderer:
    def __init__(self, width: int = 1280, height: int = 720, title: str = "Physics Simulator"):
        # Configure OpenGL window flags before initialization (resizable + MSAA 4X anti-aliasing)
        pr.set_config_flags(
            pr.ConfigFlags.FLAG_WINDOW_RESIZABLE | 
            pr.ConfigFlags.FLAG_MSAA_4X_HINT
        )
        pr.init_window(width, height, title)
        pr.set_exit_key(pr.KeyboardKey.KEY_NULL) # Disable automatic ESC close to allow menu navigation
        pr.set_target_fps(60)

        # Configure interactive orbital camera controller
        self.camera_ctrl = CameraController(pr.Vector3(0.0, 4.0, 0.0), 26.0)

        self.grid = GridRenderer(slices=30, spacing=1.0)
        self.mode_3d = True
        self.resolutions = [(1280, 720), (1600, 900), (1920, 1080), (2560, 1440)]
        self.res_index = 0

        # Advanced graphics feature modules
        self.trails = TrailRenderer(max_points=60)
        self.particles = ParticleSystem()
        self.vectors = VectorRenderer()
        self.axis_indicator = AxisIndicator()

        # Core Simulation Backend & Scenarios
        self.sim = SimulationController()
        self.scenarios = ScenarioManager()

        # Interactive Placement State
        self.placement_mode = None # 'sphere', 'cube', or None
        self.spawn_height = 5.0

        # Object Inspection & Real-Time Graphing
        self.selected_shape = None
        self.graph_renderer = GraphRenderer(self)

        # Navigation screen states
        self.current_screen = AppScreen.MAIN_MENU
        self.main_menu = MainMenuScreen()
        self.settings_screen = SettingsScreen(self)
        self.load_scenario_screen = LoadScenarioScreen(self)
        self.active_scenario_name = "Single Sphere"
        self.should_quit = False

        # Domain Modes & Scenes
        self.sim_mode = SimulationMode.KINEMATICS_3D
        self.circuit_scene = None
        self.optics_scene = None
        self.fields_scene = None

        self.circuit_renderer = None
        self.optics_renderer = None
        self.fields_renderer = None
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.zoom_2d = 1.0
        self.switch_mode(SimulationMode.KINEMATICS_3D)

        self.workspace_ui = WorkspaceUI(self)

        # Action dispatch map for keyboard shortcuts
        self._action_handlers: Dict[str, Callable[[], None]] = {
            ACTION_PLAY_PAUSE: lambda: self.sim.toggle_play(),
            ACTION_STOP: self._stop_sim,
            ACTION_TOGGLE_GRID: self._toggle_grid,
            ACTION_TOGGLE_VECTORS: lambda: setattr(self.vectors, 'enabled', not self.vectors.enabled),
            ACTION_TOGGLE_TRAILS: lambda: setattr(self.trails, 'enabled', not self.trails.enabled),
            ACTION_BORDERLESS: pr.toggle_borderless_windowed,
            ACTION_CYCLE_RES: self._cycle_resolution,
        }

        # 2D pan action direction accumulation map (action → (dx, dy))
        self._pan_actions: Dict[str, Tuple[float, float]] = {
            ACTION_PAN_UP:    (0.0,  1.0),
            ACTION_PAN_DOWN:  (0.0, -1.0),
            ACTION_PAN_LEFT:  (1.0,  0.0),
            ACTION_PAN_RIGHT: (-1.0,  0.0),
        }

        # 3D shape draw strategy: shape_type → (solid_fn, wire_fn)
        self._shape_draw_3d = {
            "sphere": (
                lambda s: pr.draw_sphere(s.pos, s.radius, s.color),
                lambda s: pr.draw_sphere_wires(s.pos, s.radius, 16, 16, Colors.AXIS_X),
            ),
            "cube": (
                lambda s: pr.draw_cube(s.pos, s.size.x, s.size.y, s.size.z, s.color),
                lambda s: pr.draw_cube_wires(s.pos, s.size.x, s.size.y, s.size.z, Colors.AXIS_X),
            ),
        }

        # 3D ray-pick collision strategy: shape_type → fn(ray, shape) → RayCollision
        self._ray_pick_3d = {
            "sphere": lambda ray, s: pr.get_ray_collision_sphere(ray, s.pos, s.radius),
            "cube":   lambda ray, s: pr.get_ray_collision_box(
                ray,
                pr.BoundingBox(
                    pr.Vector3(s.pos.x - s.size.x/2, s.pos.y - s.size.y/2, s.pos.z - s.size.z/2),
                    pr.Vector3(s.pos.x + s.size.x/2, s.pos.y + s.size.y/2, s.pos.z + s.size.z/2)
                )
            ),
        }

        # Screen-render dispatch map (built after screen objects exist)
        self._screen_render_map = None

    @property
    def _key_actions(self) -> Dict[int, Callable[[], None]]:
        mgr = KeyBindingsManager.get_instance()
        res: Dict[int, Callable[[], None]] = {}
        for action, handler in self._action_handlers.items():
            for key in mgr.get_action_keys(action):
                res[key] = handler
        return res

    @property
    def _pan_keys(self) -> Dict[int, Tuple[float, float]]:
        mgr = KeyBindingsManager.get_instance()
        res: Dict[int, Tuple[float, float]] = {}
        for action, delta in self._pan_actions.items():
            for key in mgr.get_action_keys(action):
                res[key] = delta
        return res

    def switch_mode(self, mode: SimulationMode) -> None:
        self.sim_mode = mode
        self.mode_3d = (mode == SimulationMode.KINEMATICS_3D)
        self.selected_shape = None
        self.placement_mode = None
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.zoom_2d = 1.0

        # Rebuild ScenarioManager so file tree points to this mode's directory
        self.scenarios = ScenarioManager(mode=mode)

        # Free inactive mode scenes/renderers
        self.circuit_scene = None
        self.circuit_renderer = None
        self.optics_scene = None
        self.optics_renderer = None
        self.fields_scene = None
        self.fields_renderer = None

        match mode:
            case SimulationMode.KINEMATICS_3D | SimulationMode.KINETIC_2D:
                self.sim.clear_shapes()
                self.trails.clear()
            case SimulationMode.CIRCUITS:
                self.circuit_scene = CircuitScene()
                self.circuit_scene.create_default_circuit()
                self.circuit_renderer = CircuitRenderer()
            case SimulationMode.OPTICS:
                self.optics_scene = OpticsScene()
                self.optics_scene.create_default_scene()
                self.optics_renderer = OpticsRenderer()
            case SimulationMode.FIELDS:
                self.fields_scene = FieldScene()
                self.fields_scene.create_default_scene()
                self.fields_renderer = FieldsRenderer()

        # Refresh load screen so its file tree reflects the new mode directory
        if hasattr(self, 'load_scenario_screen'):
            self.load_scenario_screen.refresh_for_mode()

    def _build_screen_render_map(self) -> None:
        """Build the screen→handler dispatch map once all screen objects are ready."""
        self._screen_render_map = {
            AppScreen.MAIN_MENU:     self._handle_screen_main_menu,
            AppScreen.SETTINGS:      self._handle_screen_settings,
            AppScreen.LOAD_SCENARIO: self._handle_screen_load_scenario,
        }

    def handle_input(self) -> None:
        match self.current_screen:
            case AppScreen.MAIN_MENU:
                if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
                    self.should_quit = True
                return
            case AppScreen.SETTINGS | AppScreen.SCENARIOS | AppScreen.LOAD_SCENARIO:
                if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
                    self.current_screen = AppScreen.MAIN_MENU
                return
            case AppScreen.SIMULATION:
                if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
                    if self.placement_mode:
                        self.placement_mode = None
                    elif self.selected_shape:
                        self.selected_shape = None
                    else:
                        self.current_screen = AppScreen.MAIN_MENU
                    return

        mouse_pos = pr.get_mouse_position()
        is_over_panel = self.workspace_ui.is_over_ui(mouse_pos)

        is_shift = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_SHIFT) or pr.is_key_down(pr.KeyboardKey.KEY_RIGHT_SHIFT)
        wheel_move = pr.get_mouse_wheel_move()
        if is_shift and wheel_move != 0:
            if self.selected_shape is not None and hasattr(self.selected_shape, 'pos'):
                self.selected_shape.pos.y = max(0.1, min(50.0, self.selected_shape.pos.y + wheel_move * 0.5))
                if hasattr(self.selected_shape, 'vel'):
                    self.selected_shape.vel.y = 0.0
            elif self.placement_mode:
                self.spawn_height = max(0.5, min(14.0, self.spawn_height + wheel_move * 0.5))
            elif self.mode_3d:
                self.camera_ctrl.target.y = max(-50.0, min(100.0, self.camera_ctrl.target.y + wheel_move * 0.5))
                self.camera_ctrl.update_camera_vectors()
            else:
                self.pan_y += wheel_move * 10.0

        # Interactive placement adjustments
        if self.placement_mode:
            if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_RIGHT):
                self.placement_mode = None
                return
            wheel = pr.get_mouse_wheel_move()
            if not is_shift and wheel != 0:
                self.spawn_height = max(0.5, min(14.0, self.spawn_height + wheel * 0.5))
        elif self.mode_3d:
            # Check object picking selection on Left Click via dispatch table
            if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) and not is_over_panel:
                ray = pr.get_screen_to_world_ray(mouse_pos, self.camera_ctrl.camera)
                hit_any = False
                for s in self.sim.scene.shapes:
                    col = self._ray_pick_3d.get(s.shape_type, self._ray_pick_3d["sphere"])(ray, s)
                    if col.hit:
                        self.selected_shape = s
                        self.graph_renderer.clear()
                        hit_any = True
                        break
                if not hit_any:
                    self.selected_shape = None
            else:
                self.camera_ctrl.handle_input()
        else:
            if pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_RIGHT) or pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_MIDDLE):
                delta = pr.get_mouse_delta()
                self.pan_x += delta.x
                self.pan_y += delta.y
            # Accumulate pan direction from all held actions in a single pass
            pan_speed = 5.0
            mgr = KeyBindingsManager.get_instance()
            for action, (dx, dy) in self._pan_actions.items():
                if mgr.is_action_down(action):
                    self.pan_x += dx * pan_speed
                    self.pan_y += dy * pan_speed

            # 2D Zoom via mouse wheel and keyboard actions
            wheel = 0.0 if is_shift else pr.get_mouse_wheel_move()
            zoom_delta = wheel * 0.1
            if mgr.is_action_down(ACTION_ZOOM_IN):
                zoom_delta += 1.0 * max(0.001, pr.get_frame_time())
            if mgr.is_action_down(ACTION_ZOOM_OUT):
                zoom_delta -= 1.0 * max(0.001, pr.get_frame_time())
            if zoom_delta != 0.0:
                self.zoom_2d = max(0.2, min(5.0, self.zoom_2d + zoom_delta))

        # Keyboard shortcuts via dynamic action dispatch
        mgr = KeyBindingsManager.get_instance()
        for action, handler in self._action_handlers.items():
            if mgr.is_action_pressed(action):
                handler()
                break

        if pr.is_key_down(pr.KeyboardKey.KEY_LEFT):
            self.sim.rewind(steps=5)

    def _stop_sim(self) -> None:
        self.sim.stop()
        self.trails.clear()

    def _toggle_grid(self) -> None:
        self.grid.show_grid = not self.grid.show_grid

    def _cycle_resolution(self) -> None:
        self.res_index = (self.res_index + 1) % len(self.resolutions)
        w, h = self.resolutions[self.res_index]
        pr.set_window_size(w, h)

    def render_hud(self) -> None:
        self.workspace_ui.update_and_draw()

        # Display placement mode banner
        if self.placement_mode:
            msg = f"PLACEMENT MODE (+ {self.placement_mode.upper()}): Aim & Left Click to Place | Scroll Wheel adjusts height | Right Click / ESC to Cancel"
            box_w = pr.measure_text(msg, 15) + 30
            bx = (pr.get_screen_width() - box_w) // 2
            pr.draw_rectangle_rounded(pr.Rectangle(bx, 50, box_w, 36), 0.4, 8, pr.Color(20, 22, 27, 230))
            pr.draw_rectangle_rounded_lines(pr.Rectangle(bx, 50, box_w, 36), 0.4, 8, Colors.UI_ACTIVE)
            pr.draw_text(msg, bx + 15, 60, 15, Colors.UI_ACTIVE)

        # Draw Inspector Graph Panel if a rigid shape is selected
        if self.selected_shape in self.sim.scene.shapes:
            self.graph_renderer.draw(self.selected_shape, -self.workspace_ui.slider_gravity.value)

        if self.mode_3d and getattr(self.axis_indicator, 'show', True):
            self.axis_indicator.draw(self.camera_ctrl.camera, pr.get_screen_width(), pr.get_screen_height())

    def _handle_screen_main_menu(self, dt: float) -> bool:
        """Render main menu. Returns True if we should skip simulation rendering."""
        next_screen = self.main_menu.update_and_draw(self)
        if next_screen == self.current_screen:
            return True
        if next_screen == AppScreen.QUIT:
            self.should_quit = True
        elif next_screen == AppScreen.SIMULATION:
            if not self.sim.scene.shapes:
                loaded = self.scenarios.load_scenario(self.active_scenario_name)
                if loaded:
                    self.sim.load_scene(loaded)
                    self.trails.clear()
            self.current_screen = next_screen
        elif next_screen == AppScreen.LOAD_SCENARIO:
            self.load_scenario_screen.refresh_list()
            self.current_screen = next_screen
        else:
            self.current_screen = next_screen
        return True

    def _handle_screen_settings(self, dt: float) -> bool:
        """Render settings screen. Returns True to skip simulation rendering."""
        next_screen = self.settings_screen.update_and_draw()
        if next_screen != AppScreen.SETTINGS:
            self.current_screen = next_screen
        return True

    def _handle_screen_load_scenario(self, dt: float) -> bool:
        """Render load scenario screen. Returns True to skip simulation rendering."""
        next_screen = self.load_scenario_screen.update_and_draw()
        if next_screen != AppScreen.LOAD_SCENARIO:
            if next_screen == AppScreen.SIMULATION:
                selected_name = self.load_scenario_screen.get_selected_scenario()
                self.active_scenario_name = selected_name
                loaded = self.scenarios.load_scenario(selected_name)
                if loaded:
                    self.sim.load_scene(loaded)
                    self.trails.clear()
            self.current_screen = next_screen
        return True

    def render_frame(self) -> None:
        # Lazily build the screen dispatch map on first frame (all screen objects guaranteed ready)
        if self._screen_render_map is None:
            self._build_screen_render_map()

        dt = pr.get_frame_time()

        pr.begin_drawing()
        pr.clear_background(Colors.BACKGROUND)

        # Dispatch to the appropriate screen handler; returns True if we should stop here
        screen_handler = self._screen_render_map.get(self.current_screen)
        if screen_handler and screen_handler(dt):
            pr.end_drawing()
            return

        # Advance backend simulation integration
        # gravity is driven by the live workspace slider (positive UI magnitude -> downward pull)
        gravity = -self.workspace_ui.slider_gravity.value
        self.sim.step(dt, gravity, particle_system=self.particles, trail_renderer=self.trails)

        if self.sim.state == "PLAYING" and self.selected_shape in self.sim.scene.shapes:
            self.graph_renderer.add_sample(self.selected_shape, gravity)

        match self.sim_mode:
            case SimulationMode.CIRCUITS:
                self._render_mode_circuits(dt)
            case SimulationMode.OPTICS:
                self._render_mode_optics(dt)
            case SimulationMode.FIELDS:
                self._render_mode_fields(dt)
            case SimulationMode.KINEMATICS_3D:
                self._render_mode_3d(dt, gravity)
            case SimulationMode.KINETIC_2D:
                self._render_mode_2d(dt, gravity)

        self.render_hud()
        pr.end_drawing()

    def _render_mode_circuits(self, dt: float) -> None:
        from Simulation.sim_circuits import CircuitSolver
        CircuitSolver.step(self.circuit_scene)
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        mouse_pos = pr.get_mouse_position()
        is_over_ui = self.workspace_ui.is_over_ui(mouse_pos)
        self.circuit_renderer.scale = 40.0 * self.zoom_2d
        self.circuit_renderer.handle_input(self.circuit_scene, sw, sh, self.pan_x, self.pan_y, is_over_ui)
        self.circuit_renderer.draw(self.circuit_scene, sw, sh, dt, self.pan_x, self.pan_y)
        if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) and not is_over_ui:
            cx = int(sw // 2 + self.pan_x)
            cy = int(sh // 2 + self.pan_y)
            gx = round((mouse_pos.x - cx) / self.circuit_renderer.scale * 2.0) / 2.0
            gy = round((cy - mouse_pos.y) / self.circuit_renderer.scale * 2.0) / 2.0
            picked = self.circuit_scene.pick_component(gx, gy)
            self.selected_shape = picked

    def _render_mode_optics(self, dt: float) -> None:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        self.optics_renderer.scale = 40.0 * self.zoom_2d
        self.optics_renderer.draw(self.optics_scene, sw, sh, dt, self.pan_x, self.pan_y)
        self._handle_grid_picking_placing(sw, sh)

    def _render_mode_fields(self, dt: float) -> None:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        self.fields_renderer.scale = 40.0 * self.zoom_2d
        self.fields_renderer.draw(self.fields_scene, sw, sh, dt, self.pan_x, self.pan_y)
        self._handle_grid_picking_placing(sw, sh)

    def _handle_grid_picking_placing(self, sw: int, sh: int) -> None:
        mouse_pos = pr.get_mouse_position()
        is_over_panel = self.workspace_ui.is_over_ui(mouse_pos)
        cx = int(sw // 2 + self.pan_x)
        cy = int(sh // 2 + self.pan_y)
        scale = 40.0 * self.zoom_2d
        gx = round((mouse_pos.x - cx) / scale * 2.0) / 2.0
        gy = round((cy - mouse_pos.y) / scale * 2.0) / 2.0
        screen_gx = cx + int(gx * scale)
        screen_gy = cy - int(gy * scale)

        if is_over_panel:
            return

        if self.placement_mode:
            pr.draw_circle_lines(screen_gx, screen_gy, 15, pr.Color(0, 255, 100, 200))
            if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT):
                spawn_actions = {
                    "emitter": lambda: self.optics_scene.add_emitter(gx, gy, 0.0),
                    "mirror": lambda: self.optics_scene.add_mirror(gx, gy, 135.0, 3.0),
                    "lens": lambda: self.optics_scene.add_lens(gx, gy, 2.5, 3.5),
                    "+charge": lambda: self.fields_scene.add_charge(gx, gy, 1.0),
                    "-charge": lambda: self.fields_scene.add_charge(gx, gy, -1.0),
                    "magnet": lambda: self.fields_scene.add_magnet(gx, gy, 2.0, 0.0)
                }
                action = spawn_actions.get(self.placement_mode)
                if action:
                    self.selected_shape = action()
                self.placement_mode = None
            return

        if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT):
            match self.sim_mode:
                case SimulationMode.OPTICS:
                    if self.optics_scene:
                        self.selected_shape = self.optics_scene.pick_element(gx, gy)
                case SimulationMode.FIELDS:
                    if self.fields_scene:
                        self.selected_shape = self.fields_scene.pick_source(gx, gy)
            return

        if pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT):
            if self.selected_shape and hasattr(self.selected_shape, 'x') and hasattr(self.selected_shape, 'y'):
                self.selected_shape.x = gx
                self.selected_shape.y = gy

    def _render_mode_3d(self, dt: float, gravity: float) -> None:
        pr.begin_mode_3d(self.camera_ctrl.camera)
        self.grid.draw_3d()
        self.trails.draw_3d()

        if self.selected_shape in self.sim.scene.shapes:
            pr.draw_circle_3d(pr.Vector3(self.selected_shape.pos.x, 0.05, self.selected_shape.pos.z), self.selected_shape.radius * 1.4, pr.Vector3(1, 0, 0), 90.0, Colors.UI_ACTIVE)

        for s in self.sim.scene.shapes:
            draw_fns = self._shape_draw_3d.get(s.shape_type)
            if draw_fns:
                draw_fns[0](s)
                draw_fns[1](s)
            self.vectors.draw_vector_3d(s.pos, pr.Vector3(s.vel.x * 0.3, s.vel.y * 0.3, s.vel.z * 0.3), Colors.VECTOR_VELOCITY)
            self.vectors.draw_vector_3d(s.pos, pr.Vector3(0.0, gravity * 0.15, 0.0), Colors.VECTOR_ACCEL)

        if self.placement_mode:
            mouse_pos = pr.get_mouse_position()
            ray = pr.get_screen_to_world_ray(mouse_pos, self.camera_ctrl.camera)
            if abs(ray.direction.y) > 0.0001:
                t = (self.spawn_height - ray.position.y) / ray.direction.y
                if t > 0:
                    gx = max(-14.0, min(14.0, ray.position.x + t * ray.direction.x))
                    gz = max(-14.0, min(14.0, ray.position.z + t * ray.direction.z))
                    ghost_pos = pr.Vector3(gx, self.spawn_height, gz)

                    pr.draw_line_3d(ghost_pos, pr.Vector3(gx, 0.0, gz), pr.Color(0, 255, 100, 180))
                    pr.draw_circle_3d(pr.Vector3(gx, 0.02, gz), 1.0, pr.Vector3(1, 0, 0), 90.0, pr.Color(0, 255, 100, 120))

                    if self.placement_mode == "sphere":
                        pr.draw_sphere(ghost_pos, 1.0, pr.Color(0, 255, 100, 150))
                        pr.draw_sphere_wires(ghost_pos, 1.0, 16, 16, pr.Color(0, 255, 100, 255))
                    else:
                        pr.draw_cube(ghost_pos, 2.0, 2.0, 2.0, pr.Color(0, 255, 100, 150))
                        pr.draw_cube_wires(ghost_pos, 2.0, 2.0, 2.0, pr.Color(0, 255, 100, 255))

                    is_over_panel = self.workspace_ui.is_over_ui(mouse_pos)
                    if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) and not is_over_panel:
                        new_s = self.sim.spawn_shape_at(self.placement_mode, ghost_pos)
                        self.selected_shape = new_s
                        self.graph_renderer.clear()
                        self.placement_mode = None

        self.particles.update_and_draw(dt)
        pr.end_mode_3d()

    def _render_mode_2d(self, dt: float, gravity: float) -> None:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        center_x = int(sw // 2 + self.pan_x)
        center_y = int(sh // 2 + self.pan_y)
        scale = 35.0 * self.zoom_2d

        start_x = int(center_x % scale)
        for lx in range(start_x, sw, int(scale)):
            pr.draw_line(lx, 0, lx, sh, pr.Color(30, 35, 45, 100))
        start_y = int(center_y % scale)
        for ly in range(start_y, sh, int(scale)):
            pr.draw_line(0, ly, sw, ly, pr.Color(30, 35, 45, 100))

        if 0 <= center_y <= sh:
            pr.draw_line(0, center_y, sw, center_y, pr.Color(100, 100, 110, 150))
        if 0 <= center_x <= sw:
            pr.draw_line(center_x, 0, center_x, sh, pr.Color(100, 100, 110, 150))

        # 2D shape draw dispatch: avoid per-shape if/elif inside a tight loop
        def _draw_shape_2d(s, proj_x: int, proj_y: int, is_sel: bool) -> None:
            if s.shape_type == "sphere":
                rad = max(4, int(s.radius * scale))
                if is_sel:
                    pr.draw_circle(proj_x, proj_y, rad + 4, Colors.UI_ACTIVE)
                pr.draw_circle(proj_x, proj_y, rad, s.color)
                pr.draw_circle_lines(proj_x, proj_y, rad, pr.WHITE)
            else:
                w = max(8, int(s.size.x * scale))
                h = max(8, int(s.size.y * scale))
                rect = pr.Rectangle(proj_x - w // 2, proj_y - h // 2, w, h)
                if is_sel:
                    pr.draw_rectangle_rounded(pr.Rectangle(rect.x - 3, rect.y - 3, rect.width + 6, rect.height + 6), 0.1, 4, Colors.UI_ACTIVE)
                pr.draw_rectangle_rounded(rect, 0.1, 4, s.color)
                pr.draw_rectangle_rounded_lines(rect, 0.1, 4, pr.WHITE)

        # 2D shape hit-test dispatch: returns True if mouse hits the shape
        def _hit_test_2d(s, px: int, py: int) -> bool:
            if s.shape_type == "sphere":
                return math.hypot(mouse_pos.x - px, mouse_pos.y - py) <= int(s.radius * scale)
            w, h = int(s.size.x * scale), int(s.size.y * scale)
            return abs(mouse_pos.x - px) <= w // 2 and abs(mouse_pos.y - py) <= h // 2

        for s in self.sim.scene.shapes:
            proj_x = center_x + int(s.pos.x * scale)
            proj_y = center_y - int(s.pos.y * scale)
            _draw_shape_2d(s, proj_x, proj_y, s == self.selected_shape)

            vx_end = proj_x + int(s.vel.x * 8)
            vy_end = proj_y - int(s.vel.y * 8)
            pr.draw_line_ex(pr.Vector2(proj_x, proj_y), pr.Vector2(vx_end, vy_end), 3.0, Colors.VECTOR_VELOCITY)
            pr.draw_circle(vx_end, vy_end, 4, Colors.VECTOR_VELOCITY)

            ay_end = proj_y - int(gravity * 3)
            pr.draw_line_ex(pr.Vector2(proj_x, proj_y), pr.Vector2(proj_x, ay_end), 2.0, Colors.VECTOR_ACCEL)

        mouse_pos = pr.get_mouse_position()
        is_over_panel = self.workspace_ui.is_over_ui(mouse_pos)

        if self.placement_mode:
            gx = round((mouse_pos.x - center_x) / scale * 2.0) / 2.0
            gy = round((center_y - mouse_pos.y) / scale * 2.0) / 2.0
            screen_gx = center_x + int(gx * scale)
            screen_gy = center_y - int(gy * scale)

            if self.placement_mode == "sphere":
                pr.draw_circle_lines(screen_gx, screen_gy, int(1.0 * scale), pr.Color(0, 255, 100, 200))
            else:
                w = int(2.0 * scale)
                pr.draw_rectangle_lines(screen_gx - w // 2, screen_gy - w // 2, w, w, pr.Color(0, 255, 100, 200))

            if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) and not is_over_panel:
                new_s = self.sim.spawn_shape_at(self.placement_mode, pr.Vector3(gx, gy, 0.0))
                self.selected_shape = new_s
                self.graph_renderer.clear()
                self.placement_mode = None
        elif pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) and not is_over_panel:
            # Single-pass pick: iterate reversed for top-draw-order priority
            clicked_shape = next(
                (s for s in reversed(self.sim.scene.shapes)
                 if _hit_test_2d(s, center_x + int(s.pos.x * scale), center_y - int(s.pos.y * scale))),
                None
            )
            self.selected_shape = clicked_shape

    def cleanup(self) -> None:
        pr.close_window()
