import os
import math
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

    def update_and_draw(self, enabled: bool = True) -> bool:
        mouse_pos = pr.get_mouse_position()
        is_hovered = enabled and pr.check_collision_point_rec(mouse_pos, self.rect)
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


class NodeSelector:
    """An interactive multi-option selector with arrows and clickable nodes that flash options on hover."""
    def __init__(self, x: int, y: int, width: int, label: str, options: list[str], current_index: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.label = label
        self.options = options
        self.current_index = current_index

    def update_and_draw(self) -> tuple[bool, int]:
        changed = False
        mouse_pos = pr.get_mouse_position()
        left_click = pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT)

        # Draw Setting Label on top left
        pr.draw_text(self.label, self.x, self.y, 16, Colors.UI_ACTIVE)

        # Left Arrow `<`
        arrow_w, arrow_h = 36, 28
        ay = self.y + 24
        rect_left = pr.Rectangle(self.x, ay, arrow_w, arrow_h)
        hov_left = pr.check_collision_point_rec(mouse_pos, rect_left)
        if hov_left and left_click:
            self.current_index = (self.current_index - 1) % len(self.options)
            changed = True

        bg_left = Colors.UI_ACTIVE if (hov_left and pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT)) else (Colors.UI_HOVER if hov_left else Colors.GRID_MAJOR)
        pr.draw_rectangle_rounded(rect_left, 0.2, 4, bg_left)
        pr.draw_rectangle_rounded_lines(rect_left, 0.2, 4, Colors.TEXT if hov_left else Colors.UI_BORDER)
        pr.draw_text("<", int(self.x + 13), int(ay + 6), 16, Colors.TEXT)

        # Right Arrow `>`
        rx = self.x + self.width - arrow_w
        rect_right = pr.Rectangle(rx, ay, arrow_w, arrow_h)
        hov_right = pr.check_collision_point_rec(mouse_pos, rect_right)
        if hov_right and left_click:
            self.current_index = (self.current_index + 1) % len(self.options)
            changed = True

        bg_right = Colors.UI_ACTIVE if (hov_right and pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT)) else (Colors.UI_HOVER if hov_right else Colors.GRID_MAJOR)
        pr.draw_rectangle_rounded(rect_right, 0.2, 4, bg_right)
        pr.draw_rectangle_rounded_lines(rect_right, 0.2, 4, Colors.TEXT if hov_right else Colors.UI_BORDER)
        pr.draw_text(">", int(rx + 13), int(ay + 6), 16, Colors.TEXT)

        # Draw Nodes in between
        num_nodes = len(self.options)
        available_w = rx - (self.x + arrow_w)
        spacing = available_w / (num_nodes + 1)

        hovered_node_idx = -1
        for i in range(num_nodes):
            cx = int(self.x + arrow_w + spacing * (i + 1))
            cy = int(ay + arrow_h / 2)
            node_radius = 8.0

            # Check collision with circle area
            dist_sq = (mouse_pos.x - cx)**2 + (mouse_pos.y - cy)**2
            hov_node = dist_sq <= (node_radius + 6)**2
            if hov_node:
                hovered_node_idx = i
                node_radius = 11.0
                if left_click:
                    self.current_index = i
                    changed = True

            is_selected = (i == self.current_index)
            color_node = Colors.UI_ACTIVE if is_selected else (Colors.TEXT if hov_node else Colors.GRID_MINOR)
            pr.draw_circle(cx, cy, node_radius, color_node)
            if is_selected or hov_node:
                pr.draw_circle_lines(cx, cy, node_radius + 3, Colors.UI_ACTIVE if is_selected else Colors.TEXT)

        # Display flashing/highlighted option text aligned to top right
        display_idx = hovered_node_idx if hovered_node_idx != -1 else self.current_index
        option_str = self.options[display_idx]
        text_w = pr.measure_text(option_str, 16)
        text_x = int(self.x + self.width - text_w)
        
        if hovered_node_idx != -1:
            pulse = int((math.sin(pr.get_time() * 15) * 0.4 + 0.6) * 255)
            text_color = pr.Color(255, 255, pulse, 255)
            pr.draw_text(f"► {option_str}", text_x - 18, self.y, 16, text_color)
        else:
            pr.draw_text(option_str, text_x, self.y, 16, Colors.TEXT)

        return changed, self.current_index


class FileTreeSelector:
    """A vertical hierarchical file tree widget allowing direct file browser selection and drag & drop rearrangement."""
    def __init__(self, x: int, y: int, width: int, height: int, root_name: str, options: list[str], current_index: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.root_name = root_name
        self.options = options
        self.current_index = current_index
        self.scroll_offset = 0
        self.dragging_index = -1
        self.drag_move_request = None

    def update_and_draw(self, enabled: bool = True) -> tuple[bool, int]:
        changed = False
        self.drag_move_request = None
        mouse_pos = pr.get_mouse_position()
        left_click = enabled and pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT)
        left_down = enabled and pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT)
        left_released = enabled and pr.is_mouse_button_released(pr.MouseButton.MOUSE_BUTTON_LEFT)

        # Draw tree container frame
        rect = pr.Rectangle(self.x, self.y, self.width, self.height)
        pr.draw_rectangle(self.x, self.y, self.width, self.height, pr.Color(20, 22, 27, 255))
        pr.draw_rectangle_lines(self.x, self.y, self.width, self.height, Colors.GRID_MAJOR)

        # Root folder header
        header_h = 32
        header_rect = pr.Rectangle(self.x, self.y, self.width, header_h)
        is_header_hovered = enabled and pr.check_collision_point_rec(mouse_pos, header_rect)
        if is_header_hovered and left_released and self.dragging_index != -1:
            src_opt = self.options[self.dragging_index]
            self.drag_move_request = (src_opt, "")
            self.dragging_index = -1

        pr.draw_rectangle(self.x, self.y, self.width, header_h, Colors.UI_ACTIVE if (is_header_hovered and self.dragging_index != -1) else Colors.GRID_MINOR)
        pr.draw_text(f"[DIR] {self.root_name}/ (Drop here for root)", self.x + 12, self.y + 8, 16, Colors.UI_PANEL if (is_header_hovered and self.dragging_index != -1) else Colors.UI_ACTIVE)
        pr.draw_line(self.x, self.y + header_h, self.x + self.width, self.y + header_h, Colors.GRID_MAJOR)

        # Handle wheel scrolling if hovered
        if enabled and pr.check_collision_point_rec(mouse_pos, rect):
            wheel = pr.get_mouse_wheel_move()
            if wheel != 0:
                self.scroll_offset = max(0, min(max(0, len(self.options) - 10), int(self.scroll_offset - wheel)))

        # Draw file items
        item_h = 28
        start_y = self.y + header_h + 6
        max_visible = max(1, (self.height - header_h - 10) // item_h)

        for i in range(self.scroll_offset, min(len(self.options), self.scroll_offset + max_visible)):
            item_y = start_y + (i - self.scroll_offset) * item_h
            item_rect = pr.Rectangle(self.x + 4, item_y, self.width - 8, item_h)
            is_hovered = enabled and pr.check_collision_point_rec(mouse_pos, item_rect)

            if is_hovered:
                if left_click:
                    self.current_index = i
                    self.dragging_index = i
                    changed = True
                elif left_released and self.dragging_index != -1 and self.dragging_index != i:
                    src_opt = self.options[self.dragging_index]
                    target_opt = self.options[i]
                    full_target = os.path.join(self.root_name, target_opt)
                    is_target_dir = os.path.isdir(full_target) or any(o.replace("\\", "/").startswith(target_opt.replace("\\", "/") + "/") for o in self.options)
                    dest_folder = target_opt if is_target_dir else os.path.dirname(target_opt).replace("\\", "/")
                    self.drag_move_request = (src_opt, dest_folder)
                    self.dragging_index = -1

            is_selected = (i == self.current_index)
            if is_selected:
                pr.draw_rectangle_rounded(item_rect, 0.1, 4, Colors.UI_ACTIVE)
            elif is_hovered:
                pr.draw_rectangle_rounded(item_rect, 0.1, 4, Colors.GRID_MINOR)

            opt = self.options[i]
            parts = opt.replace("\\", "/").split("/")
            depth = len(parts) - 1
            basename = parts[-1]

            full_path = os.path.join(self.root_name, opt)
            is_dir = os.path.isdir(full_path) or any(o.replace("\\", "/").startswith(opt.replace("\\", "/") + "/") for o in self.options)

            parent_prefix = "/".join(parts[:-1])
            is_last_sibling = True
            for j in range(i + 1, len(self.options)):
                next_parts = self.options[j].replace("\\", "/").split("/")
                next_parent = "/".join(next_parts[:-1])
                if len(next_parts) - 1 == depth and next_parent == parent_prefix:
                    is_last_sibling = False
                    break
                if len(next_parts) - 1 < depth:
                    break

            branch = "\\--" if is_last_sibling else "|--"
            icon = "[DIR]" if is_dir else " * "
            label = f"{basename}/" if is_dir else f"{basename}.json"

            text_color = pr.Color(20, 22, 27, 255) if is_selected else Colors.TEXT
            indent_x = int(self.x + 16 + (depth * 20))
            pr.draw_text(f"{branch} {icon} {label}", indent_x, int(item_y + 6), 15, text_color)

        if self.dragging_index != -1 and enabled and left_down:
            drag_txt = f"[Dragging]: {self.options[self.dragging_index]}"
            dw = pr.measure_text(drag_txt, 14) + 20
            pr.draw_rectangle(int(mouse_pos.x) + 12, int(mouse_pos.y) + 12, dw, 26, pr.Color(40, 44, 52, 230))
            pr.draw_rectangle_lines(int(mouse_pos.x) + 12, int(mouse_pos.y) + 12, dw, 26, Colors.UI_ACTIVE)
            pr.draw_text(drag_txt, int(mouse_pos.x) + 22, int(mouse_pos.y) + 18, 14, pr.WHITE)

        if not left_down:
            self.dragging_index = -1

        return changed, self.current_index

