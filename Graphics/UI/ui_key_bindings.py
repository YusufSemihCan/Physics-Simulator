from typing import Dict, List, Optional
import pyray as pr

ACTION_PLAY_PAUSE = "play_pause"
ACTION_STOP = "stop"
ACTION_TOGGLE_GRID = "toggle_grid"
ACTION_TOGGLE_VECTORS = "toggle_vectors"
ACTION_TOGGLE_TRAILS = "toggle_trails"
ACTION_CYCLE_RES = "cycle_resolution"
ACTION_BORDERLESS = "borderless"

ACTION_ZOOM_IN = "zoom_in"
ACTION_ZOOM_OUT = "zoom_out"

ACTION_PAN_UP = "pan_up"
ACTION_PAN_DOWN = "pan_down"
ACTION_PAN_LEFT = "pan_left"
ACTION_PAN_RIGHT = "pan_right"

ACTION_PRESET_DEFAULT = "preset_default"
ACTION_PRESET_TOP = "preset_top"
ACTION_PRESET_SIDE = "preset_side"
ACTION_PRESET_FRONT = "preset_front"


class KeyBindingsManager:
    """Manages dynamic key bindings and mapping lookup for simulation actions and camera navigation."""
    
    _instance: Optional['KeyBindingsManager'] = None

    def __init__(self) -> None:
        self._bindings: Dict[str, List[int]] = {
            ACTION_PLAY_PAUSE: [pr.KeyboardKey.KEY_P, pr.KeyboardKey.KEY_SPACE],
            ACTION_STOP: [pr.KeyboardKey.KEY_S],
            ACTION_TOGGLE_GRID: [pr.KeyboardKey.KEY_G],
            ACTION_TOGGLE_VECTORS: [pr.KeyboardKey.KEY_V],
            ACTION_TOGGLE_TRAILS: [pr.KeyboardKey.KEY_T],
            ACTION_CYCLE_RES: [pr.KeyboardKey.KEY_R],
            ACTION_BORDERLESS: [pr.KeyboardKey.KEY_F11, pr.KeyboardKey.KEY_B],
            ACTION_ZOOM_IN: [pr.KeyboardKey.KEY_EQUAL, pr.KeyboardKey.KEY_KP_ADD],
            ACTION_ZOOM_OUT: [pr.KeyboardKey.KEY_MINUS, pr.KeyboardKey.KEY_KP_SUBTRACT],
            ACTION_PAN_UP: [pr.KeyboardKey.KEY_W, pr.KeyboardKey.KEY_UP],
            ACTION_PAN_DOWN: [pr.KeyboardKey.KEY_DOWN],  # Note: KEY_S is stop by default
            ACTION_PAN_LEFT: [pr.KeyboardKey.KEY_A, pr.KeyboardKey.KEY_LEFT],
            ACTION_PAN_RIGHT: [pr.KeyboardKey.KEY_D, pr.KeyboardKey.KEY_RIGHT],
            ACTION_PRESET_DEFAULT: [pr.KeyboardKey.KEY_ONE],
            ACTION_PRESET_TOP: [pr.KeyboardKey.KEY_TWO],
            ACTION_PRESET_SIDE: [pr.KeyboardKey.KEY_THREE],
            ACTION_PRESET_FRONT: [pr.KeyboardKey.KEY_FOUR],
        }

        self._action_labels: Dict[str, str] = {
            ACTION_PLAY_PAUSE: "Toggle Play / Pause",
            ACTION_STOP: "Stop Simulator",
            ACTION_TOGGLE_GRID: "Toggle Grid",
            ACTION_TOGGLE_VECTORS: "Toggle Vectors",
            ACTION_TOGGLE_TRAILS: "Toggle Trails",
            ACTION_CYCLE_RES: "Cycle Resolution",
            ACTION_BORDERLESS: "Toggle Borderless",
            ACTION_ZOOM_IN: "Zoom In",
            ACTION_ZOOM_OUT: "Zoom Out",
            ACTION_PAN_UP: "Pan Up",
            ACTION_PAN_DOWN: "Pan Down",
            ACTION_PAN_LEFT: "Pan Left",
            ACTION_PAN_RIGHT: "Pan Right",
            ACTION_PRESET_DEFAULT: "Camera View: Default",
            ACTION_PRESET_TOP: "Camera View: Top",
            ACTION_PRESET_SIDE: "Camera View: Side",
            ACTION_PRESET_FRONT: "Camera View: Front",
        }

        self._key_names: Dict[int, str] = {
            pr.KeyboardKey.KEY_SPACE: "SPACE",
            pr.KeyboardKey.KEY_ESCAPE: "ESC",
            pr.KeyboardKey.KEY_ENTER: "ENTER",
            pr.KeyboardKey.KEY_UP: "UP",
            pr.KeyboardKey.KEY_DOWN: "DOWN",
            pr.KeyboardKey.KEY_LEFT: "LEFT",
            pr.KeyboardKey.KEY_RIGHT: "RIGHT",
            pr.KeyboardKey.KEY_EQUAL: "=",
            pr.KeyboardKey.KEY_MINUS: "-",
            pr.KeyboardKey.KEY_KP_ADD: "NUM +",
            pr.KeyboardKey.KEY_KP_SUBTRACT: "NUM -",
            pr.KeyboardKey.KEY_ONE: "1",
            pr.KeyboardKey.KEY_TWO: "2",
            pr.KeyboardKey.KEY_THREE: "3",
            pr.KeyboardKey.KEY_FOUR: "4",
            pr.KeyboardKey.KEY_F11: "F11",
        }
        # Populate A-Z numbers automatically
        for code in range(pr.KeyboardKey.KEY_A, pr.KeyboardKey.KEY_Z + 1):
            self._key_names[code] = chr(ord('A') + (code - pr.KeyboardKey.KEY_A))

    @classmethod
    def get_instance(cls) -> 'KeyBindingsManager':
        """Returns the singleton instance of the key bindings manager."""
        if cls._instance is None:
            cls._instance = KeyBindingsManager()
        return cls._instance

    def is_action_pressed(self, action: str) -> bool:
        """Checks if any keyboard key associated with the action was pressed this frame."""
        keys = self._bindings.get(action, [])
        return any(pr.is_key_pressed(key) for key in keys)

    def is_action_down(self, action: str) -> bool:
        """Checks if any keyboard key associated with the action is currently held down."""
        keys = self._bindings.get(action, [])
        return any(pr.is_key_down(key) for key in keys)

    def remap_action(self, action: str, new_key: int) -> None:
        """Remaps the specified action to a new primary keyboard key."""
        if action in self._bindings:
            self._bindings[action] = [new_key]

    def get_action_keys(self, action: str) -> List[int]:
        """Returns the list of key codes currently assigned to the action."""
        return list(self._bindings.get(action, []))

    def get_action_label(self, action: str) -> str:
        """Returns the human-readable description for the given action identifier."""
        return self._action_labels.get(action, action)

    def get_key_name(self, key: int) -> str:
        """Returns a user-friendly string representation of a pyray key code."""
        return self._key_names.get(key, f"KEY_{key}")

    def get_all_actions(self) -> List[str]:
        """Returns a list of all customizable action identifiers."""
        return list(self._bindings.keys())
