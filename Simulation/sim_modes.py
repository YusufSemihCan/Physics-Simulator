from enum import Enum

class SimulationMode(Enum):
    KINEMATICS_3D = "3D Kinematics & Rigid Bodies"
    KINETIC_2D = "2D Kinetics & Collisions"
    CIRCUITS = "DC Electronics & Circuits"
    OPTICS = "Ray Optics & Lenses"
    FIELDS = "Electromagnetic Fields"
