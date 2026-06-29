import unittest
from Simulation.sim_circuits import CircuitScene, CircuitSolver

class TestCircuitSimulation(unittest.TestCase):
    def test_default_circuit_current(self):
        scene = CircuitScene()
        scene.create_default_circuit()
        CircuitSolver.step(scene, iterations=100)

        # 9V battery across switch (0.001) + bulb (15) + wire (0.001) + bat_int (0.01) ~ 15.012 ohms
        # Expected current ~ 9.0 / 15.012 ~ 0.599 A
        bulb = next(c for c in scene.components if c.comp_type == 'bulb')
        self.assertGreater(abs(bulb.current), 0.55)
        self.assertLess(abs(bulb.current), 0.65)

    def test_open_switch_zero_current(self):
        scene = CircuitScene()
        scene.create_default_circuit()
        switch = next(c for c in scene.components if c.comp_type == 'switch')
        switch.state = False # Open switch
        CircuitSolver.step(scene, iterations=100)

        bulb = next(c for c in scene.components if c.comp_type == 'bulb')
        self.assertLess(abs(bulb.current), 1e-5)

if __name__ == "__main__":
    unittest.main()
