import pyray as pr
import math
from typing import Callable, Dict
from Graphics.UI.ui_key_bindings import (
    KeyBindingsManager,
    ACTION_ZOOM_IN,
    ACTION_ZOOM_OUT,
    ACTION_PRESET_DEFAULT,
    ACTION_PRESET_TOP,
    ACTION_PRESET_SIDE,
    ACTION_PRESET_FRONT,
)

class CameraController:
    """Manages an orbital 3D camera with mouse rotation, zoom, pan, and preset views."""
    def __init__(self, target: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0), distance: float = 20.0):
        self.target = pr.Vector3(target.x, target.y, target.z)
        self.distance = distance
        self.yaw   = math.radians(45.0)   # Azimuth angle around Y axis
        self.pitch = math.radians(30.0)   # Elevation angle above XZ plane

        self.camera = pr.Camera3D(
            pr.Vector3(0.0, 0.0, 0.0),
            self.target,
            pr.Vector3(0.0, 1.0, 0.0),
            45.0,
            pr.CameraProjection.CAMERA_PERSPECTIVE
        )
        # Action → handler map built once; looked up dynamically in handle_input
        self._preset_actions: Dict[str, Callable[[], None]] = {
            ACTION_PRESET_DEFAULT: self.set_preset_default,
            ACTION_PRESET_TOP:     self.set_preset_top,
            ACTION_PRESET_SIDE:    self.set_preset_side,
            ACTION_PRESET_FRONT:   self.set_preset_front,
        }
        self.update_camera_vectors()

    @property
    def _preset_keys(self) -> Dict[int, Callable[[], None]]:
        mgr = KeyBindingsManager.get_instance()
        res: Dict[int, Callable[[], None]] = {}
        for action, handler in self._preset_actions.items():
            for key in mgr.get_action_keys(action):
                res[key] = handler
        return res

    def update_camera_vectors(self) -> None:
        """Calculates camera Cartesian coordinates from spherical orbital parameters."""
        # Clamp pitch to prevent flipping
        max_pitch = math.radians(89.0)
        self.pitch = max(-max_pitch, min(max_pitch, self.pitch))

        horizontal_dist = self.distance * math.cos(self.pitch)
        
        self.camera.position = pr.Vector3(
            self.target.x + horizontal_dist * math.sin(self.yaw),
            self.target.y + self.distance * math.sin(self.pitch),
            self.target.z + horizontal_dist * math.cos(self.yaw)
        )
        self.camera.target = self.target

    def handle_input(self) -> None:
        """Processes mouse and keyboard input for interactive camera control."""
        # 1. Orbital Rotation (Right Mouse Button drag or Alt + Left Mouse Button)
        if pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_RIGHT) or (
            pr.is_key_down(pr.KeyboardKey.KEY_LEFT_ALT) and pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT)
        ):
            mouse_delta = pr.get_mouse_delta()
            rot_speed = 0.005
            self.yaw -= mouse_delta.x * rot_speed
            self.pitch += mouse_delta.y * rot_speed
            self.update_camera_vectors()

        # 2. Camera Pan (Middle Mouse Button drag or Shift + Right Mouse Button)
        if pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_MIDDLE) or (
            pr.is_key_down(pr.KeyboardKey.KEY_LEFT_SHIFT) and pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_RIGHT)
        ):
            mouse_delta = pr.get_mouse_delta()
            pan_speed = self.distance * 0.001
            
            # Calculate right vector of camera
            forward = pr.Vector3(
                self.target.x - self.camera.position.x,
                0.0,
                self.target.z - self.camera.position.z
            )
            length = math.sqrt(forward.x**2 + forward.z**2)
            if length > 0.0001:
                forward.x /= length
                forward.z /= length
            right = pr.Vector3(-forward.z, 0.0, forward.x)

            # Pan target along right and up vectors
            self.target.x -= right.x * mouse_delta.x * pan_speed - forward.x * mouse_delta.y * pan_speed
            self.target.z -= right.z * mouse_delta.x * pan_speed - forward.z * mouse_delta.y * pan_speed
            self.update_camera_vectors()

        # 3. Zoom (Mouse Scroll Wheel & Keyboard Actions)
        is_shift = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_SHIFT) or pr.is_key_down(pr.KeyboardKey.KEY_RIGHT_SHIFT)
        wheel_move = 0.0 if is_shift else pr.get_mouse_wheel_move()
        mgr = KeyBindingsManager.get_instance()
        zoom_delta = -wheel_move * 1.5
        if mgr.is_action_down(ACTION_ZOOM_IN):
            zoom_delta -= 30.0 * max(0.001, pr.get_frame_time())
        if mgr.is_action_down(ACTION_ZOOM_OUT):
            zoom_delta += 30.0 * max(0.001, pr.get_frame_time())

        if zoom_delta != 0.0:
            self.distance = max(2.0, min(150.0, self.distance + zoom_delta))
            self.update_camera_vectors()

        # 4. View Presets (Keys 1–4) — dispatch table lookup
        for action, preset_fn in self._preset_actions.items():
            if mgr.is_action_pressed(action):
                preset_fn()
                break

    def set_preset_default(self) -> None:
        self.target = pr.Vector3(0.0, 1.0, 0.0)
        self.yaw = math.radians(45.0)
        self.pitch = math.radians(30.0)
        self.distance = 20.0
        self.update_camera_vectors()

    def set_preset_top(self) -> None:
        self.target = pr.Vector3(0.0, 0.0, 0.0)
        self.yaw = math.radians(0.0)
        self.pitch = math.radians(88.9)
        self.distance = 25.0
        self.update_camera_vectors()

    def set_preset_side(self) -> None:
        self.target = pr.Vector3(0.0, 1.0, 0.0)
        self.yaw = math.radians(90.0)
        self.pitch = math.radians(5.0)
        self.distance = 20.0
        self.update_camera_vectors()

    def set_preset_front(self) -> None:
        self.target = pr.Vector3(0.0, 1.0, 0.0)
        self.yaw = math.radians(0.0)
        self.pitch = math.radians(5.0)
        self.distance = 20.0
        self.update_camera_vectors()
