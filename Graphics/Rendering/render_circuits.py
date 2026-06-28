import pyray as pr
import math
from Graphics.Rendering.render_colors import Colors
from Simulation.sim_circuits import CircuitSolver
from Graphics.Rendering.render_fields import _draw_scrolling_grid

class CircuitRenderer:
    """Renders DC circuit components, animated electron current flow, glowing bulbs, and supports interactive wire dragging."""
    def __init__(self):
        self.scale = 40.0
        self.wiring_start_node = None
        self.active_comp_type = 'wire'

    def handle_input(self, scene, sw: int, sh: int, pan_x: float = 0.0, pan_y: float = 0.0, is_over_ui: bool = False) -> None:
        if not scene or is_over_ui:
            return
        cx = int(sw // 2 + pan_x)
        cy = int(sh // 2 + pan_y)
        mouse_pos = pr.get_mouse_position()

        # Snap to grid of 0.5 units
        gx = round((mouse_pos.x - cx) / self.scale * 2.0) / 2.0
        gy = round((cy - mouse_pos.y) / self.scale * 2.0) / 2.0

        if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT):
            self.wiring_start_node = scene.add_node(gx, gy)

        if pr.is_mouse_button_released(pr.MouseButton.MOUSE_BUTTON_LEFT) and self.wiring_start_node:
            end_node = scene.add_node(gx, gy)
            if end_node != self.wiring_start_node and math.hypot(end_node.x - self.wiring_start_node.x, end_node.y - self.wiring_start_node.y) > 0.1:
                val = 9.0 if self.active_comp_type == 'battery' else 10.0
                scene.add_component(self.active_comp_type, self.wiring_start_node, end_node, val)
                CircuitSolver.step(scene)
            self.wiring_start_node = None

    def draw(self, scene, sw: int, sh: int, dt: float = 0.0, pan_x: float = 0.0, pan_y: float = 0.0) -> None:
        if not scene:
            return

        cx = int(sw // 2 + pan_x)
        cy = int(sh // 2 + pan_y)
        time_sec = pr.get_time()

        _draw_scrolling_grid(cx, cy, sw, sh, self.scale)

        # Draw components and wires
        for comp in scene.components:
            n1 = comp.node_a
            n2 = comp.node_b
            x1, y1 = cx + int(n1.x * self.scale), cy - int(n1.y * self.scale)
            x2, y2 = cx + int(n2.x * self.scale), cy - int(n2.y * self.scale)

            # Draw wire connection base
            wire_color = pr.Color(100, 181, 246, 255) if abs(comp.current) > 0.01 else pr.GRAY
            pr.draw_line_ex(pr.Vector2(x1, y1), pr.Vector2(x2, y2), 4.0, wire_color)

            # Draw animated electron particles along current direction
            if abs(comp.current) > 0.005:
                num_dots = 4
                direction = 1.0 if comp.current > 0 else -1.0
                speed = min(5.0, abs(comp.current) * 2.0)
                for k in range(num_dots):
                    progress = (time_sec * speed * direction + k / float(num_dots)) % 1.0
                    px = int(x1 + progress * (x2 - x1))
                    py = int(y1 + progress * (y2 - y1))
                    pr.draw_circle(px, py, 4, pr.YELLOW)

            # Draw component icon at midpoint
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            if comp.comp_type == 'battery':
                pr.draw_rectangle(mx - 18, my - 12, 36, 24, pr.Color(229, 115, 115, 255))
                pr.draw_rectangle_lines(mx - 18, my - 12, 36, 24, pr.WHITE)
                pr.draw_text(f"{comp.val:.0f}V", mx - 10, my - 7, 14, pr.WHITE)
            elif comp.comp_type == 'resistor':
                pr.draw_rectangle(mx - 20, my - 10, 40, 20, pr.Color(255, 183, 77, 255))
                pr.draw_rectangle_lines(mx - 20, my - 10, 40, 20, pr.WHITE)
                pr.draw_text(f"{comp.val:.0f} ohm", mx - 18, my - 6, 12, pr.BLACK)
            elif comp.comp_type == 'switch':
                pr.draw_circle(mx, my, 8, pr.GREEN if comp.state else pr.RED)
                state_str = "CLOSED" if comp.state else "OPEN"
                pr.draw_text(state_str, mx - 15, my - 22, 12, pr.WHITE)
            elif comp.comp_type == 'bulb':
                # Glow effect based on current
                glow = min(255, int(abs(comp.current) * 400))
                if glow > 20:
                    pr.draw_circle(mx, my, 28, pr.Color(255, 255, 0, min(120, glow // 2)))
                    pr.draw_circle(mx, my, 20, pr.Color(255, 255, 100, min(200, glow)))
                pr.draw_circle(mx, my, 14, pr.Color(255, 235, 59, 255) if glow > 50 else pr.DARKGRAY)
                pr.draw_circle_lines(mx, my, 14, pr.WHITE)

        # Draw nodes with voltage labels
        for n in scene.nodes:
            nx, ny = cx + int(n.x * self.scale), cy - int(n.y * self.scale)
            pr.draw_circle(nx, ny, 6, pr.WHITE)
            pr.draw_text(f"{n.voltage:.1f}V", nx + 8, ny - 14, 12, pr.SKYBLUE)

        # Interactive wire dragging preview
        if self.wiring_start_node and pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT):
            nx = cx + int(self.wiring_start_node.x * self.scale)
            ny = cy - int(self.wiring_start_node.y * self.scale)
            m_pos = pr.get_mouse_position()
            pr.draw_line_ex(pr.Vector2(nx, ny), m_pos, 3.0, pr.Color(100, 255, 100, 200))
            pr.draw_text(f"+ Adding {self.active_comp_type.upper()}", int(m_pos.x) + 15, int(m_pos.y) - 10, 14, pr.GREEN)
