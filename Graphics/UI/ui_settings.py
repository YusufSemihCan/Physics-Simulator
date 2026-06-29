import pyray as pr
from typing import Dict, Optional
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button, NodeSelector
from Graphics.UI.ui_menu import AppScreen
from Graphics.UI.ui_key_bindings import KeyBindingsManager

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

        # Tab navigation and Key Bindings state
        self.active_tab = "display"
        self.btn_tab_display = Button(0, 0, 220, 35, "Display Settings")
        self.btn_tab_bindings = Button(0, 0, 220, 35, "Key Bindings")
        self.bindings_page = 0
        self.btn_prev_page = Button(0, 0, 110, 30, "< Prev")
        self.btn_next_page = Button(0, 0, 110, 30, "Next >")
        self.remapping_action: Optional[str] = None
        self.action_buttons: Dict[str, Button] = {}

        mgr = KeyBindingsManager.get_instance()
        for action in mgr.get_all_actions():
            self.action_buttons[action] = Button(0, 0, 150, 30, "")

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

        # Tab navigation buttons
        self.btn_tab_display.rect.x, self.btn_tab_display.rect.y = px + 30, py + 65
        self.btn_tab_bindings.rect.x, self.btn_tab_bindings.rect.y = px + 270, py + 65
        if self.btn_tab_display.update_and_draw():
            self.active_tab = "display"
            self.remapping_action = None
        if self.btn_tab_bindings.update_and_draw():
            self.active_tab = "bindings"
            self.remapping_action = None

        pr.draw_line(px + 30, py + 110, px + panel_w - 30, py + 110, Colors.UI_BORDER)

        if self.active_tab == "display":
            # Update node selector coordinates dynamically
            sel_w = panel_w - 100
            self.sel_res.x, self.sel_res.y, self.sel_res.width = px + 50, py + 130, sel_w
            self.sel_mode.x, self.sel_mode.y, self.sel_mode.width = px + 50, py + 195, sel_w
            self.sel_top_bar.x, self.sel_top_bar.y, self.sel_top_bar.width = px + 50, py + 260, sel_w
            self.sel_bot_bar.x, self.sel_bot_bar.y, self.sel_bot_bar.width = px + 50, py + 325, sel_w
            self.sel_sidebar.x, self.sel_sidebar.y, self.sel_sidebar.width = px + 50, py + 390, sel_w

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
        else:
            mgr = KeyBindingsManager.get_instance()
            if self.remapping_action is not None:
                msg = f"Press any key to bind '{mgr.get_action_label(self.remapping_action)}'..."
                mw = pr.measure_text(msg, 18)
                pr.draw_rectangle_rounded(pr.Rectangle(px + 60, py + 220, panel_w - 120, 100), 0.1, 6, Colors.UI_HOVER)
                pr.draw_rectangle_rounded_lines(pr.Rectangle(px + 60, py + 220, panel_w - 120, 100), 0.1, 6, Colors.UI_ACTIVE)
                pr.draw_text(msg, px + (panel_w - mw) // 2, py + 250, 18, Colors.TEXT)
                pr.draw_text("Press ESC to cancel", px + (panel_w - pr.measure_text("Press ESC to cancel", 14)) // 2, py + 285, 14, Colors.AXIS_X)
                
                key = pr.get_key_pressed()
                if key != 0:
                    if key != pr.KeyboardKey.KEY_ESCAPE:
                        mgr.remap_action(self.remapping_action, key)
                    self.remapping_action = None
            else:
                actions = mgr.get_all_actions()
                items_per_page = 6
                max_pages = max(1, (len(actions) + items_per_page - 1) // items_per_page)
                self.bindings_page = max(0, min(max_pages - 1, self.bindings_page))
                
                start_idx = self.bindings_page * items_per_page
                page_actions = actions[start_idx:min(start_idx + items_per_page, len(actions))]
                
                for i, action in enumerate(page_actions):
                    item_y = py + 130 + i * 45
                    label = mgr.get_action_label(action)
                    pr.draw_text(label, px + 50, item_y + 8, 16, Colors.TEXT)
                    
                    keys = mgr.get_action_keys(action)
                    key_str = mgr.get_key_name(keys[0]) if keys else "NONE"
                    btn = self.action_buttons.get(action)
                    if btn:
                        btn.text = key_str
                        btn.rect.x, btn.rect.y = px + panel_w - 200, item_y
                        if btn.update_and_draw():
                            self.remapping_action = action

                if max_pages > 1:
                    self.btn_prev_page.rect.x, self.btn_prev_page.rect.y = px + 50, py + 410
                    self.btn_next_page.rect.x, self.btn_next_page.rect.y = px + panel_w - 160, py + 410
                    if self.btn_prev_page.update_and_draw(enabled=(self.bindings_page > 0)):
                        self.bindings_page -= 1
                    if self.btn_next_page.update_and_draw(enabled=(self.bindings_page < max_pages - 1)):
                        self.bindings_page += 1
                    page_str = f"Page {self.bindings_page + 1}/{max_pages}"
                    pw = pr.measure_text(page_str, 16)
                    pr.draw_text(page_str, px + (panel_w - pw) // 2, py + 417, 16, Colors.TEXT)

        # Back button
        bx = (sw - 300) // 2
        self.btn_back.rect.x, self.btn_back.rect.y = bx, py + 465
        if self.btn_back.update_and_draw():
            return AppScreen.MAIN_MENU

        return AppScreen.SETTINGS
