import pyray as pr
import math

class CameraController:
    """Manages an orbital 3D camera with mouse rotation, zoom, pan, and preset views."""
    def __init__(self, target: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0), distance: float = 20.0):
        self.target = pr.Vector3(target.x, target.y, target.z)
        self.distance = distance
        self.yaw = math.radians(45.0)    # Azimuth angle around Y axis
        self.pitch = math.radians(30.0)  # Elevation angle above XZ plane
        
        self.camera = pr.Camera3D(
            pr.Vector3(0.0, 0.0, 0.0),
            self.target,
            pr.Vector3(0.0, 1.0, 0.0),
            45.0,
            pr.CameraProjection.CAMERA_PERSPECTIVE
        )
        self.update_camera_vectors()

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

        # 3. Zoom (Mouse Scroll Wheel)
        wheel_move = pr.get_mouse_wheel_move()
        if wheel_move != 0:
            zoom_speed = 1.5
            self.distance = max(2.0, min(150.0, self.distance - wheel_move * zoom_speed))
            self.update_camera_vectors()

        # 4. View Presets (Keys 1, 2, 3, 4)
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ONE):
            self.set_preset_default()
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_TWO):
            self.set_preset_top()
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_THREE):
            self.set_preset_side()
        elif pr.is_key_pressed(pr.KeyboardKey.KEY_FOUR):
            self.set_preset_front()

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
