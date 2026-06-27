import pyray as pr
import math
from Simulation.sim_fields import FieldCalculator

class FieldsRenderer:
    """Renders vector field arrows and point charge visualizers."""
    def __init__(self):
        self.scale = 40.0
        self.grid_step = 35

    def draw(self, scene, sw: int, sh: int, dt: float = 0.0, pan_x: float = 0.0, pan_y: float = 0.0) -> None:
        if not scene:
            return

        cx = int(sw // 2 + pan_x)
        cy = int(sh // 2 + pan_y)

        # Draw infinite scrolling grid background
        start_x = int(cx % self.scale)
        for lx in range(start_x, sw, int(self.scale)):
            pr.draw_line(lx, 0, lx, sh, pr.Color(30, 35, 45, 100))
        start_y = int(cy % self.scale)
        for ly in range(start_y, sh, int(self.scale)):
            pr.draw_line(0, ly, sw, ly, pr.Color(30, 35, 45, 100))

        # Draw origin axes
        if 0 <= cx <= sw:
            pr.draw_line(cx, 0, cx, sh, pr.Color(100, 100, 110, 150))
        if 0 <= cy <= sh:
            pr.draw_line(0, cy, sw, cy, pr.Color(100, 100, 110, 150))

        # Sample vector field grid
        for sx in range(self.grid_step // 2, sw, self.grid_step):
            for sy in range(self.grid_step // 2, sh, self.grid_step):
                gx = (sx - cx) / self.scale
                gy = (cy - sy) / self.scale
                vx, vy, mag = FieldCalculator.calculate_vector_at(scene, gx, gy)

                if mag > 0.05:
                    angle = math.atan2(-vy, vx) # Invert Y for screen space
                    arrow_len = min(14.0, mag * 5.0 + 6.0)
                    ex = sx + math.cos(angle) * arrow_len
                    ey = sy + math.sin(angle) * arrow_len

                    # Color intensity
                    intensity = min(1.0, mag / 5.0)
                    r = int(255 * intensity)
                    g = int(100 * (1.0 - intensity))
                    b = int(255 * (1.0 - intensity))
                    color = pr.Color(r, g, b, 180)

                    pr.draw_line_ex(pr.Vector2(sx, sy), pr.Vector2(ex, ey), 2.0, color)
                    pr.draw_circle(int(ex), int(ey), 2, color)

        # Draw sources
        for s in scene.sources:
            sx = cx + int(s.x * self.scale)
            sy = cy - int(s.y * self.scale)
            if s.source_type == 'charge':
                is_pos = s.val > 0
                color = pr.Color(229, 115, 115, 255) if is_pos else pr.Color(100, 181, 246, 255)
                pr.draw_circle(sx, sy, 18, color)
                pr.draw_circle_lines(sx, sy, 18, pr.WHITE)
                symbol = "+" if is_pos else "-"
                pr.draw_text(symbol, sx - 5, sy - 10, 20, pr.WHITE)
