import pyray as pr
import math
import uuid
from typing import List, Dict, Optional

class CircuitNode:
    __slots__ = ('node_id', 'x', 'y', 'voltage', 'fixed_voltage')

    def __init__(self, x: float, y: float, node_id: Optional[str] = None):
        self.node_id = node_id or str(uuid.uuid4())[:8]
        self.x = x
        self.y = y
        self.voltage = 0.0
        self.fixed_voltage = False

class CircuitComponent:
    __slots__ = ('comp_id', 'comp_type', 'node_a', 'node_b', 'val', 'current', 'state')

    # Fixed resistances for passive component types
    _FIXED_R = {'wire': 0.001, 'battery': 0.01}

    def __init__(self, comp_type: str, node_a: CircuitNode, node_b: CircuitNode, val: float = 10.0):
        self.comp_id = str(uuid.uuid4())[:8]
        self.comp_type = comp_type  # 'battery', 'resistor', 'switch', 'bulb', 'wire'
        self.node_a = node_a
        self.node_b = node_b
        self.val = val  # Voltage for battery, Resistance for others
        self.current = 0.0
        self.state = True  # Closed/Open for switch

    def get_resistance(self) -> float:
        if self.comp_type == 'switch':
            return 0.001 if self.state else 1e9
        fixed = self._FIXED_R.get(self.comp_type)
        if fixed is not None:
            return fixed
        return max(0.01, self.val)

class CircuitScene:
    def __init__(self, name: str = "DC Circuit Lab"):
        self.name = name
        self.nodes: List[CircuitNode] = []
        self.components: List[CircuitComponent] = []

    def add_node(self, x: float, y: float) -> CircuitNode:
        # Check if existing node nearby
        for n in self.nodes:
            if math.hypot(n.x - x, n.y - y) < 0.3:
                return n
        node = CircuitNode(x, y)
        self.nodes.append(node)
        return node

    def add_component(self, comp_type: str, n1: CircuitNode, n2: CircuitNode, val: float = 10.0) -> CircuitComponent:
        comp = CircuitComponent(comp_type, n1, n2, val)
        self.components.append(comp)
        return comp

    def clear(self):
        self.nodes.clear()
        self.components.clear()

    def pick_component(self, x: float, y: float, threshold: float = 0.8):
        for comp in self.components:
            x1, y1 = comp.node_a.x, comp.node_a.y
            x2, y2 = comp.node_b.x, comp.node_b.y
            dx = x2 - x1
            dy = y2 - y1
            l2 = dx*dx + dy*dy
            if l2 == 0:
                dist = math.hypot(x - x1, y - y1)
            else:
                t = max(0.0, min(1.0, ((x - x1)*dx + (y - y1)*dy) / l2))
                dist = math.hypot(x - (x1 + t*dx), y - (y1 + t*dy))
            if dist <= threshold:
                return comp
        return None

    def create_default_circuit(self):
        self.clear()
        # 9V Battery connected to Switch and Bulb
        n1 = self.add_node(-4.0, 2.0)
        n2 = self.add_node(4.0, 2.0)
        n3 = self.add_node(4.0, -2.0)
        n4 = self.add_node(-4.0, -2.0)

        self.add_component('battery', n4, n1, 9.0)   # Left branch: 9V battery
        self.add_component('switch', n1, n2, 1.0)    # Top branch: Switch
        self.add_component('bulb', n2, n3, 15.0)     # Right branch: Bulb (15 ohm)
        self.add_component('wire', n3, n4, 0.0)      # Bottom branch: Wire return

class CircuitSolver:
    @staticmethod
    def step(scene: CircuitScene, iterations: int = 50):
        if not scene.nodes or not scene.components:
            return

        # Ground anchor: set lowest battery negative terminal to 0V
        for comp in scene.components:
            if comp.comp_type == 'battery':
                comp.node_a.voltage = 0.0
                comp.node_a.fixed_voltage = True
                comp.node_b.voltage = comp.val
                comp.node_b.fixed_voltage = True

        # Nodal relaxation solver
        for _ in range(iterations):
            for n in scene.nodes:
                if n.fixed_voltage:
                    continue
                sum_v_over_r = 0.0
                sum_1_over_r = 0.0
                for c in scene.components:
                    r = c.get_resistance()
                    if c.node_a == n:
                        sum_v_over_r += c.node_b.voltage / r
                        sum_1_over_r += 1.0 / r
                    elif c.node_b == n:
                        sum_v_over_r += c.node_a.voltage / r
                        sum_1_over_r += 1.0 / r
                if sum_1_over_r > 0:
                    n.voltage = sum_v_over_r / sum_1_over_r

        # Calculate component currents
        for c in scene.components:
            if c.comp_type == 'battery':
                # Battery current inferred from node_b outgoing current
                tot_i = 0.0
                for other in scene.components:
                    if other == c: continue
                    r = other.get_resistance()
                    if other.node_a == c.node_b:
                        tot_i += (c.node_b.voltage - other.node_b.voltage) / r
                    elif other.node_b == c.node_b:
                        tot_i += (c.node_b.voltage - other.node_a.voltage) / r
                c.current = tot_i
            else:
                r = c.get_resistance()
                c.current = (c.node_a.voltage - c.node_b.voltage) / r
