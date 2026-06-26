import pyray as pr

class Colors:
    # Curated HSL dark mode color palette formatted as Raylib hardware GPU Color structs
    BACKGROUND = pr.Color(24, 26, 31, 255)
    GRID_MAJOR = pr.Color(65, 71, 84, 255)
    GRID_MINOR = pr.Color(40, 44, 52, 255)
    AXIS_X = pr.Color(224, 108, 117, 255)
    AXIS_Y = pr.Color(152, 195, 121, 255)
    AXIS_Z = pr.Color(97, 175, 239, 255)
    SHAPE_ACCENT = pr.Color(229, 192, 123, 255)
    TEXT = pr.Color(209, 213, 219, 255)


class GridRenderer:
    def __init__(self, slices: int = 30, spacing: float = 1.0):
        self.slices = slices
        self.spacing = spacing
        self.show_grid = True

    def draw_3d(self) -> None:
        if not self.show_grid:
            return
        # Hardware GPU accelerated 3D floor grid rendering
        pr.draw_grid(self.slices, self.spacing)

    def draw_2d(self, screen_width: int, screen_height: int) -> None:
        if not self.show_grid:
            return
        # Calculate dynamic 2D Cartesian quadrant divisions relative to viewport resolution
        center_x, center_y = screen_width // 2, screen_height // 2
        cell_size = 50

        for x in range(center_x % cell_size, screen_width, cell_size):
            pr.draw_line(x, 0, x, screen_height, Colors.GRID_MINOR)
        for y in range(center_y % cell_size, screen_height, cell_size):
            pr.draw_line(0, y, screen_width, y, Colors.GRID_MINOR)

        # Highlight origin coordinate axes (X=Red, Y=Green)
        pr.draw_line(0, center_y, screen_width, center_y, Colors.AXIS_X)
        pr.draw_line(center_x, 0, center_x, screen_height, Colors.AXIS_Y)


class SimulationRenderer:
    def __init__(self, width: int = 1280, height: int = 720, title: str = "Antigravity Raylib Physics Engine"):
        # Configure OpenGL window flags before initialization (resizable + MSAA 4X anti-aliasing)
        pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE | pr.ConfigFlags.FLAG_MSAA_4X_HINT)
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

    def handle_input(self) -> None:
        # Poll hardware input queue for viewport mode switching or grid toggles
        if pr.is_key_pressed(pr.KeyboardKey.KEY_M):
            self.mode_3d = not self.mode_3d
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_G):
            self.grid.show_grid = not self.grid.show_grid

    def render_hud(self) -> None:
        # Render 2D Heads-Up Display directly over OpenGL frame buffer
        mode_str = "3D PERSPECTIVE" if self.mode_3d else "2D CARTESIAN"
        pr.draw_text(f"ANTIGRAVITY ENGINE [GPU MODE: {mode_str}]", 15, 15, 20, Colors.TEXT)
        pr.draw_text("Controls: [M] Toggle 2D/3D Mode | [G] Toggle Grid | [ESC] Quit", 15, 42, 16, pr.GRAY)
        pr.draw_fps(pr.get_screen_width() - 95, 15)

    def render_frame(self) -> None:
        pr.begin_drawing()
        pr.clear_background(Colors.BACKGROUND)

        if self.mode_3d:
            # Dispatch hardware GPU draw calls inside 3D camera perspective matrix
            pr.begin_mode_3d(self.camera_3d)
            self.grid.draw_3d()

            # Render demonstration 3D rigid body sphere at origin (PHY-20)
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
