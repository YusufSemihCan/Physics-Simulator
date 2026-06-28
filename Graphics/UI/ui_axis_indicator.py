import pyray as pr
import math
from typing import List, Tuple
from Graphics.Rendering.render_colors import Colors

# Axis definitions built once at module level — no rebuild per frame
_AXES: List[Tuple[str, pr.Vector3, pr.Color]] = [
    ("X", pr.Vector3(0.9, 0.0, 0.0), Colors.AXIS_X),
    ("Y", pr.Vector3(0.0, 0.9, 0.0), Colors.AXIS_Y),
    ("Z", pr.Vector3(0.0, 0.0, 0.9), Colors.AXIS_Z),
]


class AxisIndicator:
    """UI element that renders an interactive mini 3D coordinate axis triad in the screen corner."""
    def __init__(self):
        self.show = True  # toggled by View dropdown

    def draw(self, camera: pr.Camera3D, screen_width: int, screen_height: int) -> None:
        if not self.show:
            return

        # Normalize direction from target to camera
        dx = camera.position.x - camera.target.x
        dy = camera.position.y - camera.target.y
        dz = camera.position.z - camera.target.z
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dist < 0.001:
            return

        inv_dist = 1.0 / dist
        mini_pos = pr.Vector3(dx * inv_dist * 3.2, dy * inv_dist * 3.2, dz * inv_dist * 3.2)
        mini_cam = pr.Camera3D(
            mini_pos,
            pr.Vector3(0.0, 0.0, 0.0),
            camera.up,
            45.0,
            pr.CameraProjection.CAMERA_PERSPECTIVE
        )

        vp_size = 100
        offset_x = screen_width  - vp_size - 20
        offset_y = screen_height - vp_size - 20

        # Sort axes by depth so foreground axes draw over background ones
        def _depth(item: Tuple[str, pr.Vector3, pr.Color]) -> float:
            t = item[1]
            return (t.x - mini_pos.x) ** 2 + (t.y - mini_pos.y) ** 2 + (t.z - mini_pos.z) ** 2

        sorted_axes = sorted(_AXES, key=_depth, reverse=True)

        # Background circle panel
        cx = offset_x + vp_size // 2
        cy = offset_y + vp_size // 2
        pr.draw_circle(cx, cy, int(vp_size * 0.45), pr.Color(20, 22, 27, 180))
        pr.draw_circle_lines(cx, cy, int(vp_size * 0.45), Colors.UI_BORDER)

        o_2d = pr.get_world_to_screen_ex(pr.Vector3(0.0, 0.0, 0.0), mini_cam, vp_size, vp_size)
        o_screen = pr.Vector2(offset_x + o_2d.x, offset_y + o_2d.y)
        pr.draw_circle_v(o_screen, 3.0, pr.WHITE)

        for label, tip_3d, color in sorted_axes:
            tip_2d = pr.get_world_to_screen_ex(tip_3d, mini_cam, vp_size, vp_size)
            tip_screen = pr.Vector2(offset_x + tip_2d.x, offset_y + tip_2d.y)
            pr.draw_line_ex(o_screen, tip_screen, 3.0, color)
            pr.draw_circle_v(tip_screen, 8.0, color)
            text_w = pr.measure_text(label, 10)
            pr.draw_text(label, int(tip_screen.x - text_w / 2), int(tip_screen.y - 5), 10,
                         pr.BLACK if label == "Y" else pr.WHITE)
