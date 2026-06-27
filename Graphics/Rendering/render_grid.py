import pyray as pr
from graphics.rendering.render_colors import Colors

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
