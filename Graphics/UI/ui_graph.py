import pyray as pr
import math
from typing import List
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button

class GraphRenderer:
    """Renders real-time kinematics inspection data and dynamic time-series graphing curves."""
    def __init__(self, app):
        self.app = app
        self.max_points = 300 # 5 seconds at 60 FPS
        self.history_h: List[float] = []
        self.history_v: List[float] = []
        self.history_ke: List[float] = []
        self.history_pe: List[float] = []
        self.history_tot: List[float] = []

        self.active_tab = "e" # 'h' (Height), 'v' (Velocity), 'e' (Energy)
        self.btn_h = Button(0, 0, 90, 24, "Height")
        self.btn_v = Button(0, 0, 90, 24, "Velocity")
        self.btn_e = Button(0, 0, 95, 24, "Energy")

    def clear(self) -> None:
        self.history_h.clear()
        self.history_v.clear()
        self.history_ke.clear()
        self.history_pe.clear()
        self.history_tot.clear()

    def add_sample(self, shape, gravity: float) -> None:
        if not shape:
            return
        h_val = shape.pos.y if not math.isnan(shape.pos.y) and not math.isinf(shape.pos.y) else 0.0
        v_val = shape.vel.y if not math.isnan(shape.vel.y) and not math.isinf(shape.vel.y) else 0.0
        ke_val = shape.kinetic_energy()
        pe_val = shape.potential_energy(gravity)
        tot_val = shape.total_energy(gravity)

        if math.isnan(ke_val) or math.isinf(ke_val): ke_val = 0.0
        if math.isnan(pe_val) or math.isinf(pe_val): pe_val = 0.0
        if math.isnan(tot_val) or math.isinf(tot_val): tot_val = 0.0

        self.history_h.append(h_val)
        self.history_v.append(v_val)
        self.history_ke.append(ke_val)
        self.history_pe.append(pe_val)
        self.history_tot.append(tot_val)

        if len(self.history_h) > self.max_points:
            self.history_h.pop(0)
            self.history_v.pop(0)
            self.history_ke.pop(0)
            self.history_pe.pop(0)
            self.history_tot.pop(0)

    def draw_polyline(self, data: List[float], rect: pr.Rectangle, min_val: float, max_val: float, color: pr.Color) -> None:
        if len(data) < 2:
            return
        span = max(0.001, max_val - min_val)
        step_x = rect.width / max(1, self.max_points - 1)

        for i in range(len(data) - 1):
            x1 = rect.x + i * step_x
            y1 = rect.y + rect.height - ((data[i] - min_val) / span) * rect.height
            x2 = rect.x + (i + 1) * step_x
            y2 = rect.y + rect.height - ((data[i + 1] - min_val) / span) * rect.height
            pr.draw_line_ex(pr.Vector2(x1, y1), pr.Vector2(x2, y2), 2.0, color)

    def draw(self, shape, gravity: float) -> None:
        if not shape:
            return

        sw = pr.get_screen_width()
        panel_w, panel_h = 320, 560
        px = sw - panel_w - 15
        py = 60

        # Background panel
        pr.draw_rectangle_rounded(pr.Rectangle(px, py, panel_w, panel_h), 0.08, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(pr.Rectangle(px, py, panel_w, panel_h), 0.08, 8, Colors.UI_BORDER)

        # 1. OBJECT INSPECTOR HEADER
        pr.draw_text("OBJECT INSPECTOR", px + 15, py + 15, 18, Colors.UI_ACTIVE)
        pr.draw_line(px + 15, py + 38, px + panel_w - 15, py + 38, Colors.UI_BORDER)

        pr.draw_text(f"ID: {shape.shape_id} ({shape.shape_type.upper()})", px + 15, py + 48, 15, pr.WHITE)
        pr.draw_text(f"Mass: {shape.mass:.2f} kg | Restitution: {shape.restitution:.2f}", px + 15, py + 68, 14, pr.LIGHTGRAY)
        
        pos_str = f"X:{shape.pos.x:.1f}  Y:{shape.pos.y:.1f}  Z:{shape.pos.z:.1f}"
        vel_str = f"Vx:{shape.vel.x:.1f} Vy:{shape.vel.y:.1f} Vz:{shape.vel.z:.1f}"
        pr.draw_text(f"Pos (m):   {pos_str}", px + 15, py + 95, 14, pr.SKYBLUE)
        pr.draw_text(f"Vel (m/s): {vel_str}", px + 15, py + 115, 14, Colors.VECTOR_VELOCITY)
        pr.draw_text(f"Speed:     {shape.speed:.2f} m/s", px + 15, py + 135, 14, Colors.VECTOR_ACCEL)

        ke = shape.kinetic_energy()
        pe = shape.potential_energy(gravity)
        tot = shape.total_energy(gravity)
        pr.draw_text(f"KE: {ke:.1f} J | PE: {pe:.1f} J | Tot: {tot:.1f} J", px + 15, py + 160, 14, pr.Color(255, 183, 77, 255))

        # 2. REAL-TIME GRAPHING OVERLAY
        pr.draw_line(px + 15, py + 190, px + panel_w - 15, py + 190, Colors.UI_BORDER)
        pr.draw_text("REAL-TIME KINEMATICS GRAPH", px + 15, py + 202, 16, Colors.UI_ACTIVE)

        # Position tabs
        self.btn_h.rect.x, self.btn_h.rect.y = px + 15, py + 228
        self.btn_v.rect.x, self.btn_v.rect.y = px + 112, py + 228
        self.btn_e.rect.x, self.btn_e.rect.y = px + 210, py + 228

        if self.btn_h.update_and_draw():
            self.active_tab = "h"
        if self.btn_v.update_and_draw():
            self.active_tab = "v"
        if self.btn_e.update_and_draw():
            self.active_tab = "e"

        # Highlight active tab indicator
        tx = px + 15 if self.active_tab == "h" else (px + 112 if self.active_tab == "v" else px + 210)
        tw = 90 if self.active_tab != "e" else 95
        pr.draw_rectangle_lines(int(tx), py + 228, tw, 24, Colors.UI_ACTIVE)

        # Graph drawing box
        gx, gy, gw, gh = px + 15, py + 265, panel_w - 30, 240
        g_rect = pr.Rectangle(gx, gy, gw, gh)
        pr.draw_rectangle(gx, gy, gw, gh, pr.Color(15, 18, 22, 255))
        pr.draw_rectangle_lines(gx, gy, gw, gh, pr.DARKGRAY)

        # Draw baseline grid
        for i in range(1, 4):
            ly = gy + int(i * gh / 4)
            pr.draw_line(gx, ly, gx + gw, ly, pr.Color(40, 45, 55, 255))

        match self.active_tab:
            case "h":
                self._draw_height_tab(shape, g_rect, gx, gy, gh)
            case "v":
                self._draw_velocity_tab(shape, g_rect, gx, gy, gw, gh)
            case "e":
                self._draw_energy_tab(g_rect, gx, gy, gw, gh, ke, pe, tot)

        pr.draw_text("Left Click another object to inspect | Click empty space to deselect", px + 12, py + 520, 11, pr.DARKGRAY)

    def _draw_height_tab(self, shape, g_rect: pr.Rectangle, gx: int, gy: int, gh: int) -> None:
        data = self.history_h if self.history_h else [shape.pos.y]
        min_v, max_v = min(0.0, min(data)), max(10.0, max(data) * 1.1)
        self.draw_polyline(data, g_rect, min_v, max_v, pr.SKYBLUE)
        pr.draw_text(f"Max Height: {max_v:.1f} m", gx + 8, gy + 8, 12, pr.SKYBLUE)
        pr.draw_text(f"Min: {min_v:.1f} m", gx + 8, gy + gh - 20, 12, pr.GRAY)

    def _draw_velocity_tab(self, shape, g_rect: pr.Rectangle, gx: int, gy: int, gw: int, gh: int) -> None:
        data = self.history_v if self.history_v else [shape.vel.y]
        abs_m = max(10.0, max(abs(v) for v in data) * 1.1)
        min_v, max_v = -abs_m, abs_m
        mid_y = gy + gh // 2
        pr.draw_line(gx, mid_y, gx + gw, mid_y, pr.GRAY)
        self.draw_polyline(data, g_rect, min_v, max_v, Colors.VECTOR_VELOCITY)
        pr.draw_text(f"+V max: {max_v:.1f} m/s", gx + 8, gy + 8, 12, Colors.VECTOR_VELOCITY)
        pr.draw_text(f"-V min: {min_v:.1f} m/s", gx + 8, gy + gh - 20, 12, Colors.VECTOR_VELOCITY)

    def _draw_energy_tab(self, g_rect: pr.Rectangle, gx: int, gy: int, gw: int, gh: int, ke: float, pe: float, tot: float) -> None:
        d_ke = self.history_ke if self.history_ke else [ke]
        d_pe = self.history_pe if self.history_pe else [pe]
        d_tot = self.history_tot if self.history_tot else [tot]
        max_v = max(50.0, max(d_tot) * 1.1)
        
        self.draw_polyline(d_pe, g_rect, 0.0, max_v, pr.Color(129, 199, 132, 255))
        self.draw_polyline(d_ke, g_rect, 0.0, max_v, pr.Color(255, 183, 77, 255))
        self.draw_polyline(d_tot, g_rect, 0.0, max_v, pr.WHITE)

        pr.draw_text("Total Energy (White)", gx + 8, gy + 8, 12, pr.WHITE)
        pr.draw_text("Potential Energy (Green)", gx + 8, gy + 24, 12, pr.Color(129, 199, 132, 255))
        pr.draw_text("Kinetic Energy (Orange)", gx + 8, gy + 40, 12, pr.Color(255, 183, 77, 255))
        pr.draw_text(f"Scale Max: {max_v:.0f} J", gx + gw - 110, gy + gh - 20, 12, pr.LIGHTGRAY)
