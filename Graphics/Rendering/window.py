import pyray as pr
from graphics.rendering.colors import Colors
from graphics.rendering.grid import GridRenderer
from graphics.ui.elements import Panel, Slider, Toggle, Button

class SimulationRenderer:
    def __init__(self, width: int = 1280, height: int = 720, title: str = "Antigravity Raylib Physics Engine"):
        # Configure OpenGL window flags before initialization (resizable + maximized + high DPI + MSAA 4X anti-aliasing)
        pr.set_config_flags(
            pr.ConfigFlags.FLAG_WINDOW_RESIZABLE | 
            pr.ConfigFlags.FLAG_WINDOW_MAXIMIZED | 
            pr.ConfigFlags.FLAG_WINDOW_HIGHDPI | 
            pr.ConfigFlags.FLAG_MSAA_4X_HINT
        )
        pr.init_window(width, height, title)
        pr.set_target_fps(60)

        # Configure 3D perspective orbital camera
        self.camera_3d = pr.Camera3D(
            pr.Vector3(12.0, 12.0, 12.0),
            pr.Vector3(0.0, 0.0, 0.0),
            pr.Vector3(0.0, 1.0, 0.0),
            45.0,
            pr.CameraProjection.CAMERA_PERSPECTIVE
        )

        self.grid = GridRenderer(slices=30, spacing=1.0)
        self.mode_3d = True
        self.resolutions = [(1280, 720), (1600, 900), (1920, 1080), (2560, 1440)]
        self.res_index = 0

        # Initialize educational UI sidebar panel and widgets
        self.ui_panel = Panel(15, 65, 260, 210, "Physics Controls")
        self.slider_gravity = Slider(30, 115, 230, 12, "Gravity (m/s^2)", -20.0, 20.0, -9.81)
        self.toggle_grid = Toggle(30, 175, 18, "Show Grid Lines", True)
        self.btn_reset = Button(30, 220, 230, 36, "Reset Simulation")

    def handle_input(self) -> None:
        # Poll hardware input queue for viewport mode switching or grid toggles
        if pr.is_key_pressed(pr.KeyboardKey.KEY_M):
            self.mode_3d = not self.mode_3d
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_G):
            self.grid.show_grid = not self.grid.show_grid
            self.toggle_grid.state = self.grid.show_grid
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_F11):
            pr.toggle_fullscreen()
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_B):
            if hasattr(pr, "toggle_borderless_windowed"):
                pr.toggle_borderless_windowed()
            else:
                pr.toggle_fullscreen()
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_R):
            self.res_index = (self.res_index + 1) % len(self.resolutions)
            w, h = self.resolutions[self.res_index]
            pr.set_window_size(w, h)

    def render_hud(self) -> None:
        # Render 2D Heads-Up Display directly over OpenGL frame buffer
        mode_str = "3D PERSPECTIVE" if self.mode_3d else "2D CARTESIAN"
        res_str = f"{pr.get_screen_width()}x{pr.get_screen_height()}"
        pr.draw_text(f"ANTIGRAVITY ENGINE [GPU MODE: {mode_str}] | RES: {res_str}", 15, 15, 20, Colors.TEXT)
        pr.draw_text("Controls: [M] 2D/3D | [G] Grid | [R] Cycle Res | [F11] Fullscreen | [B] Borderless | [ESC] Quit", 15, 42, 16, pr.GRAY)
        pr.draw_fps(pr.get_screen_width() - 95, 15)

        # Draw interactive UI Panel and widgets
        self.ui_panel.draw()
        gravity_val = self.slider_gravity.update_and_draw()
        self.grid.show_grid = self.toggle_grid.update_and_draw()
        if self.btn_reset.update_and_draw():
            print(f"[!] Reset Simulation clicked! Current Gravity: {gravity_val:.2f} m/s^2")

    def render_frame(self) -> None:
        pr.begin_drawing()
        pr.clear_background(Colors.BACKGROUND)

        if self.mode_3d:
            # Dispatch hardware GPU draw calls inside 3D camera perspective matrix
            pr.begin_mode_3d(self.camera_3d)
            self.grid.draw_3d()

            # Render demonstration 3D rigid body sphere at origin
            pr.draw_sphere(pr.Vector3(0.0, 1.0, 0.0), 1.0, Colors.SHAPE_ACCENT)
            pr.draw_sphere_wires(pr.Vector3(0.0, 1.0, 0.0), 1.0, 16, 16, Colors.AXIS_X)
            pr.end_mode_3d()
        else:
            # Render 2D orthographic physics entities
            self.grid.draw_2d(pr.get_screen_width(), pr.get_screen_height())
            center_x, center_y = pr.get_screen_width() // 2, pr.get_screen_height() // 2
            pr.draw_circle(center_x, center_y, 45, Colors.SHAPE_ACCENT)

        self.render_hud()
        pr.end_drawing()

    def cleanup(self) -> None:
        # Unbind OpenGL context and cleanly release hardware display drivers
        pr.close_window()
