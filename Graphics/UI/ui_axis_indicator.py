import pyray as pr
import math
from Graphics.Rendering.render_colors import Colors

class AxisIndicator:
    """UI element that renders an interactive mini 3D coordinate axis triad in the screen corner."""
    def __init__(self):
        self.enabled = True

    def draw(self, camera: pr.Camera3D, screen_width: int, screen_height: int) -> None:
        if not self.enabled:
            return

        # Calculate normalized direction from target to camera
        dx = camera.position.x - camera.target.x
        dy = camera.position.y - camera.target.y
        dz = camera.position.z - camera.target.z
        dist = math.sqrt(dx**2 + dy**2 + dz**2)
        if dist < 0.001:
            return

        mini_pos = pr.Vector3((dx / dist) * 3.2, (dy / dist) * 3.2, (dz / dist) * 3.2)
        mini_cam = pr.Camera3D(
            mini_pos,
            pr.Vector3(0.0, 0.0, 0.0),
            camera.up,
            45.0,
            pr.CameraProjection.CAMERA_PERSPECTIVE
        )

        vp_size = 100
        offset_x = screen_width - vp_size - 20
        offset_y = screen_height - vp_size - 20

        # Project 3D origin and axis tips to 2D mini-viewport coordinates
        o_2d = pr.get_world_to_screen_ex(pr.Vector3(0.0, 0.0, 0.0), mini_cam, vp_size, vp_size)
        axes = [
            ("X", pr.Vector3(0.9, 0.0, 0.0), Colors.AXIS_X),
            ("Y", pr.Vector3(0.0, 0.9, 0.0), Colors.AXIS_Y),
            ("Z", pr.Vector3(0.0, 0.0, 0.9), Colors.AXIS_Z)
        ]

        # Sort axes by distance to mini_cam so foreground axes draw over background axes
        def axis_depth(item):
            tip = item[1]
            return (tip.x - mini_pos.x)**2 + (tip.y - mini_pos.y)**2 + (tip.z - mini_pos.z)**2

        axes.sort(key=axis_depth, reverse=True)

        # Draw background panel circle
        center_pos = pr.Vector2(offset_x + vp_size / 2, offset_y + vp_size / 2)
        pr.draw_circle_v(center_pos, vp_size * 0.45, pr.Color(20, 22, 27, 180))
        pr.draw_circle_lines(int(center_pos.x), int(center_pos.y), float(vp_size * 0.45), Colors.UI_BORDER)

        o_screen = pr.Vector2(offset_x + o_2d.x, offset_y + o_2d.y)
        pr.draw_circle_v(o_screen, 3.0, pr.WHITE)

        for label, tip_3d, color in axes:
            tip_2d = pr.get_world_to_screen_ex(tip_3d, mini_cam, vp_size, vp_size)
            tip_screen = pr.Vector2(offset_x + tip_2d.x, offset_y + tip_2d.y)

            # Draw thick axis line
            pr.draw_line_ex(o_screen, tip_screen, 3.0, color)
            
            # Draw tip dot and label
            pr.draw_circle_v(tip_screen, 8.0, color)
            text_width = pr.measure_text(label, 10)
            pr.draw_text(label, int(tip_screen.x - text_width / 2), int(tip_screen.y - 5), 10, pr.BLACK if label == "Y" else pr.WHITE)
