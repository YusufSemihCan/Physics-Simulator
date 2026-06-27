from enum import Enum
import pyray as pr
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button, NodeSelector
from Simulation.sim_scenarios import ScenarioManager

class AppScreen(Enum):
    MAIN_MENU = 1
    SETTINGS = 2
    SIMULATION = 3
    QUIT = 4
    SCENARIOS = 5
    LOAD_SCENARIO = 6

class MainMenuScreen:
    """The landing screen where teachers and developers choose navigation options or launch tools."""
    def __init__(self):
        self.btn_start = Button(0, 0, 320, 42, "Launch / Resume Simulation")
        self.btn_load = Button(0, 0, 320, 42, "Load Scenario (Browse & Preview)")
        self.btn_scenarios = Button(0, 0, 320, 42, "Manage Scenarios (Import/Export)")
        self.btn_settings = Button(0, 0, 320, 42, "Settings")
        self.btn_quit = Button(0, 0, 320, 42, "Quit Application")

    def update_and_draw(self) -> AppScreen:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()

        # Dynamic centering calculation
        panel_w, panel_h = 460, 450
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2

        # Draw semi-transparent glassmorphism menu panel
        pr.draw_rectangle_rounded(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_BORDER)

        # Title & Subtitle
        title = "ANTIGRAVITY CLASSROOM"
        sub = "Interactive Physics Education Engine"
        tw = pr.measure_text(title, 26)
        sw_sub = pr.measure_text(sub, 16)
        pr.draw_text(title, (sw - tw) // 2, py + 25, 26, Colors.UI_ACTIVE)
        pr.draw_text(sub, (sw - sw_sub) // 2, py + 58, 16, Colors.TEXT)
        pr.draw_line(px + 30, py + 85, px + panel_w - 30, py + 85, Colors.UI_BORDER)

        # Position menu buttons dynamically
        sx = (sw - 320) // 2
        self.btn_start.rect.x, self.btn_start.rect.y = sx, py + 110
        self.btn_load.rect.x, self.btn_load.rect.y = sx, py + 168
        self.btn_scenarios.rect.x, self.btn_scenarios.rect.y = sx, py + 226
        self.btn_settings.rect.x, self.btn_settings.rect.y = sx, py + 284
        self.btn_quit.rect.x, self.btn_quit.rect.y = sx, py + 342

        # Handle widget updates
        if self.btn_start.update_and_draw():
            return AppScreen.SIMULATION
        if self.btn_load.update_and_draw():
            return AppScreen.LOAD_SCENARIO
        if self.btn_scenarios.update_and_draw():
            return AppScreen.SCENARIOS
        if self.btn_settings.update_and_draw():
            return AppScreen.SETTINGS
        if self.btn_quit.update_and_draw():
            return AppScreen.QUIT

        return AppScreen.MAIN_MENU
