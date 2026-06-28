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
        
        self.sel_top_bar = NodeSelector(0, 0, 380, "Top Bar", ["Hidden", "Visible"], 1)
        self.sel_bot_bar = NodeSelector(0, 0, 380, "Bottom Bar", ["Hidden", "Visible"], 1)
        self.sel_sidebar = NodeSelector(0, 0, 380, "Sidebar Layout", ["Left", "Right", "Hidden"], 0)

    def update_and_draw(self) -> AppScreen:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()

        panel_w, panel_h = 520, 540
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2

        pr.draw_rectangle_rounded(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_BORDER)

        title = "DISPLAY & WORKSPACE SETTINGS"
        tw = pr.measure_text(title, 22)
        pr.draw_text(title, (sw - tw) // 2, py + 20, 22, Colors.UI_ACTIVE)
        pr.draw_line(px + 30, py + 55, px + panel_w - 30, py + 55, Colors.UI_BORDER)

        # Update node selector coordinates dynamically
        sel_w = panel_w - 100
        self.sel_res.x, self.sel_res.y, self.sel_res.width = px + 50, py + 75, sel_w
        self.sel_mode.x, self.sel_mode.y, self.sel_mode.width = px + 50, py + 145, sel_w
        self.sel_top_bar.x, self.sel_top_bar.y, self.sel_top_bar.width = px + 50, py + 215, sel_w
        self.sel_bot_bar.x, self.sel_bot_bar.y, self.sel_bot_bar.width = px + 50, py + 285, sel_w
        self.sel_sidebar.x, self.sel_sidebar.y, self.sel_sidebar.width = px + 50, py + 355, sel_w

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
            match mode_str:
                case "Windowed":
                    if is_fs:
                        pr.toggle_borderless_windowed() if pr.is_window_state(pr.ConfigFlags.FLAG_BORDERLESS_WINDOWED_MODE) else pr.toggle_fullscreen()
                    w, h = self.renderer.resolutions[self.renderer.res_index]
                    pr.set_window_size(w, h)
                case "Borderless Windowed" | "True Fullscreen":
                    if not is_fs:
                        pr.toggle_borderless_windowed()

        # Handle Workspace UI Customizations
        if hasattr(self.renderer, 'workspace_ui'):
            tb_changed, tb_idx = self.sel_top_bar.update_and_draw()
            if tb_changed:
                self.renderer.workspace_ui.show_top_bar = (tb_idx == 1)
                
            bb_changed, bb_idx = self.sel_bot_bar.update_and_draw()
            if bb_changed:
                self.renderer.workspace_ui.show_bottom_bar = (bb_idx == 1)
                
            sb_changed, sb_idx = self.sel_sidebar.update_and_draw()
            if sb_changed:
                match sb_idx:
                    case 0:
                        self.renderer.workspace_ui.show_sidebar = True
                        self.renderer.workspace_ui.sidebar_position = 'left'
                    case 1:
                        self.renderer.workspace_ui.show_sidebar = True
                        self.renderer.workspace_ui.sidebar_position = 'right'
                    case _:
                        self.renderer.workspace_ui.show_sidebar = False

        # Back button
        bx = (sw - 300) // 2
        self.btn_back.rect.x, self.btn_back.rect.y = bx, py + 450
        if self.btn_back.update_and_draw():
            return AppScreen.MAIN_MENU

        return AppScreen.SETTINGS
