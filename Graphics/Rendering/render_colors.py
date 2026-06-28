import pyray as pr

class Colors:
    # Curated HSL dark mode color palette formatted as Raylib hardware GPU Color structs
    BACKGROUND = pr.Color(24, 26, 31, 255)
    GRID_MAJOR = pr.Color(65, 71, 84, 255)
    GRID_MINOR = pr.Color(40, 44, 52, 255)
    AXIS_X = pr.Color(224, 108, 117, 255)
    AXIS_Y = pr.Color(152, 195, 121, 255)
    AXIS_Z = pr.Color(97, 175, 239, 255)
    SHAPE_ACCENT = pr.Color(229, 192, 123, 255)
    TEXT = pr.Color(209, 213, 219, 255)
    
    # UI Element specific colors
    UI_PANEL = pr.Color(33, 37, 43, 230)
    UI_BORDER = pr.Color(75, 82, 99, 255)
    UI_HOVER = pr.Color(85, 95, 115, 255)
    UI_ACTIVE = pr.Color(97, 175, 239, 255)

    # Physics Visualization Colors
    VECTOR_VELOCITY = pr.Color(86, 182, 194, 255)   # Cyan
    VECTOR_FORCE = pr.Color(224, 108, 117, 255)     # Red/Coral
    VECTOR_ACCEL = pr.Color(198, 120, 221, 255)     # Purple
    TRAIL_DEFAULT = pr.Color(229, 192, 123, 180)    # Gold with transparency
    PARTICLE_SPARK = pr.Color(255, 215, 0, 255)     # Bright yellow

