import pyray as pr
import math
from Graphics.Rendering.render_colors import Colors
from Simulation.sim_fields import FieldCalculator

# Pre-built colors shared across all field grid samples
_GRID_LINE  = pr.Color(30,  35,  45,  100)
_AXIS_LINE  = pr.Color(100, 100, 110, 150)
_POS_CHARGE = pr.Color(229, 115, 115, 255)
_NEG_CHARGE = pr.Color(100, 181, 246, 255)


def _draw_scrolling_grid(cx: int, cy: int, sw: int, sh: int, scale: float) -> None:
    """Draws the shared infinite-scrolling grid used by 2D simulation modes."""
    int_scale = int(scale)
    for lx in range(int(cx % scale), sw, int_scale):
        pr.draw_line(lx, 0, lx, sh, _GRID_LINE)
    for ly in range(int(cy % scale), sh, int_scale):
        pr.draw_line(0, ly, sw, ly, _GRID_LINE)
    if 0 <= cx <= sw:
        pr.draw_line(cx, 0, cx, sh, _AXIS_LINE)
    if 0 <= cy <= sh:
        pr.draw_line(0, cy, sw, cy, _AXIS_LINE)


class FieldsRenderer:
    """Renders vector field arrows and point charge / magnet sources."""
    def __init__(self):
        self.scale = 40.0
        self.grid_step = 35

    def draw(self, scene, sw: int, sh: int, dt: float = 0.0,
             pan_x: float = 0.0, pan_y: float = 0.0) -> None:
        if not scene:
            return

        cx = int(sw // 2 + pan_x)
        cy = int(sh // 2 + pan_y)
        _draw_scrolling_grid(cx, cy, sw, sh, self.scale)

        # Sample and draw the vector field on a coarse grid
        half_step = self.grid_step // 2
        for sx in range(half_step, sw, self.grid_step):
            for sy in range(half_step, sh, self.grid_step):
                gx = (sx - cx) / self.scale
                gy = (cy - sy) / self.scale
                vx, vy, mag = FieldCalculator.calculate_vector_at(scene, gx, gy)

                if mag > 0.05:
                    angle = math.atan2(-vy, vx)
                    arrow_len = min(14.0, mag * 5.0 + 6.0)
                    ex = sx + math.cos(angle) * arrow_len
                    ey = sy + math.sin(angle) * arrow_len

                    # Compute color once — not once per draw call
                    intensity = min(1.0, mag / 5.0)
                    color = pr.Color(int(255 * intensity), int(100 * (1.0 - intensity)), int(255 * (1.0 - intensity)), 180)
                    pr.draw_line_ex(pr.Vector2(sx, sy), pr.Vector2(ex, ey), 2.0, color)
                    pr.draw_circle(int(ex), int(ey), 2, color)

        # Draw field sources
        for s in scene.sources:
            sx = cx + int(s.x * self.scale)
            sy = cy - int(s.y * self.scale)
            if s.source_type == 'charge':
                color = _POS_CHARGE if s.val > 0 else _NEG_CHARGE
                pr.draw_circle(sx, sy, 18, color)
                pr.draw_circle_lines(sx, sy, 18, pr.WHITE)
                pr.draw_text("+" if s.val > 0 else "-", sx - 5, sy - 10, 20, pr.WHITE)
