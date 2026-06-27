import pyray as pr
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button, NodeSelector
from Graphics.UI.ui_menu import AppScreen

class LoadScenarioScreen:
    """Dedicated detailed load screen allowing teachers and students to inspect scenario statistics and preview descriptions before launching."""
    def __init__(self, app):
        self.app = app
        scenario_list = self.app.scenarios.list_scenarios() or ["Default"]
        self.selector = NodeSelector(0, 0, 480, "Select Preset:", scenario_list, 0)
        self.btn_launch = Button(0, 0, 290, 45, "Launch Selected Scenario")
        self.btn_back = Button(0, 0, 290, 45, "Back to Main Menu")
        self.cached_scene = None
        self.last_selected_name = None

    def refresh_list(self) -> None:
        lst = self.app.scenarios.list_scenarios() or ["Default"]
        self.selector.options = lst
        self.selector.current_index = min(self.selector.current_index, len(lst) - 1)
        self.last_selected_name = None  # Force card refresh

    def get_selected_scenario(self) -> str:
        idx = self.selector.current_index
        if 0 <= idx < len(self.selector.options):
            return self.selector.options[idx]
        return "Default"

    def update_and_draw(self) -> AppScreen:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()

        # Dynamic panel sizing
        panel_w, panel_h = 660, 520
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2

        # Draw semi-transparent background panel
        pr.draw_rectangle_rounded(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_BORDER)

        # Title & Subtitle
        title = "CLASSROOM SCENARIO SELECTION"
        sub = "Inspect configuration details and geometry before loading into classroom"
        tw = pr.measure_text(title, 24)
        sw_sub = pr.measure_text(sub, 15)
        pr.draw_text(title, (sw - tw) // 2, py + 22, 24, Colors.UI_ACTIVE)
        pr.draw_text(sub, (sw - sw_sub) // 2, py + 54, 15, Colors.TEXT)
        pr.draw_line(px + 30, py + 82, px + panel_w - 30, py + 82, Colors.UI_BORDER)

        # Position and update node selector
        self.selector.x = (sw - 480) // 2
        self.selector.y = py + 105
        self.selector.width = 480
        self.selector.update_and_draw()

        selected_name = self.get_selected_scenario()
        if selected_name != self.last_selected_name:
            self.last_selected_name = selected_name
            self.cached_scene = self.app.scenarios.load_scenario(selected_name)

        # Draw Detailed Info Card
        card_w, card_h = 600, 230
        cx = px + 30
        cy = py + 175
        pr.draw_rectangle_rounded(pr.Rectangle(cx, cy, card_w, card_h), 0.1, 8, pr.Color(18, 20, 25, 230))
        pr.draw_rectangle_rounded_lines(pr.Rectangle(cx, cy, card_w, card_h), 0.1, 8, Colors.UI_BORDER)

        if self.cached_scene:
            # Header inside card
            pr.draw_text(f"Preset: {self.cached_scene.name}", cx + 25, cy + 20, 20, Colors.UI_ACTIVE)
            desc = self.cached_scene.description or "No description provided for this scenario."
            pr.draw_text(desc, cx + 25, cy + 50, 16, Colors.TEXT)
            pr.draw_line(cx + 25, cy + 80, cx + card_w - 25, cy + 80, Colors.UI_BORDER)

            # Calculate geometry stats
            spheres = sum(1 for s in self.cached_scene.shapes if s.shape_type == "sphere")
            cubes = sum(1 for s in self.cached_scene.shapes if s.shape_type == "cube")
            total = len(self.cached_scene.shapes)
            avg_rest = sum(s.restitution for s in self.cached_scene.shapes) / total if total > 0 else 0.0

            pr.draw_text("Scenario Breakdown & Specifications:", cx + 25, cy + 98, 16, pr.Color(200, 210, 225, 255))
            pr.draw_text(f"* Total Rigid Bodies:  {total} active physical object(s)", cx + 35, cy + 130, 15, Colors.TEXT)
            pr.draw_text(f"* Geometry Types:      {spheres} Sphere(s) | {cubes} Cube(s)", cx + 35, cy + 158, 15, Colors.TEXT)
            pr.draw_text(f"* Average Elasticity:  {avg_rest:.2f} restitution coefficient", cx + 35, cy + 186, 15, Colors.TEXT)
        else:
            pr.draw_text("Unable to load scenario details.", cx + 25, cy + 40, 16, pr.Color(220, 53, 69, 255))

        # Action Buttons at bottom
        self.btn_launch.rect.x, self.btn_launch.rect.y = px + 30, py + 435
        self.btn_back.rect.x, self.btn_back.rect.y = px + 340, py + 435

        if self.btn_launch.update_and_draw():
            return AppScreen.SIMULATION
        if self.btn_back.update_and_draw():
            return AppScreen.MAIN_MENU

        return AppScreen.LOAD_SCENARIO
