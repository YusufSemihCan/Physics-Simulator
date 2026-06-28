import pyray as pr
import math
from Graphics.Rendering.render_colors import Colors

class VectorRenderer:
    """Renders 3D and 2D vector arrows showing physical quantities like velocity and force."""
    def __init__(self):
        self.enabled = True
        self.scale = 1.0

    def draw_vector_3d(self, start: pr.Vector3, vec: pr.Vector3, color: pr.Color) -> None:
        if not self.enabled:
            return
            
        scaled_vec = pr.Vector3(vec.x * self.scale, vec.y * self.scale, vec.z * self.scale)
        length = math.sqrt(scaled_vec.x**2 + scaled_vec.y**2 + scaled_vec.z**2)
        if length < 0.05:
            return

        end = pr.Vector3(start.x + scaled_vec.x, start.y + scaled_vec.y, start.z + scaled_vec.z)
        
        # Calculate transition point between cylinder stem (80%) and cone arrowhead (20%)
        head_ratio = min(0.3, 0.4 / length) # Head is at most 30% of arrow or 0.4 units
        stem_end = pr.Vector3(
            end.x - scaled_vec.x * head_ratio,
            end.y - scaled_vec.y * head_ratio,
            end.z - scaled_vec.z * head_ratio
        )
        
        stem_radius = max(0.02, min(0.06, length * 0.03))
        head_radius = stem_radius * 2.8
        
        # Draw hardware GPU cylinder stem and cone tip
        pr.draw_cylinder_ex(start, stem_end, stem_radius, stem_radius, 8, color)
        pr.draw_cylinder_ex(stem_end, end, head_radius, 0.0, 8, color)

    def draw_vector_2d(self, start_x: float, start_y: float, vec_x: float, vec_y: float, color: pr.Color) -> None:
        if not self.enabled:
            return
            
        vx = vec_x * self.scale
        vy = vec_y * self.scale
        length = math.sqrt(vx**2 + vy**2)
        if length < 2.0:
            return

        end_x = start_x + vx
        end_y = start_y + vy
        
        # Draw main stem line
        pr.draw_line_ex(pr.Vector2(start_x, start_y), pr.Vector2(end_x, end_y), 3.0, color)
        
        # Calculate arrowhead lines
        angle = math.atan2(vy, vx)
        head_len = min(15.0, length * 0.3)
        angle1 = angle + math.radians(145)
        angle2 = angle - math.radians(145)
        
        h1_x = end_x + head_len * math.cos(angle1)
        h1_y = end_y + head_len * math.sin(angle1)
        h2_x = end_x + head_len * math.cos(angle2)
        h2_y = end_y + head_len * math.sin(angle2)
        
        pr.draw_triangle(
            pr.Vector2(end_x, end_y),
            pr.Vector2(h1_x, h1_y),
            pr.Vector2(h2_x, h2_y),
            color
        )
