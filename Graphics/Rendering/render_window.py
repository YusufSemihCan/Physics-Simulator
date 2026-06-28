import pyray as pr
import math
from Graphics.Rendering.render_colors import Colors
from Graphics.Rendering.render_grid import GridRenderer
from Graphics.Rendering.render_camera import CameraController
from Graphics.Rendering.render_particles import TrailRenderer, ParticleSystem
from Graphics.Rendering.render_vectors import VectorRenderer
from Graphics.UI.ui_axis_indicator import AxisIndicator
from Graphics.UI.ui_elements import Panel, Slider, Toggle, Button
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

        # Initialize UI sidebar panel and simulation widgets
        self.ui_panel = Panel(15, 60, 270, 415, "Simulation Controls")
        self.slider_gravity = Slider(30, 105, 240, 12, "Gravity (m/s^2)", -20.0, 20.0, -9.81)
        self.toggle_grid = Toggle(30, 155, 18, "Show Grid Lines", True)

        # Playback Controls
        self.btn_play = Button(30, 195, 115, 34, "Play / Pause")
        self.btn_stop = Button(155, 195, 115, 34, "Stop / Reset")
        self.btn_rewind = Button(30, 235, 240, 34, "<< Rewind 1s (Hold)")

        # Spawning Controls
        self.btn_add_sphere = Button(30, 290, 115, 34, "+ Sphere")
        self.btn_add_cube = Button(155, 290, 115, 34, "+ Cube")
        self.btn_clear = Button(30, 330, 240, 34, "Clear All Shapes")

        # Navigation Controls
        self.btn_scenarios = Button(30, 380, 240, 34, "Scenario File Tree")
        self.btn_menu = Button(30, 424, 240, 34, "Main Menu")

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
        self.switch_mode(SimulationMode.KINEMATICS_3D)

        # Circuit tool buttons
        self.btn_c_wire = Button(30, 290, 115, 30, "Wire")
        self.btn_c_bat = Button(155, 290, 115, 30, "Battery")
        self.btn_c_res = Button(30, 330, 115, 30, "Resistor")
        self.btn_c_sw = Button(155, 330, 115, 30, "Switch")
        self.btn_c_bulb = Button(90, 370, 115, 30, "Bulb")
        self.workspace_ui = WorkspaceUI(self)

    def switch_mode(self, mode: SimulationMode) -> None:
        self.sim_mode = mode
        self.mode_3d = (mode == SimulationMode.KINEMATICS_3D)
        self.selected_shape = None
        self.placement_mode = None
        self.pan_x = 0.0
        self.pan_y = 0.0

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
        sw = pr.get_screen_width()
        is_over_panel = self.workspace_ui.is_over_ui(mouse_pos)

        # Interactive placement adjustments
        if self.placement_mode:
            if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_RIGHT):
                self.placement_mode = None
                return
            wheel = pr.get_mouse_wheel_move()
            if wheel != 0:
                self.spawn_height = max(0.5, min(14.0, self.spawn_height + wheel * 0.5))
        elif self.mode_3d:
            # Check object picking selection on Left Click
            if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) and not is_over_panel:
                ray = pr.get_mouse_ray(mouse_pos, self.camera_ctrl.camera)
                hit_any = False
                for s in self.sim.scene.shapes:
                    if s.shape_type == "sphere":
                        col = pr.get_ray_collision_sphere(ray, s.pos, s.radius)
                    else:
                        hw, hh, hd = s.size.x / 2, s.size.y / 2, s.size.z / 2
                        box = pr.BoundingBox(pr.Vector3(s.pos.x - hw, s.pos.y - hh, s.pos.z - hd), pr.Vector3(s.pos.x + hw, s.pos.y + hh, s.pos.z + hd))
                        col = pr.get_ray_collision_box(ray, box)
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
            pan_speed = 5.0
            if pr.is_key_down(pr.KeyboardKey.KEY_W) or pr.is_key_down(pr.KeyboardKey.KEY_UP):
                self.pan_y += pan_speed
            if pr.is_key_down(pr.KeyboardKey.KEY_S) or pr.is_key_down(pr.KeyboardKey.KEY_DOWN):
                self.pan_y -= pan_speed
            if pr.is_key_down(pr.KeyboardKey.KEY_A):
                self.pan_x += pan_speed
            if pr.is_key_down(pr.KeyboardKey.KEY_D):
                self.pan_x -= pan_speed

        # Keyboard shortcuts for classroom playback & features
        if pr.is_key_pressed(pr.KeyboardKey.KEY_P) or pr.is_key_pressed(pr.KeyboardKey.KEY_SPACE):
            self.sim.toggle_play()
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_S):
            self.sim.stop()
            self.trails.clear()
        elif pr.is_key_down(pr.KeyboardKey.KEY_LEFT):
            self.sim.rewind(steps=5)
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_G):
            self.grid.show_grid = not self.grid.show_grid
            self.toggle_grid.state = self.grid.show_grid
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_V):
            self.vectors.enabled = not self.vectors.enabled
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_T):
            self.trails.enabled = not self.trails.enabled
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_F11) or pr.is_key_pressed(pr.KeyboardKey.KEY_B):
            pr.toggle_borderless_windowed()
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_R):
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
            self.graph_renderer.draw(self.selected_shape, self.workspace_ui.slider_gravity.value)

        if self.mode_3d and getattr(self.axis_indicator, 'show', True):
            self.axis_indicator.draw(self.camera_ctrl.camera, pr.get_screen_width(), pr.get_screen_height())

    def render_frame(self) -> None:
        dt = pr.get_frame_time()

        pr.begin_drawing()
        pr.clear_background(Colors.BACKGROUND)

        if self.current_screen == AppScreen.MAIN_MENU:
            next_screen = self.main_menu.update_and_draw(self)
            if next_screen != AppScreen.MAIN_MENU:
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
            pr.end_drawing()
            return

        if self.current_screen == AppScreen.SETTINGS:
            next_screen = self.settings_screen.update_and_draw()
            if next_screen != AppScreen.SETTINGS:
                self.current_screen = next_screen
            pr.end_drawing()
            return

        if self.current_screen == AppScreen.LOAD_SCENARIO:
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
                else:
                    self.current_screen = next_screen
            pr.end_drawing()
            return

        # Advance backend simulation integration
        gravity = self.slider_gravity.value
        self.sim.step(dt, gravity, particle_system=self.particles, trail_renderer=self.trails)

        if self.sim.state == "PLAYING" and self.selected_shape:
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
        self.circuit_renderer.handle_input(self.circuit_scene, sw, sh, self.pan_x, self.pan_y, is_over_ui)
        self.circuit_renderer.draw(self.circuit_scene, sw, sh, dt, self.pan_x, self.pan_y)
        if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) and not is_over_ui:
            cx = int(sw // 2 + self.pan_x)
            cy = int(sh // 2 + self.pan_y)
            gx = round((mouse_pos.x - cx) / 40.0 * 2.0) / 2.0
            gy = round((cy - mouse_pos.y) / 40.0 * 2.0) / 2.0
            picked = self.circuit_scene.pick_component(gx, gy)
            if picked:
                self.selected_shape = picked

    def _render_mode_optics(self, dt: float) -> None:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        self.optics_renderer.draw(self.optics_scene, sw, sh, dt, self.pan_x, self.pan_y)
        self._handle_grid_picking_placing(sw, sh)

    def _render_mode_fields(self, dt: float) -> None:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        self.fields_renderer.draw(self.fields_scene, sw, sh, dt, self.pan_x, self.pan_y)
        self._handle_grid_picking_placing(sw, sh)

    def _handle_grid_picking_placing(self, sw: int, sh: int) -> None:
        mouse_pos = pr.get_mouse_position()
        is_over_panel = self.workspace_ui.is_over_ui(mouse_pos)
        cx = int(sw // 2 + self.pan_x)
        cy = int(sh // 2 + self.pan_y)
        scale = 40.0
        gx = round((mouse_pos.x - cx) / scale * 2.0) / 2.0
        gy = round((cy - mouse_pos.y) / scale * 2.0) / 2.0
        screen_gx = cx + int(gx * scale)
        screen_gy = cy - int(gy * scale)

        if self.placement_mode:
            pr.draw_circle_lines(screen_gx, screen_gy, 15, pr.Color(0, 255, 100, 200))
            if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) and not is_over_panel:
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
        elif pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) and not is_over_panel:
            picker = {
                SimulationMode.OPTICS: self.optics_scene.pick_element,
                SimulationMode.FIELDS: self.fields_scene.pick_source
            }.get(self.sim_mode)
            if picker:
                self.selected_shape = picker(gx, gy)

    def _render_mode_3d(self, dt: float, gravity: float) -> None:
        pr.begin_mode_3d(self.camera_ctrl.camera)
        self.grid.draw_3d()
        self.trails.draw_3d()

        if self.selected_shape in self.sim.scene.shapes:
            pr.draw_circle_3d(pr.Vector3(self.selected_shape.pos.x, 0.05, self.selected_shape.pos.z), self.selected_shape.radius * 1.4, pr.Vector3(1, 0, 0), 90.0, Colors.UI_ACTIVE)

        for s in self.sim.scene.shapes:
            if s.shape_type == "sphere":
                pr.draw_sphere(s.pos, s.radius, s.color)
                pr.draw_sphere_wires(s.pos, s.radius, 16, 16, Colors.AXIS_X)
            elif s.shape_type == "cube":
                pr.draw_cube(s.pos, s.size.x, s.size.y, s.size.z, s.color)
                pr.draw_cube_wires(s.pos, s.size.x, s.size.y, s.size.z, Colors.AXIS_X)

            self.vectors.draw_vector_3d(s.pos, pr.Vector3(s.vel.x * 0.3, s.vel.y * 0.3, s.vel.z * 0.3), Colors.VECTOR_VELOCITY)
            self.vectors.draw_vector_3d(s.pos, pr.Vector3(0.0, gravity * 0.15, 0.0), Colors.VECTOR_ACCEL)

        if self.placement_mode:
            mouse_pos = pr.get_mouse_position()
            ray = pr.get_mouse_ray(mouse_pos, self.camera_ctrl.camera)
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
        scale = 35.0

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

        for s in self.sim.scene.shapes:
            proj_x = center_x + int(s.pos.x * scale)
            proj_y = center_y - int(s.pos.y * scale)
            is_sel = (s == self.selected_shape)

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
            clicked_shape = None
            for s in reversed(self.sim.scene.shapes):
                px = center_x + int(s.pos.x * scale)
                py = center_y - int(s.pos.y * scale)
                if s.shape_type == "sphere":
                    if math.hypot(mouse_pos.x - px, mouse_pos.y - py) <= int(s.radius * scale):
                        clicked_shape = s
                        break
                else:
                    w = int(s.size.x * scale)
                    h = int(s.size.y * scale)
                    if abs(mouse_pos.x - px) <= w // 2 and abs(mouse_pos.y - py) <= h // 2:
                        clicked_shape = s
                        break
            if clicked_shape:
                self.selected_shape = clicked_shape
        pr.end_drawing()

    def cleanup(self) -> None:
        pr.close_window()
