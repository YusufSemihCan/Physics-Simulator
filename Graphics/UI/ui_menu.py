from enum import Enum
import pyray as pr
from graphics.rendering.render_colors import Colors
from graphics.ui.ui_elements import Button

class AppScreen(Enum):
    MAIN_MENU = 1
    SETTINGS = 2
    SIMULATION = 3
    QUIT = 4

class MainMenuScreen:
    """The landing screen where users choose to start the simulation, configure settings, or exit."""
    def __init__(self):
        self.btn_start = Button(0, 0, 260, 45, "Start Simulation")
        self.btn_settings = Button(0, 0, 260, 45, "Settings")
        self.btn_quit = Button(0, 0, 260, 45, "Quit Application")

    def update_and_draw(self) -> AppScreen:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()

        # Dynamic centering calculation
        panel_w, panel_h = 420, 340
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2

        # Draw semi-transparent glassmorphism menu panel
        pr.draw_rectangle_rounded(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, 2, Colors.UI_BORDER)

        # Title & Subtitle
        title = "ANTIGRAVITY ENGINE"
        sub = "Interactive Physics Simulation"
        tw = pr.measure_text(title, 26)
        sw_sub = pr.measure_text(sub, 16)
        pr.draw_text(title, (sw - tw) // 2, py + 25, 26, Colors.UI_ACTIVE)
        pr.draw_text(sub, (sw - sw_sub) // 2, py + 58, 16, Colors.TEXT)
        pr.draw_line(px + 30, py + 85, px + panel_w - 30, py + 85, Colors.UI_BORDER)

        # Update button positions dynamically to keep them centered
        bx = (sw - 260) // 2
        self.btn_start.rect.x, self.btn_start.rect.y = bx, py + 110
        self.btn_settings.rect.x, self.btn_settings.rect.y = bx, py + 175
        self.btn_quit.rect.x, self.btn_quit.rect.y = bx, py + 240

        # Handle button interactions
        if self.btn_start.update_and_draw():
            return AppScreen.SIMULATION
        if self.btn_settings.update_and_draw():
            return AppScreen.SETTINGS
        if self.btn_quit.update_and_draw():
            return AppScreen.QUIT

        return AppScreen.MAIN_MENU
