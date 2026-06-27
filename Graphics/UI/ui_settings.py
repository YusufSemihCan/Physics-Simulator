import pyray as pr
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button, NodeSelector
from Graphics.UI.ui_menu import AppScreen

class SettingsScreen:
    """Configuration screen allowing users to customize display modes and resolution."""
    def __init__(self, renderer):
        self.renderer = renderer
        self.btn_back = Button(0, 0, 300, 45, "Back to Main Menu")
        
        self.display_modes = ["Windowed", "Borderless Windowed", "True Fullscreen"]
        self.mode_idx = 0
        
        res_strings = [f"{w}x{h}" for w, h in self.renderer.resolutions]
        self.sel_res = NodeSelector(0, 0, 380, "Resolution", res_strings, self.renderer.res_index)
        self.sel_mode = NodeSelector(0, 0, 380, "Screen Type", self.display_modes, self.mode_idx)

    def update_and_draw(self) -> AppScreen:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()

        panel_w, panel_h = 480, 380
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2

        pr.draw_rectangle_rounded(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_BORDER)

        title = "DISPLAY & ENGINE SETTINGS"
        tw = pr.measure_text(title, 22)
        pr.draw_text(title, (sw - tw) // 2, py + 25, 22, Colors.UI_ACTIVE)
        pr.draw_line(px + 30, py + 65, px + panel_w - 30, py + 65, Colors.UI_BORDER)

        # Update node selector coordinates dynamically
        sel_w = panel_w - 100
        self.sel_res.x, self.sel_res.y, self.sel_res.width = px + 50, py + 95, sel_w
        self.sel_mode.x, self.sel_mode.y, self.sel_mode.width = px + 50, py + 185, sel_w

        # Handle Resolution Selection
        res_changed, new_res_idx = self.sel_res.update_and_draw()
        if res_changed:
            self.renderer.res_index = new_res_idx
            w, h = self.renderer.resolutions[self.renderer.res_index]
            pr.set_window_size(w, h)

        # Handle Display Mode Selection
        mode_changed, new_mode_idx = self.sel_mode.update_and_draw()
        if mode_changed:
            self.mode_idx = new_mode_idx
            mode_str = self.display_modes[self.mode_idx]
            is_fs = pr.is_window_fullscreen() or pr.is_window_state(pr.ConfigFlags.FLAG_BORDERLESS_WINDOWED_MODE)
            if mode_str == "Windowed":
                if is_fs:
                    pr.toggle_borderless_windowed() if pr.is_window_state(pr.ConfigFlags.FLAG_BORDERLESS_WINDOWED_MODE) else pr.toggle_fullscreen()
                w, h = self.renderer.resolutions[self.renderer.res_index]
                pr.set_window_size(w, h)
            elif mode_str in ("Borderless Windowed", "True Fullscreen"):
                if not is_fs:
                    pr.toggle_borderless_windowed()

        # Back button
        bx = (sw - 300) // 2
        self.btn_back.rect.x, self.btn_back.rect.y = bx, py + 285
        if self.btn_back.update_and_draw():
            return AppScreen.MAIN_MENU

        return AppScreen.SETTINGS
