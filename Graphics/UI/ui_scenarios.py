import json
import pyray as pr
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button, NodeSelector
from Graphics.UI.ui_menu import AppScreen
from Simulation.sim_controller import SimulationScene

class ScenarioScreen:
    """Dedicated management tab for loading, saving, importing, and exporting classroom scenarios."""
    def __init__(self, app):
        self.app = app
        scenario_list = self.app.scenarios.list_scenarios() or ["Default"]
        self.selector = NodeSelector(0, 0, 380, "Saved Scenarios:", scenario_list, 0)
        
        self.btn_load = Button(0, 0, 380, 40, "Load Selected into Classroom")
        self.btn_save_live = Button(0, 0, 380, 40, "Save Active Workspace to Disk")
        self.btn_export = Button(0, 0, 185, 40, "Export (Copy JSON)")
        self.btn_import = Button(0, 0, 185, 40, "Import (Paste JSON)")
        self.btn_delete = Button(0, 0, 380, 40, "Delete Selected Scenario")
        self.btn_back = Button(0, 0, 380, 40, "Back to Main Menu")

        self.notification = ""
        self.notif_timer = 0.0

    def refresh_list(self) -> None:
        lst = self.app.scenarios.list_scenarios() or ["Default"]
        self.selector.options = lst
        self.selector.current_index = min(self.selector.current_index, len(lst) - 1)
        if hasattr(self.app, 'load_scenario_screen'):
            self.app.load_scenario_screen.refresh_list()

    def set_notification(self, msg: str) -> None:
        self.notification = msg
        self.notif_timer = 3.5

    def update_and_draw(self) -> AppScreen:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        dt = pr.get_frame_time()

        if self.notif_timer > 0:
            self.notif_timer -= dt

        # Centered management panel
        panel_w, panel_h = 520, 520
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2

        pr.draw_rectangle_rounded(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_BORDER)

        title = "CLASSROOM SCENARIOS TAB"
        sub = "Import, Export & Manage Classroom Configurations"
        tw = pr.measure_text(title, 24)
        sw_sub = pr.measure_text(sub, 15)
        pr.draw_text(title, (sw - tw) // 2, py + 20, 24, Colors.UI_ACTIVE)
        pr.draw_text(sub, (sw - sw_sub) // 2, py + 52, 15, Colors.TEXT)
        pr.draw_line(px + 30, py + 80, px + panel_w - 30, py + 80, Colors.UI_BORDER)

        # Position widgets dynamically
        sx = (sw - 380) // 2
        self.selector.x = sx
        self.selector.y = py + 100
        self.selector.width = 380

        self.btn_load.rect.x, self.btn_load.rect.y = sx, py + 165
        self.btn_save_live.rect.x, self.btn_save_live.rect.y = sx, py + 220
        
        self.btn_export.rect.x, self.btn_export.rect.y = sx, py + 275
        self.btn_import.rect.x, self.btn_import.rect.y = sx + 195, py + 275
        
        self.btn_delete.rect.x, self.btn_delete.rect.y = sx, py + 330
        self.btn_back.rect.x, self.btn_back.rect.y = sx, py + 415

        # Update widget interactions
        _, idx = self.selector.update_and_draw()

        if self.btn_load.update_and_draw():
            selected_name = self.selector.options[idx]
            loaded = self.app.scenarios.load_scenario(selected_name)
            if loaded:
                self.app.sim.load_scene(loaded)
                self.app.trails.clear()
                self.set_notification(f"Loaded '{selected_name}'!")
                return AppScreen.SIMULATION

        if self.btn_save_live.update_and_draw():
            selected_name = self.selector.options[idx]
            self.app.scenarios.save_scenario(selected_name, self.app.sim.scene)
            self.refresh_list()
            self.set_notification(f"Saved live workspace to '{selected_name}'!")

        if self.btn_export.update_and_draw():
            selected_name = self.selector.options[idx]
            loaded = self.app.scenarios.load_scenario(selected_name) or self.app.sim.scene
            json_str = json.dumps(loaded.to_dict(), indent=2)
            pr.set_clipboard_text(json_str)
            self.set_notification(f"Copied '{selected_name}' JSON to Clipboard!")

        if self.btn_import.update_and_draw():
            try:
                raw = pr.get_clipboard_text()
                data = json.loads(raw)
                if "name" in data and "shapes" in data:
                    scene = SimulationScene.from_dict(data)
                    self.app.scenarios.save_scenario(scene.name, scene)
                    self.refresh_list()
                    self.set_notification(f"Imported '{scene.name}' Successfully!")
                else:
                    self.set_notification("Error: Clipboard JSON missing 'name' or 'shapes'!")
            except Exception as e:
                self.set_notification("Error: Invalid JSON data in Clipboard!")

        if self.btn_delete.update_and_draw():
            selected_name = self.selector.options[idx]
            if len(self.selector.options) > 1:
                self.app.scenarios.delete_scenario(selected_name)
                self.refresh_list()
                self.set_notification(f"Deleted '{selected_name}'!")
            else:
                self.set_notification("Cannot delete the last remaining scenario!")

        if self.btn_back.update_and_draw():
            return AppScreen.MAIN_MENU

        # Display status notification banner if active
        if self.notif_timer > 0:
            nw = pr.measure_text(self.notification, 16)
            pr.draw_rectangle_rounded(pr.Rectangle((sw - nw - 40) // 2, py + 475, nw + 40, 32), 0.5, 8, pr.Color(40, 180, 99, 220) if "Error" not in self.notification else pr.Color(220, 53, 69, 220))
            pr.draw_text(self.notification, (sw - nw) // 2, py + 483, 16, pr.WHITE)

        return AppScreen.SCENARIOS
