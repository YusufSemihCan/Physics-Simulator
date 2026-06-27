import pyray as pr
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button
from Graphics.UI.ui_menu import AppScreen

class SettingsScreen:
    """Configuration screen allowing users to customize display modes and resolution."""
    def __init__(self, renderer):
        self.renderer = renderer
        self.btn_res = Button(0, 0, 300, 45, "Resolution: Auto")
        self.btn_mode = Button(0, 0, 300, 45, "Display Mode: Windowed")
        self.btn_back = Button(0, 0, 300, 45, "Back to Main Menu")
        
        self.display_modes = ["Windowed", "Borderless Windowed", "True Fullscreen"]
        self.mode_idx = 0

    def update_and_draw(self) -> AppScreen:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()

        panel_w, panel_h = 460, 360
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2

        pr.draw_rectangle_rounded(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_BORDER)

        title = "DISPLAY & ENGINE SETTINGS"
        tw = pr.measure_text(title, 22)
        pr.draw_text(title, (sw - tw) // 2, py + 25, 22, Colors.UI_ACTIVE)
        pr.draw_line(px + 30, py + 65, px + panel_w - 30, py + 65, Colors.UI_BORDER)

        # Dynamic readout updates
        cur_w, cur_h = pr.get_screen_width(), pr.get_screen_height()
        self.btn_res.text = f"Cycle Resolution ({cur_w}x{cur_h})"
        self.btn_mode.text = f"Mode: {self.display_modes[self.mode_idx]}"

        bx = (sw - 300) // 2
        self.btn_res.rect.x, self.btn_res.rect.y = bx, py + 95
        self.btn_mode.rect.x, self.btn_mode.rect.y = bx, py + 165
        self.btn_back.rect.x, self.btn_back.rect.y = bx, py + 250

        # Handle Resolution Cycling
        if self.btn_res.update_and_draw():
            self.renderer.res_index = (self.renderer.res_index + 1) % len(self.renderer.resolutions)
            w, h = self.renderer.resolutions[self.renderer.res_index]
            pr.set_window_size(w, h)

        # Handle Display Mode Cycling
        if self.btn_mode.update_and_draw():
            self.mode_idx = (self.mode_idx + 1) % len(self.display_modes)
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

        if self.btn_back.update_and_draw():
            return AppScreen.MAIN_MENU

        return AppScreen.SETTINGS
