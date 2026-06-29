from enum import Enum
import pyray as pr
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button
from Simulation.sim_modes import SimulationMode

class AppScreen(Enum):
    MAIN_MENU = 1
    SETTINGS = 2
    SIMULATION = 3
    QUIT = 4
    SCENARIOS = 5
    LOAD_SCENARIO = 6

class MainMenuScreen:
    """The landing screen where users choose new simulations via a modal menu or navigation options."""
    def __init__(self):
        self.btn_new_sim = Button(0, 0, 430, 45, "New Simulation")
        self.btn_load = Button(0, 0, 430, 45, "Load Scenario File Tree")
        self.btn_settings = Button(0, 0, 210, 40, "Settings")
        self.btn_quit = Button(0, 0, 210, 40, "Quit Application")

        self.show_new_sim_modal = False
        self.btn_m_3d = Button(0, 0, 360, 40, "3D Kinematics")
        self.btn_m_2d = Button(0, 0, 360, 40, "2D Kinetics")
        self.btn_m_circuits = Button(0, 0, 360, 40, "DC Circuits")
        self.btn_m_optics = Button(0, 0, 360, 40, "Ray Optics")
        self.btn_m_fields = Button(0, 0, 360, 40, "Electromagnetic Fields")
        self.btn_m_back = Button(0, 0, 360, 35, "Cancel")

        self._modal_buttons = [
            (self.btn_m_3d, SimulationMode.KINEMATICS_3D),
            (self.btn_m_2d, SimulationMode.KINETIC_2D),
            (self.btn_m_circuits, SimulationMode.CIRCUITS),
            (self.btn_m_optics, SimulationMode.OPTICS),
            (self.btn_m_fields, SimulationMode.FIELDS),
        ]

    def update_and_draw(self, app=None) -> AppScreen:
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()

        if self.show_new_sim_modal:
            # Draw dark overlay over background
            pr.draw_rectangle(0, 0, sw, sh, pr.Color(0, 0, 0, 180))
            mw, mh = 440, 380
            mx = (sw - mw) // 2
            my = (sh - mh) // 2
            pr.draw_rectangle_rounded(pr.Rectangle(mx, my, mw, mh), 0.1, 8, Colors.UI_PANEL)
            pr.draw_rectangle_rounded_lines(pr.Rectangle(mx, my, mw, mh), 0.1, 8, Colors.UI_ACTIVE)
            pr.draw_text("CHOOSE SIMULATION MODE", mx + 60, my + 20, 22, Colors.UI_ACTIVE)
            pr.draw_line(mx + 20, my + 55, mx + mw - 20, my + 55, Colors.UI_BORDER)

            bx = mx + 40
            for i, (btn, mode) in enumerate(self._modal_buttons):
                btn.rect.x, btn.rect.y = bx, my + 70 + i * 50
                if btn.update_and_draw():
                    self.show_new_sim_modal = False
                    if app and hasattr(app, 'switch_mode'):
                        app.switch_mode(mode)
                    return AppScreen.SIMULATION

            self.btn_m_back.rect.x, self.btn_m_back.rect.y = bx, my + 325
            if self.btn_m_back.update_and_draw() or pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
                self.show_new_sim_modal = False

            return AppScreen.MAIN_MENU

        panel_w, panel_h = 500, 320
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2

        pr.draw_rectangle_rounded(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_PANEL)
        pr.draw_rectangle_rounded_lines(pr.Rectangle(px, py, panel_w, panel_h), 0.1, 8, Colors.UI_BORDER)

        title = "PHYSICS SIMULATOR"
        sub = "Interactive Multi-Domain Physics Lab"
        tw = pr.measure_text(title, 28)
        sw_sub = pr.measure_text(sub, 16)
        pr.draw_text(title, (sw - tw) // 2, py + 25, 28, Colors.UI_ACTIVE)
        pr.draw_text(sub, (sw - sw_sub) // 2, py + 60, 16, Colors.TEXT)
        pr.draw_line(px + 30, py + 90, px + panel_w - 30, py + 90, Colors.UI_BORDER)

        sx = px + 35
        self.btn_new_sim.rect.x, self.btn_new_sim.rect.y = sx, py + 115
        self.btn_load.rect.x, self.btn_load.rect.y = sx, py + 175
        self.btn_settings.rect.x, self.btn_settings.rect.y = sx, py + 240
        self.btn_quit.rect.x, self.btn_quit.rect.y = sx + 220, py + 240

        if self.btn_new_sim.update_and_draw():
            self.show_new_sim_modal = True
        if self.btn_load.update_and_draw():
            return AppScreen.LOAD_SCENARIO
        if self.btn_settings.update_and_draw():
            return AppScreen.SETTINGS
        if self.btn_quit.update_and_draw():
            return AppScreen.QUIT

        return AppScreen.MAIN_MENU
