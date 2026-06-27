from typing import Callable, Optional
import pyray as pr
from Graphics.Rendering.render_colors import Colors

class Panel:
    """A glassmorphism-inspired semi-transparent container panel for UI elements."""
    def __init__(self, x: int, y: int, width: int, height: int, title: str = ""):
        self.rect = pr.Rectangle(x, y, width, height)
        self.title = title

    def draw(self) -> None:
        # Draw semi-transparent rounded background panel
        pr.draw_rectangle_rounded(self.rect, 0.1, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(self.rect, 0.1, 8, Colors.UI_BORDER)
        if self.title:
            pr.draw_text(self.title, int(self.rect.x) + 15, int(self.rect.y) + 12, 18, Colors.TEXT)
            pr.draw_line(int(self.rect.x) + 15, int(self.rect.y) + 38, int(self.rect.x + self.rect.width) - 15, int(self.rect.y) + 38, Colors.UI_BORDER)


class Button:
    """An interactive clickable button with dynamic hover states."""
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pr.Rectangle(x, y, width, height)
        self.text = text

    def update_and_draw(self) -> bool:
        mouse_pos = pr.get_mouse_position()
        is_hovered = pr.check_collision_point_rec(mouse_pos, self.rect)
        clicked = is_hovered and pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT)

        # Dynamic visual hover styling
        bg_color = Colors.UI_ACTIVE if clicked else (Colors.UI_HOVER if is_hovered else Colors.GRID_MAJOR)
        border_color = Colors.TEXT if is_hovered else Colors.UI_BORDER

        pr.draw_rectangle_rounded(self.rect, 0.2, 8, bg_color)
        pr.draw_rectangle_rounded_lines(self.rect, 0.2, 8, border_color)

        # Center text horizontally and vertically
        text_width = pr.measure_text(self.text, 16)
        text_x = int(self.rect.x + (self.rect.width - text_width) / 2)
        text_y = int(self.rect.y + (self.rect.height - 16) / 2)
        pr.draw_text(self.text, text_x, text_y, 16, Colors.TEXT)

        return clicked


class Slider:
    """An interactive numerical slider for tuning simulation physics parameters in real-time."""
    def __init__(self, x: int, y: int, width: int, height: int, label: str, min_val: float, max_val: float, initial_val: float):
        self.rect = pr.Rectangle(x, y, width, height)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False

    def update_and_draw(self) -> float:
        mouse_pos = pr.get_mouse_position()
        is_hovered = pr.check_collision_point_rec(mouse_pos, self.rect)

        if is_hovered and pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT):
            self.dragging = True
        if pr.is_mouse_button_released(pr.MouseButton.MOUSE_BUTTON_LEFT):
            self.dragging = False

        if self.dragging:
            # Calculate interpolation factor along track width
            ratio = (mouse_pos.x - self.rect.x) / self.rect.width
            ratio = max(0.0, min(1.0, ratio))
            self.value = self.min_val + ratio * (self.max_val - self.min_val)

        # Draw label and value readout above slider track
        val_str = f"{self.value:.2f}"
        pr.draw_text(self.label, int(self.rect.x), int(self.rect.y) - 18, 14, Colors.TEXT)
        pr.draw_text(val_str, int(self.rect.x + self.rect.width) - pr.measure_text(val_str, 14), int(self.rect.y) - 18, 14, Colors.UI_ACTIVE)

        # Draw track background
        pr.draw_rectangle_rounded(self.rect, 0.5, 8, Colors.GRID_MINOR)
        
        # Draw filled progress bar
        fill_width = int(((self.value - self.min_val) / (self.max_val - self.min_val)) * self.rect.width)
        fill_rect = pr.Rectangle(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pr.draw_rectangle_rounded(fill_rect, 0.5, 8, Colors.UI_ACTIVE)

        # Draw thumb handle
        thumb_x = int(self.rect.x + fill_width)
        thumb_y = int(self.rect.y + self.rect.height / 2)
        pr.draw_circle(thumb_x, thumb_y, int(self.rect.height * 0.8), Colors.TEXT if (is_hovered or self.dragging) else Colors.UI_BORDER)

        return self.value


class Toggle:
    """An interactive boolean switch / checkbox for toggling educational overlays."""
    def __init__(self, x: int, y: int, size: int, label: str, initial_state: bool = True):
        self.rect = pr.Rectangle(x, y, size, size)
        self.label = label
        self.state = initial_state

    def update_and_draw(self) -> bool:
        mouse_pos = pr.get_mouse_position()
        is_hovered = pr.check_collision_point_rec(mouse_pos, self.rect)

        if is_hovered and pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT):
            self.state = not self.state

        # Draw checkbox background
        bg_color = Colors.UI_ACTIVE if self.state else Colors.GRID_MINOR
        pr.draw_rectangle_rounded(self.rect, 0.2, 4, bg_color)
        pr.draw_rectangle_rounded_lines(self.rect, 0.2, 4, Colors.TEXT if is_hovered else Colors.UI_BORDER)

        # Draw checkmark inside if active
        if self.state:
            center_x, center_y = int(self.rect.x + self.rect.width / 2), int(self.rect.y + self.rect.height / 2)
            pr.draw_circle(center_x, center_y, int(self.rect.width * 0.3), Colors.TEXT)

        # Draw label next to box
        pr.draw_text(self.label, int(self.rect.x + self.rect.width) + 10, int(self.rect.y + (self.rect.height - 14) / 2), 14, Colors.TEXT)

        return self.state
