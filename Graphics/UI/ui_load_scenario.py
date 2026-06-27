import os
import pyray as pr
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button, FileTreeSelector
from Graphics.UI.ui_menu import AppScreen

class LoadScenarioScreen:
    """Dedicated file tree load screen allowing direct file selection and classroom scenario management."""
    def __init__(self, app):
        self.app = app
        scenario_list = self.app.scenarios.list_scenarios() or ["Default"]
        root_dir = getattr(self.app.scenarios, 'scenarios_dir', 'scenarios')
        self.selector = FileTreeSelector(0, 0, 580, 310, root_dir, scenario_list, 0)
        self.btn_launch = Button(0, 0, 135, 40, "Load Selected")
        self.btn_save = Button(0, 0, 135, 40, "Save Active")
        self.btn_new_folder = Button(0, 0, 135, 40, "New Folder")
        self.btn_delete = Button(0, 0, 145, 40, "Delete Selected")
        self.btn_back = Button(0, 0, 580, 40, "Back to Main Menu")
        self.cached_scene = None
        self.last_selected_name = None
        self.notification = ""
        self.notif_timer = 0.0
        
        self.popup_mode = None  # None, "NEW_FOLDER", "SAVE_AS"
        self.input_text = ""
        self.btn_modal_confirm = Button(0, 0, 140, 36, "Confirm")
        self.btn_modal_cancel = Button(0, 0, 140, 36, "Cancel")

    def refresh_list(self) -> None:
        lst = self.app.scenarios.list_scenarios() or ["Default"]
        self.selector.options = lst
        self.selector.current_index = min(self.selector.current_index, len(lst) - 1)
        self.last_selected_name = None

    def get_selected_scenario(self) -> str:
        idx = self.selector.current_index
        if 0 <= idx < len(self.selector.options):
            return self.selector.options[idx]
        return "Default"

    def is_item_folder(self, name: str) -> bool:
        root_dir = getattr(self.app.scenarios, 'scenarios_dir', 'scenarios')
        full_path = os.path.join(root_dir, name)
        return os.path.isdir(full_path) or any(o.replace("\\", "/").startswith(name.replace("\\", "/") + "/") for o in self.selector.options)

    def set_notification(self, msg: str) -> None:
        self.notification = msg
        self.notif_timer = 3.5

    def update_and_draw(self) -> AppScreen:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        dt = pr.get_frame_time()

        if self.notif_timer > 0:
            self.notif_timer -= dt

        # Dynamic panel sizing
        panel_w, panel_h = 640, 540
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2

        # Draw semi-transparent background panel
        pr.draw_rectangle_rounded(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_BORDER)

        # Title & Subtitle
        title = "FILE SYSTEM — SCENARIO EXPLORER"
        sub = "Select a scenario file from directory tree to load or modify"
        tw = pr.measure_text(title, 22)
        sw_sub = pr.measure_text(sub, 15)
        pr.draw_text(title, (sw - tw) // 2, py + 20, 22, Colors.UI_ACTIVE)
        pr.draw_text(sub, (sw - sw_sub) // 2, py + 48, 15, Colors.TEXT)
        pr.draw_line(px + 30, py + 75, px + panel_w - 30, py + 75, Colors.UI_BORDER)

        # Position file tree
        self.selector.x = px + 30
        self.selector.y = py + 90
        self.selector.width = panel_w - 60
        self.selector.height = 310

        # Action Buttons positioning
        by = py + 415
        self.btn_launch.rect.x, self.btn_launch.rect.y = px + 30, by
        self.btn_save.rect.x, self.btn_save.rect.y = px + 175, by
        self.btn_new_folder.rect.x, self.btn_new_folder.rect.y = px + 320, by
        self.btn_delete.rect.x, self.btn_delete.rect.y = px + 465, by
        self.btn_back.rect.x, self.btn_back.rect.y = px + 30, by + 50

        if not self.popup_mode:
            self.selector.update_and_draw(enabled=True)
            if getattr(self.selector, 'drag_move_request', None):
                src, dest = self.selector.drag_move_request
                if hasattr(self.app.scenarios, 'move_scenario') and self.app.scenarios.move_scenario(src, dest):
                    self.refresh_list()
                    self.set_notification(f"Moved '{src}' to '{dest or 'root'}'!")
                else:
                    self.set_notification(f"Could not move '{src}'!")
            selected_name = self.get_selected_scenario()
            if selected_name != self.last_selected_name:
                self.last_selected_name = selected_name

            if self.btn_launch.update_and_draw(enabled=True):
                if self.is_item_folder(selected_name):
                    self.set_notification("Cannot load a folder! Please select a .json file.")
                else:
                    loaded = self.app.scenarios.load_scenario(selected_name)
                    if loaded:
                        self.app.sim.load_scene(loaded)
                        self.app.trails.clear()
                    return AppScreen.SIMULATION

            if self.btn_save.update_and_draw(enabled=True):
                if self.is_item_folder(selected_name):
                    self.popup_mode = "SAVE_AS"
                    self.input_text = ""
                else:
                    self.app.scenarios.save_scenario(selected_name, self.app.sim.scene)
                    self.refresh_list()
                    self.set_notification(f"Saved active workspace to '{selected_name}.json'!")

            if self.btn_new_folder.update_and_draw(enabled=True):
                self.popup_mode = "NEW_FOLDER"
                self.input_text = ""

            if self.btn_delete.update_and_draw(enabled=True):
                if len(self.selector.options) > 1:
                    self.app.scenarios.delete_scenario(selected_name)
                    self.refresh_list()
                    self.set_notification(f"Deleted '{selected_name}'!")
                else:
                    self.set_notification("Cannot delete the last remaining scenario file!")

            if self.btn_back.update_and_draw(enabled=True):
                return AppScreen.MAIN_MENU
        else:
            # Draw background elements passively when modal popup is active
            self.selector.update_and_draw(enabled=False)
            self.btn_launch.update_and_draw(enabled=False)
            self.btn_save.update_and_draw(enabled=False)
            self.btn_new_folder.update_and_draw(enabled=False)
            self.btn_delete.update_and_draw(enabled=False)
            self.btn_back.update_and_draw(enabled=False)

            # Draw modal backdrop
            pr.draw_rectangle(0, 0, sw, sh, pr.Color(0, 0, 0, 160))

            modal_w, modal_h = 440, 240
            mx = (sw - modal_w) // 2
            my = (sh - modal_h) // 2
            pr.draw_rectangle_rounded(pr.Rectangle(mx, my, modal_w, modal_h), 0.1, 8, Colors.UI_PANEL)
            pr.draw_rectangle_rounded_lines(pr.Rectangle(mx, my, modal_w, modal_h), 0.1, 8, Colors.UI_BORDER)

            title_str = "CREATE NEW FOLDER" if self.popup_mode == "NEW_FOLDER" else "SAVE SCENARIO AS"
            tw_m = pr.measure_text(title_str, 18)
            pr.draw_text(title_str, mx + (modal_w - tw_m) // 2, my + 18, 18, Colors.UI_ACTIVE)
            pr.draw_line(mx + 20, my + 45, mx + modal_w - 20, my + 45, Colors.UI_BORDER)

            selected_name = self.get_selected_scenario()
            if self.is_item_folder(selected_name):
                target_parent = selected_name
            else:
                target_parent = os.path.dirname(selected_name).replace("\\", "/")

            loc_str = f"Inside: {target_parent}/" if target_parent else "Inside: Root Directory"
            pr.draw_text(loc_str, mx + 25, my + 55, 14, Colors.TEXT)

            # Process text input
            char = pr.get_char_pressed()
            while char > 0:
                if 32 <= char <= 126 and len(self.input_text) < 40:
                    self.input_text += chr(char)
                char = pr.get_char_pressed()

            if pr.is_key_pressed(pr.KeyboardKey.KEY_BACKSPACE) or pr.is_key_pressed_repeat(pr.KeyboardKey.KEY_BACKSPACE):
                if len(self.input_text) > 0:
                    self.input_text = self.input_text[:-1]

            input_rect = pr.Rectangle(mx + 25, my + 80, modal_w - 50, 40)
            pr.draw_rectangle_rounded(input_rect, 0.2, 6, Colors.GRID_MINOR)
            pr.draw_rectangle_rounded_lines(input_rect, 0.2, 6, Colors.UI_ACTIVE)

            display_text = self.input_text
            if int(pr.get_time() * 2) % 2 == 0:
                display_text += "_"
            while pr.measure_text(display_text, 16) > input_rect.width - 20 and len(display_text) > 1:
                display_text = display_text[1:]
            pr.draw_text(display_text, int(input_rect.x) + 12, int(input_rect.y) + 12, 16, Colors.TEXT)

            self.btn_modal_confirm.text = "Create" if self.popup_mode == "NEW_FOLDER" else "Save"
            self.btn_modal_confirm.rect.x = mx + 45
            self.btn_modal_confirm.rect.y = my + 145
            self.btn_modal_cancel.rect.x = mx + 255
            self.btn_modal_cancel.rect.y = my + 145

            confirm_clicked = self.btn_modal_confirm.update_and_draw(enabled=True) or pr.is_key_pressed(pr.KeyboardKey.KEY_ENTER) or pr.is_key_pressed(pr.KeyboardKey.KEY_KP_ENTER)
            cancel_clicked = self.btn_modal_cancel.update_and_draw(enabled=True) or pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE)

            if cancel_clicked:
                self.popup_mode = None
            elif confirm_clicked and self.input_text.strip():
                clean_name = self.input_text.strip()
                full_rel = os.path.join(target_parent, clean_name).replace("\\", "/") if target_parent else clean_name
                
                if self.popup_mode == "NEW_FOLDER":
                    self.app.scenarios.create_folder(full_rel)
                    self.refresh_list()
                    self.set_notification(f"Created folder '{full_rel}'!")
                elif self.popup_mode == "SAVE_AS":
                    self.app.scenarios.save_scenario(full_rel, self.app.sim.scene)
                    self.refresh_list()
                    self.set_notification(f"Saved scenario '{full_rel}.json'!")
                
                self.popup_mode = None

        if self.notif_timer > 0:
            nw = pr.measure_text(self.notification, 15)
            pr.draw_rectangle_rounded(pr.Rectangle((sw - nw - 30) // 2, py + 500, nw + 30, 28), 0.5, 6, pr.Color(40, 180, 99, 220) if "Cannot" not in self.notification else pr.Color(220, 53, 69, 220))
            pr.draw_text(self.notification, (sw - nw) // 2, py + 506, 15, pr.WHITE)

        return AppScreen.LOAD_SCENARIO
