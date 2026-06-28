import pyray as pr
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button, Slider, Toggle
from Simulation.sim_modes import SimulationMode
from Graphics.UI.ui_menu import AppScreen

class WorkspaceUI:
    """Modular workspace UI layout managing Top Bar, Bottom Bar, Side Bar, dropdowns, and object inspection."""
    def __init__(self, app):
        self.app = app
        
        # Visibility & layout configuration
        self.show_top_bar = True
        self.show_bottom_bar = True
        self.show_sidebar = True
        self.sidebar_position = 'left'  # 'left' or 'right'
        
        # Active unfolding dropdown state: None, 'file', 'mode', 'view'
        self.active_dropdown = None
        
        # Top Bar Dropdown Triggers
        self.btn_top_file = Button(10, 5, 80, 30, "File ▼")
        self.btn_top_mode = Button(100, 5, 100, 30, "Mode ▼")
        self.btn_top_view = Button(210, 5, 80, 30, "View ▼")
        
        # File Dropdown Items
        self.btn_f_new = Button(10, 40, 160, 32, "New Simulation")
        self.btn_f_load = Button(10, 74, 160, 32, "Load Scenario")
        self.btn_f_save = Button(10, 108, 160, 32, "Save Scenario")
        self.btn_f_menu = Button(10, 142, 160, 32, "Main Menu")
        self.btn_f_quit = Button(10, 176, 160, 32, "Quit App")
        
        # Mode Dropdown Items
        self.btn_m_3d = Button(100, 40, 180, 32, "3D Kinematics")
        self.btn_m_2d = Button(100, 74, 180, 32, "2D Kinetics")
        self.btn_m_circ = Button(100, 108, 180, 32, "DC Circuits")
        self.btn_m_opt = Button(100, 142, 180, 32, "Ray Optics")
        self.btn_m_fld = Button(100, 176, 180, 32, "EM Fields")
        
        # View Dropdown Items
        self.btn_v_grid = Button(210, 40, 150, 32, "Toggle Grid")
        self.btn_v_axis = Button(210, 74, 150, 32, "Toggle Axis")
        self.btn_v_settings = Button(210, 108, 150, 32, "Settings")
        
        # Bottom Bar Playback Controls
        self.btn_play = Button(0, 0, 110, 34, "Play / Pause")
        self.btn_stop = Button(0, 0, 100, 34, "Stop / Reset")
        self.btn_rewind = Button(0, 0, 130, 34, "<< Rewind (Hold)")
        self.slider_gravity = Slider(0, 0, 180, 14, "Gravity (m/s²)", 0.0, 25.0, 9.81)
        
        # Sidebar Spawning Tools - 3D/2D
        self.btn_s_sphere = Button(0, 0, 105, 32, "+ Sphere")
        self.btn_s_cube = Button(0, 0, 105, 32, "+ Cube")
        self.btn_s_clear = Button(0, 0, 220, 32, "Clear All")
        
        # Sidebar Spawning Tools - Circuits
        self.btn_c_wire = Button(0, 0, 105, 30, "Wire")
        self.btn_c_bat = Button(0, 0, 105, 30, "Battery")
        self.btn_c_res = Button(0, 0, 105, 30, "Resistor")
        self.btn_c_sw = Button(0, 0, 105, 30, "Switch")
        self.btn_c_bulb = Button(0, 0, 220, 30, "Bulb")
        
        # Sidebar Spawning Tools - Optics
        self.btn_o_emitter = Button(0, 0, 220, 32, "+ Laser Emitter")
        self.btn_o_mirror = Button(0, 0, 105, 32, "+ Mirror")
        self.btn_o_lens = Button(0, 0, 105, 32, "+ Lens")
        
        # Sidebar Spawning Tools - Fields
        self.btn_fld_pos = Button(0, 0, 105, 32, "+ (+1C Charge)")
        self.btn_fld_neg = Button(0, 0, 105, 32, "+ (-1C Charge)")
        self.btn_fld_mag = Button(0, 0, 220, 32, "+ Magnet")
        
        # Inspector Modification Controls
        self.btn_remove_obj = Button(0, 0, 220, 34, "Remove Object")
        self.slider_prop1 = Slider(0, 0, 220, 14, "Property 1", -50.0, 50.0, 0.0)
        self.slider_prop2 = Slider(0, 0, 220, 14, "Property 2", -50.0, 50.0, 0.0)

        # Dispatch lookups for clean optimization
        self.dropdown_rects = {
            'file': pr.Rectangle(10, 40, 160, 175),
            'mode': pr.Rectangle(100, 40, 180, 175),
            'view': pr.Rectangle(210, 40, 150, 110)
        }
        self.dropdown_draw_map = {
            'file': self._draw_dropdown_file,
            'mode': self._draw_dropdown_mode,
            'view': self._draw_dropdown_view
        }
        self.sidebar_draw_map = {
            SimulationMode.KINEMATICS_3D: self._draw_sidebar_kinematics,
            SimulationMode.KINETIC_2D: self._draw_sidebar_kinematics,
            SimulationMode.CIRCUITS: self._draw_sidebar_circuits,
            SimulationMode.OPTICS: self._draw_sidebar_optics,
            SimulationMode.FIELDS: self._draw_sidebar_fields
        }

    def is_over_ui(self, mouse_pos: pr.Vector2) -> bool:
        """Returns True if mouse is positioned over any visible workspace UI element or dropdown."""
        sw = pr.get_screen_width() or 1280
        sh = pr.get_screen_height() or 720
        
        if self.show_top_bar and mouse_pos.y < 40:
            return True
        if self.show_bottom_bar and mouse_pos.y > sh - 50:
            return True
        if self.show_sidebar:
            if self.sidebar_position == 'left' and mouse_pos.x < 250:
                return True
            if self.sidebar_position == 'right' and mouse_pos.x > sw - 250:
                return True
        if self.active_dropdown in self.dropdown_rects:
            if pr.check_collision_point_rec(mouse_pos, self.dropdown_rects[self.active_dropdown]):
                return True
        return False

    def update_and_draw(self) -> None:
        sw = pr.get_screen_width() or 1280
        sh = pr.get_screen_height() or 720
        mouse_pos = pr.get_mouse_position()
        
        # Close dropdown if clicked outside
        if self.active_dropdown and pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT):
            if not self.is_over_ui(mouse_pos):
                self.active_dropdown = None

        # 1. Draw Top Bar
        if self.show_top_bar:
            pr.draw_rectangle(0, 0, sw, 40, Colors.UI_PANEL)
            pr.draw_line(0, 40, sw, 40, Colors.UI_BORDER)
            
            # Dropdown toggle buttons
            if self.btn_top_file.update_and_draw():
                self.active_dropdown = 'file' if self.active_dropdown != 'file' else None
            if self.btn_top_mode.update_and_draw():
                self.active_dropdown = 'mode' if self.active_dropdown != 'mode' else None
            if self.btn_top_view.update_and_draw():
                self.active_dropdown = 'view' if self.active_dropdown != 'view' else None
                
            # Mode info & FPS readout on right side
            mode_names = {
                SimulationMode.KINEMATICS_3D: "3D Kinematics",
                SimulationMode.KINETIC_2D: "2D Kinetics",
                SimulationMode.CIRCUITS: "DC Circuits",
                SimulationMode.OPTICS: "Ray Optics",
                SimulationMode.FIELDS: "Electromagnetic Fields"
            }
            title_str = f"Active Domain: {mode_names.get(self.app.sim_mode, 'Unknown')}"
            pr.draw_text(title_str, sw - 320, 12, 16, Colors.UI_ACTIVE)
            pr.draw_fps(sw - 90, 10)

        # 2. Draw Sidebar
        sb_x = 0 if self.sidebar_position == 'left' else sw - 250
        if self.show_sidebar:
            sb_y = 40 if self.show_top_bar else 0
            sb_h = sh - sb_y - (50 if self.show_bottom_bar else 0)
            pr.draw_rectangle(sb_x, sb_y, 250, sb_h, Colors.UI_PANEL)
            border_x = 250 if self.sidebar_position == 'left' else sb_x
            pr.draw_line(border_x, sb_y, border_x, sb_y + sb_h, Colors.UI_BORDER)
            
            # Upper Half: Contextual Spawning Tools
            pr.draw_text("SPAWNING TOOLS", sb_x + 15, sb_y + 15, 16, Colors.UI_ACTIVE)
            pr.draw_line(sb_x + 15, sb_y + 38, sb_x + 235, sb_y + 38, Colors.UI_BORDER)
            
            ty = sb_y + 50
            handler = self.sidebar_draw_map.get(self.app.sim_mode)
            if handler:
                handler(sb_x, ty)

            # Lower Half: Object Inspector & Modification
            insp_y = sb_y + 220
            pr.draw_text("OBJECT INSPECTOR", sb_x + 15, insp_y, 16, Colors.UI_ACTIVE)
            pr.draw_line(sb_x + 15, insp_y + 23, sb_x + 235, insp_y + 23, Colors.UI_BORDER)
            
            self._draw_inspector(sb_x + 15, insp_y + 35)

        # 3. Draw Bottom Bar
        if self.show_bottom_bar:
            bb_y = sh - 50
            bb_w = sw - (250 if self.show_sidebar else 0)
            bb_x = 250 if (self.show_sidebar and self.sidebar_position == 'left') else 0
            pr.draw_rectangle(bb_x, bb_y, bb_w, 50, Colors.UI_PANEL)
            pr.draw_line(bb_x, bb_y, bb_x + bb_w, bb_y, Colors.UI_BORDER)
            
            # Position controls
            self.btn_play.rect.x, self.btn_play.rect.y = bb_x + 20, bb_y + 8
            self.btn_stop.rect.x, self.btn_stop.rect.y = bb_x + 140, bb_y + 8
            self.btn_rewind.rect.x, self.btn_rewind.rect.y = bb_x + 250, bb_y + 8
            self.slider_gravity.rect.x, self.slider_gravity.rect.y = bb_x + bb_w - 200, bb_y + 25
            
            is_rewind_hovered = pr.check_collision_point_rec(mouse_pos, self.btn_rewind.rect)
            if self.btn_play.update_and_draw():
                self.app.sim.toggle_play()
            if self.btn_stop.update_and_draw():
                self.app.sim.stop()
                self.app.trails.clear()
            if self.btn_rewind.update_and_draw():
                self.app.sim.rewind(steps=60)
            elif is_rewind_hovered and pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT):
                self.app.sim.rewind(steps=5)
                
            self.slider_gravity.update_and_draw()

        # 4. Draw Unfolding Dropdowns (Always rendered on top of everything)
        handler = self.dropdown_draw_map.get(self.active_dropdown)
        if handler:
            handler()

    def _draw_dropdown_file(self) -> None:
        pr.draw_rectangle(10, 40, 160, 215, Colors.UI_PANEL)
        pr.draw_rectangle_lines(10, 40, 160, 215, Colors.UI_BORDER)
        if self.btn_f_new.update_and_draw():
            self.app.main_menu.show_new_sim_modal = True
            self.app.current_screen = AppScreen.MAIN_MENU
            self.active_dropdown = None
        if self.btn_f_load.update_and_draw():
            self.app.load_scenario_screen.refresh_list()
            self.app.current_screen = AppScreen.LOAD_SCENARIO
            self.active_dropdown = None
        if self.btn_f_save.update_and_draw():
            self.app.scenarios.save_scenario(self.app.active_scenario_name, self.app.sim.scene)
            self.active_dropdown = None
        if self.btn_f_menu.update_and_draw():
            self.app.current_screen = AppScreen.MAIN_MENU
            self.active_dropdown = None
        if self.btn_f_quit.update_and_draw():
            self.app.should_quit = True
            self.active_dropdown = None

    def _draw_dropdown_mode(self) -> None:
        pr.draw_rectangle(100, 40, 180, 215, Colors.UI_PANEL)
        pr.draw_rectangle_lines(100, 40, 180, 215, Colors.UI_BORDER)
        if self.btn_m_3d.update_and_draw():
            self.app.switch_mode(SimulationMode.KINEMATICS_3D)
            self.active_dropdown = None
        if self.btn_m_2d.update_and_draw():
            self.app.switch_mode(SimulationMode.KINETIC_2D)
            self.active_dropdown = None
        if self.btn_m_circ.update_and_draw():
            self.app.switch_mode(SimulationMode.CIRCUITS)
            self.active_dropdown = None
        if self.btn_m_opt.update_and_draw():
            self.app.switch_mode(SimulationMode.OPTICS)
            self.active_dropdown = None
        if self.btn_m_fld.update_and_draw():
            self.app.switch_mode(SimulationMode.FIELDS)
            self.active_dropdown = None

    def _draw_dropdown_view(self) -> None:
        pr.draw_rectangle(210, 40, 150, 115, Colors.UI_PANEL)
        pr.draw_rectangle_lines(210, 40, 150, 115, Colors.UI_BORDER)
        if self.btn_v_grid.update_and_draw():
            self.app.grid.show_grid = not self.app.grid.show_grid
            self.active_dropdown = None
        if self.btn_v_axis.update_and_draw():
            self.app.axis_indicator.show = getattr(self.app.axis_indicator, 'show', True)
            self.active_dropdown = None
        if self.btn_v_settings.update_and_draw():
            self.app.current_screen = AppScreen.SETTINGS
            self.active_dropdown = None

    def _draw_inspector(self, ix: int, iy: int) -> None:
        mode = self.app.sim_mode
        obj = self.app.selected_shape
        if not obj:
            pr.draw_text("No object selected.", ix, iy, 14, Colors.TEXT)
            pr.draw_text("Click an item on canvas", ix, iy + 20, 14, Colors.GRID_MAJOR)
            return

        pr.draw_text(f"Selected: {getattr(obj, 'shape_id', getattr(obj, 'elem_id', getattr(obj, 'comp_id', getattr(obj, 'source_id', 'Item'))))}", ix, iy, 15, Colors.TEXT)
        
        self.btn_remove_obj.rect.x, self.btn_remove_obj.rect.y = ix, iy + 140
        if self.btn_remove_obj.update_and_draw():
            collections_map = {
                SimulationMode.KINEMATICS_3D: [self.app.sim.scene.shapes],
                SimulationMode.KINETIC_2D: [self.app.sim.scene.shapes],
                SimulationMode.CIRCUITS: [self.app.circuit_scene.components],
                SimulationMode.OPTICS: [self.app.optics_scene.elements, self.app.optics_scene.emitters],
                SimulationMode.FIELDS: [self.app.fields_scene.sources]
            }
            for coll in collections_map.get(mode, []):
                if obj in coll:
                    coll.remove(obj)
                    break
            self.app.selected_shape = None
            return

        # Interactive modification sliders depending on object attributes
        if hasattr(obj, 'mass'):
            if self.slider_prop1.label != "Mass (kg)":
                self.slider_prop1 = Slider(ix, iy + 45, 220, 14, "Mass (kg)", 0.1, 50.0, obj.mass)
            obj.mass = self.slider_prop1.update_and_draw()
            
        if hasattr(obj, 'restitution'):
            if self.slider_prop2.label != "Bounciness":
                self.slider_prop2 = Slider(ix, iy + 90, 220, 14, "Bounciness", 0.0, 1.0, obj.restitution)
            obj.restitution = self.slider_prop2.update_and_draw()
            
        elif hasattr(obj, 'val'): # Circuit component or field source
            lbl = "Voltage (V)" if getattr(obj, 'comp_type', '') == 'battery' else ("Resistance (Ω)" if hasattr(obj, 'comp_type') else "Value")
            if self.slider_prop1.label != lbl:
                self.slider_prop1 = Slider(ix, iy + 45, 220, 14, lbl, 0.1, 100.0, obj.val)
            obj.val = self.slider_prop1.update_and_draw()
            
        elif hasattr(obj, 'param1'): # Optical element
            lbl = "Angle (°)" if obj.elem_type == 'mirror' else "Focal Len"
            if self.slider_prop1.label != lbl:
                self.slider_prop1 = Slider(ix, iy + 45, 220, 14, lbl, -180.0, 180.0, obj.param1)
            obj.param1 = self.slider_prop1.update_and_draw()

    def _draw_sidebar_kinematics(self, sb_x: int, ty: int) -> None:
        self.btn_s_sphere.rect.x, self.btn_s_sphere.rect.y = sb_x + 15, ty
        self.btn_s_cube.rect.x, self.btn_s_cube.rect.y = sb_x + 130, ty
        self.btn_s_clear.rect.x, self.btn_s_clear.rect.y = sb_x + 15, ty + 42
        
        if self.btn_s_sphere.update_and_draw():
            self.app.placement_mode = "sphere"
            self.app.spawn_height = 5.0
        if self.btn_s_cube.update_and_draw():
            self.app.placement_mode = "cube"
            self.app.spawn_height = 5.0
        if self.btn_s_clear.update_and_draw():
            self.app.sim.clear_shapes()
            self.app.trails.clear()
            self.app.selected_shape = None

    def _draw_sidebar_circuits(self, sb_x: int, ty: int) -> None:
        self.btn_c_wire.rect.x, self.btn_c_wire.rect.y = sb_x + 15, ty
        self.btn_c_bat.rect.x, self.btn_c_bat.rect.y = sb_x + 130, ty
        self.btn_c_res.rect.x, self.btn_c_res.rect.y = sb_x + 15, ty + 38
        self.btn_c_sw.rect.x, self.btn_c_sw.rect.y = sb_x + 130, ty + 38
        self.btn_c_bulb.rect.x, self.btn_c_bulb.rect.y = sb_x + 15, ty + 76
        self.btn_s_clear.rect.x, self.btn_s_clear.rect.y = sb_x + 15, ty + 114
        
        if self.btn_c_wire.update_and_draw(): self.app.circuit_renderer.active_comp_type = 'wire'
        if self.btn_c_bat.update_and_draw(): self.app.circuit_renderer.active_comp_type = 'battery'
        if self.btn_c_res.update_and_draw(): self.app.circuit_renderer.active_comp_type = 'resistor'
        if self.btn_c_sw.update_and_draw(): self.app.circuit_renderer.active_comp_type = 'switch'
        if self.btn_c_bulb.update_and_draw(): self.app.circuit_renderer.active_comp_type = 'bulb'
        if self.btn_s_clear.update_and_draw(): self.app.circuit_scene.clear()

    def _draw_sidebar_optics(self, sb_x: int, ty: int) -> None:
        self.btn_o_emitter.rect.x, self.btn_o_emitter.rect.y = sb_x + 15, ty
        self.btn_o_mirror.rect.x, self.btn_o_mirror.rect.y = sb_x + 15, ty + 42
        self.btn_o_lens.rect.x, self.btn_o_lens.rect.y = sb_x + 130, ty + 42
        self.btn_s_clear.rect.x, self.btn_s_clear.rect.y = sb_x + 15, ty + 84
        
        if self.btn_o_emitter.update_and_draw(): self.app.placement_mode = "emitter"
        if self.btn_o_mirror.update_and_draw(): self.app.placement_mode = "mirror"
        if self.btn_o_lens.update_and_draw(): self.app.placement_mode = "lens"
        if self.btn_s_clear.update_and_draw(): self.app.optics_scene.clear()

    def _draw_sidebar_fields(self, sb_x: int, ty: int) -> None:
        self.btn_fld_pos.rect.x, self.btn_fld_pos.rect.y = sb_x + 15, ty
        self.btn_fld_neg.rect.x, self.btn_fld_neg.rect.y = sb_x + 130, ty
        self.btn_fld_mag.rect.x, self.btn_fld_mag.rect.y = sb_x + 15, ty + 42
        self.btn_s_clear.rect.x, self.btn_s_clear.rect.y = sb_x + 15, ty + 84
        
        if self.btn_fld_pos.update_and_draw(): self.app.placement_mode = "+charge"
        if self.btn_fld_neg.update_and_draw(): self.app.placement_mode = "-charge"
        if self.btn_fld_mag.update_and_draw(): self.app.placement_mode = "magnet"
        if self.btn_s_clear.update_and_draw(): self.app.fields_scene.clear()
