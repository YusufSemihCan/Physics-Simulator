import pyray as pr
import math
from Simulation.sim_optics import OpticsSolver
from Graphics.Rendering.render_fields import _draw_scrolling_grid

class OpticsRenderer:
    """Renders laser beams, mirrors, and glass refraction lenses."""
    def __init__(self):
        self.scale = 40.0

    def draw(self, scene, sw: int, sh: int, dt: float = 0.0, pan_x: float = 0.0, pan_y: float = 0.0) -> None:
        if not scene:
            return

        cx = int(sw // 2 + pan_x)
        cy = int(sh // 2 + pan_y)

        _draw_scrolling_grid(cx, cy, sw, sh, self.scale)

        # Draw optical elements
        for el in scene.elements:
            match el.elem_type:
                case 'mirror':
                    m_rad = math.radians(el.param1)
                    half_l = el.param2 / 2.0
                    mx = math.cos(m_rad) * half_l
                    my = math.sin(m_rad) * half_l
                    x1, y1 = cx + int((el.x - mx) * self.scale), cy - int((el.y - my) * self.scale)
                    x2, y2 = cx + int((el.x + mx) * self.scale), cy - int((el.y + my) * self.scale)
                    pr.draw_line_ex(pr.Vector2(x1, y1), pr.Vector2(x2, y2), 5.0, pr.Color(200, 230, 255, 255))
                case 'lens':
                    half_h = el.param2 / 2.0
                    x1, y1 = cx + int(el.x * self.scale), cy - int((el.y - half_h) * self.scale)
                    x2, y2 = cx + int(el.x * self.scale), cy - int((el.y + half_h) * self.scale)
                    pr.draw_line_ex(pr.Vector2(x1, y1), pr.Vector2(x2, y2), 8.0, pr.Color(100, 181, 246, 180))
                    pr.draw_circle(x1, (y1 + y2) // 2, 6, pr.Color(100, 181, 246, 255))

        # Draw laser emitters
        for em in scene.emitters:
            ex, ey = cx + int(em.x * self.scale), cy - int(em.y * self.scale)
            pr.draw_rectangle(ex - 12, ey - 12, 24, 24, pr.Color(229, 115, 115, 255))
            pr.draw_rectangle_lines(ex - 12, ey - 12, 24, 24, pr.WHITE)

        # Trace and draw laser rays
        rays = OpticsSolver.trace_rays(scene)
        for r in rays:
            rx1, ry1 = cx + int(r.x1 * self.scale), cy - int(r.y1 * self.scale)
            rx2, ry2 = cx + int(r.x2 * self.scale), cy - int(r.y2 * self.scale)
            alpha = max(40, min(255, int(r.intensity * 255)))
            # Outer glow
            pr.draw_line_ex(pr.Vector2(rx1, ry1), pr.Vector2(rx2, ry2), 6.0, pr.Color(255, 50, 50, alpha // 3))
            # Core beam
            pr.draw_line_ex(pr.Vector2(rx1, ry1), pr.Vector2(rx2, ry2), 2.5, pr.Color(255, 100, 100, alpha))
