import pyray as pr
from Graphics.Rendering.render_colors import Colors
from Graphics.UI.ui_elements import Button, Slider, Toggle, UIState
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
        
        # Top Bar Dropdown Triggers — Mode switching is done from the main menu, not mid-simulation
        self.btn_top_file = Button(10, 5, 80, 30, "File ▼")
        self.btn_top_view = Button(100, 5, 80, 30, "View ▼")
        # File Dropdown Items
        self.btn_f_new = Button(10, 40, 160, 32, "New Simulation")
        self.btn_f_load = Button(10, 74, 160, 32, "Load Scenario")
        self.btn_f_save = Button(10, 108, 160, 32, "Save Scenario")
        self.btn_f_menu = Button(10, 142, 160, 32, "Main Menu")
        self.btn_f_quit = Button(10, 176, 160, 32, "Quit App")

        # View Dropdown Items
        self.btn_v_grid = Button(100, 40, 150, 32, "Toggle Grid")
        self.btn_v_axis = Button(100, 74, 150, 32, "Toggle Axis")
        self.btn_v_settings = Button(100, 108, 150, 32, "Settings")
        self.btn_play = Button(0, 0, 110, 34, "Play / Pause")
        self.btn_stop = Button(0, 0, 100, 34, "Stop / Reset")
        self.btn_rewind = Button(0, 0, 130, 34, "<< Rewind (Hold)")
        self.slider_gravity = Slider(0, 0, 180, 14, "Gravity (m/s²)", 0.0, 25.0, 9.81)
        
        # Sidebar Spawning Tools - 3D/2D
        self.btn_s_sphere = Button(0, 0, 105, 32, "+ Sphere")
        self.btn_s_cube = Button(0, 0, 105, 32, "+ Cube")
        self.btn_s_clear = Button(0, 0, 220, 32, "Clear All")
        
        # Sidebar Spawning Tools - Circuits
        self.btn_c_select = Button(0, 0, 220, 30, "Select / Move")
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
        self.btn_toggle_state = Button(0, 0, 220, 30, "Toggle State")
        self.slider_prop1 = Slider(0, 0, 220, 14, "Property 1", -50.0, 50.0, 0.0)
        self.slider_prop2 = Slider(0, 0, 220, 14, "Property 2", -50.0, 50.0, 0.0)

        # Dispatch lookups for clean optimization
        self.dropdown_rects = {
            'file': pr.Rectangle(10, 40, 160, 215),
            'view': pr.Rectangle(100, 40, 150, 115)
        }
        self.dropdown_draw_map = {
            'file': self._draw_dropdown_file,
            'view': self._draw_dropdown_view
        }
        self.sidebar_draw_map = {
            SimulationMode.KINEMATICS_3D: self._draw_sidebar_kinematics,
            SimulationMode.KINETIC_2D: self._draw_sidebar_kinematics,
            SimulationMode.CIRCUITS: self._draw_sidebar_circuits,
            SimulationMode.OPTICS: self._draw_sidebar_optics,
            SimulationMode.FIELDS: self._draw_sidebar_fields
        }
        self.inspector_draw_map = {
            SimulationMode.KINEMATICS_3D: self._inspect_kinematics,
            SimulationMode.KINETIC_2D: self._inspect_kinematics,
            SimulationMode.CIRCUITS: self._inspect_circuits,
            SimulationMode.OPTICS: self._inspect_optics,
            SimulationMode.FIELDS: self._inspect_fields
        }
        # Built once; looked up every frame in update_and_draw
        self._mode_names = {
            SimulationMode.KINEMATICS_3D: "3D Kinematics",
            SimulationMode.KINETIC_2D: "2D Kinetics",
            SimulationMode.CIRCUITS: "DC Circuits",
            SimulationMode.OPTICS: "Ray Optics",
            SimulationMode.FIELDS: "Electromagnetic Fields"
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
            is_inside_dropdown = False
            if self.active_dropdown in self.dropdown_rects:
                is_inside_dropdown = pr.check_collision_point_rec(mouse_pos, self.dropdown_rects[self.active_dropdown])
            clicked_toggle = pr.check_collision_point_rec(mouse_pos, self.btn_top_file.rect) or pr.check_collision_point_rec(mouse_pos, self.btn_top_view.rect)
            if not is_inside_dropdown and not clicked_toggle:
                self.active_dropdown = None

        # 1. Draw Top Bar
        if self.show_top_bar:
            pr.draw_rectangle(0, 0, sw, 40, Colors.UI_PANEL)
            pr.draw_line(0, 40, sw, 40, Colors.UI_BORDER)
            
            # Dropdown toggle buttons
            if self.btn_top_file.update_and_draw():
                self.active_dropdown = 'file' if self.active_dropdown != 'file' else None
            if self.btn_top_view.update_and_draw():
                self.active_dropdown = 'view' if self.active_dropdown != 'view' else None
                
            # Mode info & FPS readout on right side
            title_str = f"Active Domain: {self._mode_names.get(self.app.sim_mode, 'Unknown')}"
            pr.draw_text(title_str, sw - 320, 12, 16, Colors.UI_ACTIVE)
            pr.draw_fps(sw - 90, 10)

        is_over_active_dropdown = False
        if self.active_dropdown and self.active_dropdown in self.dropdown_rects:
            is_over_active_dropdown = pr.check_collision_point_rec(mouse_pos, self.dropdown_rects[self.active_dropdown])

        previous_block_state = UIState.block_interactions
        if is_over_active_dropdown:
            UIState.block_interactions = True

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

        if is_over_active_dropdown:
            UIState.block_interactions = previous_block_state

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

    def _draw_dropdown_view(self) -> None:
        pr.draw_rectangle(100, 40, 150, 115, Colors.UI_PANEL)
        pr.draw_rectangle_lines(100, 40, 150, 115, Colors.UI_BORDER)
        if self.btn_v_grid.update_and_draw():
            self.app.grid.show_grid = not self.app.grid.show_grid
            self.active_dropdown = None
        if self.btn_v_axis.update_and_draw():
            self.app.axis_indicator.show = not getattr(self.app.axis_indicator, 'show', True)
            self.active_dropdown = None
        if self.btn_v_settings.update_and_draw():
            self.app.current_screen = AppScreen.SETTINGS
            self.active_dropdown = None

    @staticmethod
    def _get_obj_id(obj) -> str:
        """Return the best available ID string for any selected object type."""
        for attr in ('shape_id', 'elem_id', 'comp_id', 'source_id'):
            val = getattr(obj, attr, None)
            if val is not None:
                return str(val)
        return 'Item'

    def _draw_inspector(self, ix: int, iy: int) -> None:
        mode = self.app.sim_mode
        obj = self.app.selected_shape
        if not obj:
            pr.draw_text("No object selected.", ix, iy, 14, Colors.TEXT)
            pr.draw_text("Click an item on canvas", ix, iy + 20, 14, Colors.GRID_MAJOR)
            return

        pr.draw_text(f"Selected: {self._get_obj_id(obj)}", ix, iy, 15, Colors.TEXT)
        curr_y = iy + 25

        handler = self.inspector_draw_map.get(mode)
        if handler:
            curr_y = handler(obj, ix, curr_y)

        self.btn_remove_obj.rect.x, self.btn_remove_obj.rect.y = ix, curr_y + 5
        if self.btn_remove_obj.update_and_draw():
            self._remove_selected_object(mode, obj)

    def _remove_selected_object(self, mode: SimulationMode, obj) -> None:
        match mode:
            case SimulationMode.KINEMATICS_3D | SimulationMode.KINETIC_2D:
                if obj in self.app.sim.scene.shapes:
                    self.app.sim.scene.shapes.remove(obj)
            case SimulationMode.CIRCUITS:
                if obj in self.app.circuit_scene.components:
                    self.app.circuit_scene.components.remove(obj)
                if obj in self.app.circuit_scene.nodes:
                    self.app.circuit_scene.nodes.remove(obj)
                    self.app.circuit_scene.components = [c for c in self.app.circuit_scene.components if c.node_a != obj and c.node_b != obj]
                # Clean up orphaned nodes and reset voltages to avoid stale solver states
                active_nodes = {c.node_a for c in self.app.circuit_scene.components} | {c.node_b for c in self.app.circuit_scene.components}
                self.app.circuit_scene.nodes = [n for n in self.app.circuit_scene.nodes if n in active_nodes]
                for n in self.app.circuit_scene.nodes:
                    n.fixed_voltage = False
                    n.voltage = 0.0
                if hasattr(self.app, 'circuit_renderer') and self.app.circuit_renderer:
                    self.app.circuit_renderer.dragging_comp = None
                    self.app.circuit_renderer.dragging_node = None
                    self.app.circuit_renderer.wiring_start_node = None
            case SimulationMode.OPTICS:
                if obj in self.app.optics_scene.elements:
                    self.app.optics_scene.elements.remove(obj)
                if obj in self.app.optics_scene.emitters:
                    self.app.optics_scene.emitters.remove(obj)
            case SimulationMode.FIELDS:
                if obj in self.app.fields_scene.sources:
                    self.app.fields_scene.sources.remove(obj)
        self.app.selected_shape = None

    def _inspect_kinematics(self, obj, ix: int, curr_y: int) -> int:
        if not (hasattr(obj, 'mass') and hasattr(obj, 'restitution')):
            return curr_y
        pr.draw_text(f"Pos: ({obj.pos.x:.1f}, {obj.pos.y:.1f}) m", ix, curr_y, 14, Colors.GRID_MAJOR)
        curr_y += 18
        pr.draw_text(f"Speed: {obj.speed:.2f} m/s", ix, curr_y, 14, Colors.GRID_MAJOR)
        curr_y += 24

        if self.slider_prop1.label != "Mass (kg)":
            self.slider_prop1 = Slider(ix, curr_y, 220, 14, "Mass (kg)", 0.1, 50.0, obj.mass)
        if not self.slider_prop1.dragging:
            self.slider_prop1.value = obj.mass
        self.slider_prop1.rect.x, self.slider_prop1.rect.y = ix, curr_y
        obj.mass = self.slider_prop1.update_and_draw()
        curr_y += 45

        if self.slider_prop2.label != "Bounciness":
            self.slider_prop2 = Slider(ix, curr_y, 220, 14, "Bounciness", 0.0, 1.0, obj.restitution)
        if not self.slider_prop2.dragging:
            self.slider_prop2.value = obj.restitution
        self.slider_prop2.rect.x, self.slider_prop2.rect.y = ix, curr_y
        obj.restitution = self.slider_prop2.update_and_draw()
        return curr_y + 45

    def _inspect_circuits(self, obj, ix: int, curr_y: int) -> int:
        if getattr(obj, 'comp_type', None) is None:
            return curr_y
        pr.draw_text(f"Type: {obj.comp_type.upper()}", ix, curr_y, 14, Colors.GRID_MAJOR)
        curr_y += 18
        pr.draw_text(f"Current: {abs(obj.current):.3f} A", ix, curr_y, 14, Colors.GRID_MAJOR)
        curr_y += 24

        pr.draw_text(f"Type: {obj.comp_type.upper()}", ix, curr_y, 14, Colors.GRID_MAJOR)
        curr_y += 24
        match obj.comp_type:
            case 'switch':
                state_str = "CLOSED" if obj.state else "OPEN"
                self.btn_toggle_state.text = f"Switch: {state_str}"
                self.btn_toggle_state.rect.x, self.btn_toggle_state.rect.y = ix, curr_y
                if self.btn_toggle_state.update_and_draw():
                    obj.state = not obj.state
                return curr_y + 40
            case 'battery' | 'resistor' | 'bulb':
                lbl = "Voltage (V)" if obj.comp_type == 'battery' else "Resistance (Ω)"
                max_v = 100.0 if obj.comp_type == 'battery' else 500.0
                if self.slider_prop1.label != lbl:
                    self.slider_prop1 = Slider(ix, curr_y, 220, 14, lbl, 0.1, max_v, obj.val)
                if not self.slider_prop1.dragging:
                    self.slider_prop1.value = obj.val
                self.slider_prop1.rect.x, self.slider_prop1.rect.y = ix, curr_y
                obj.val = self.slider_prop1.update_and_draw()
                return curr_y + 45
            case 'wire':
                pr.draw_text(f"Current: {obj.current:.3f} A", ix, curr_y, 14, pr.SKYBLUE)
                return curr_y + 25
            case _:
                return curr_y

    def _inspect_optics(self, obj, ix: int, curr_y: int) -> int:
        if hasattr(obj, 'angle_deg'): # LaserEmitter
            pr.draw_text("Type: LASER EMITTER", ix, curr_y, 14, Colors.GRID_MAJOR)
            curr_y += 24
            if self.slider_prop1.label != "Angle (°)":
                self.slider_prop1 = Slider(ix, curr_y, 220, 14, "Angle (°)", -180.0, 180.0, obj.angle_deg)
            if not self.slider_prop1.dragging:
                self.slider_prop1.value = obj.angle_deg
            self.slider_prop1.rect.x, self.slider_prop1.rect.y = ix, curr_y
            obj.angle_deg = self.slider_prop1.update_and_draw()
            return curr_y + 45
        if getattr(obj, 'elem_type', None) is not None:
            pr.draw_text(f"Type: {obj.elem_type.upper()}", ix, curr_y, 14, Colors.GRID_MAJOR)
            curr_y += 24
            lbl = "Angle (°)" if obj.elem_type in ('mirror', 'prism') else "Focal Len"
            min_v, max_v = (-180.0, 180.0) if 'Angle' in lbl else (-10.0, 10.0)
            if self.slider_prop1.label != lbl:
                self.slider_prop1 = Slider(ix, curr_y, 220, 14, lbl, min_v, max_v, obj.param1)
            if not self.slider_prop1.dragging:
                self.slider_prop1.value = obj.param1
            self.slider_prop1.rect.x, self.slider_prop1.rect.y = ix, curr_y
            obj.param1 = self.slider_prop1.update_and_draw()
            return curr_y + 45
        return curr_y

    def _inspect_fields(self, obj, ix: int, curr_y: int) -> int:
        if getattr(obj, 'source_type', None) is None:
            return curr_y
        pr.draw_text(f"Source: {obj.source_type.upper()}", ix, curr_y, 14, Colors.GRID_MAJOR)
        curr_y += 24
        lbl = "Strength"
        if self.slider_prop1.label != lbl:
            self.slider_prop1 = Slider(ix, curr_y, 220, 14, lbl, -20.0, 20.0, obj.val)
        if not self.slider_prop1.dragging:
            self.slider_prop1.value = obj.val
        self.slider_prop1.rect.x, self.slider_prop1.rect.y = ix, curr_y
        obj.val = self.slider_prop1.update_and_draw()
        return curr_y + 45

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
        self.btn_c_select.rect.x, self.btn_c_select.rect.y = sb_x + 15, ty
        self.btn_c_wire.rect.x, self.btn_c_wire.rect.y = sb_x + 15, ty + 38
        self.btn_c_bat.rect.x, self.btn_c_bat.rect.y = sb_x + 130, ty + 38
        self.btn_c_res.rect.x, self.btn_c_res.rect.y = sb_x + 15, ty + 76
        self.btn_c_sw.rect.x, self.btn_c_sw.rect.y = sb_x + 130, ty + 76
        self.btn_c_bulb.rect.x, self.btn_c_bulb.rect.y = sb_x + 15, ty + 114
        self.btn_s_clear.rect.x, self.btn_s_clear.rect.y = sb_x + 130, ty + 114
        
        if self.btn_c_select.update_and_draw(): self.app.circuit_renderer.active_comp_type = 'select'
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
