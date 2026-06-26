import sys
import pyray as pr
from rendering.window import SimulationRenderer

def main() -> None:
    # Initialize Raylib hardware OpenGL window and camera subsystem
    print("[+] Initializing Antigravity Raylib Physics Engine...")
    app = SimulationRenderer(width=1280, height=720)

    # Main synchronous GPU draw loop running until window close signal
    while not pr.window_should_close():
        app.handle_input()
        app.render_frame()

    # Clean uninitialization of OpenGL contexts
    app.cleanup()
    print("[+] Simulation engine shut down cleanly.")
    sys.exit(0)

if __name__ == "__main__":
    main()
