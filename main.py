import pygame
import random
import numpy as np
from Physics import PhysicsEngine, Body
from Rendering import Renderer

def create_demo_scene(engine, width, height):
    """Fills the simulator engine with initial bodies for demonstration."""
    engine.bodies.clear()
    
    # 1. Add some dynamic balls
    # Large heavy ball
    engine.add_body(Body(
        position=[width // 2, 150],
        velocity=[50, 0],
        mass=50.0,
        radius=40.0,
        elasticity=0.7
    ))
    
    # Fast medium ball
    engine.add_body(Body(
        position=[150, 200],
        velocity=[200, -100],
        mass=10.0,
        radius=20.0,
        elasticity=0.85
    ))

    # Small super-bouncy ball
    engine.add_body(Body(
        position=[width - 150, 250],
        velocity=[-150, 50],
        mass=2.0,
        radius=12.0,
        elasticity=0.95
    ))

    # 2. Add a static barrier in the middle
    engine.add_body(Body(
        position=[width // 2, height // 2 + 50],
        velocity=[0, 0],
        mass=1e9,
        radius=50.0,
        elasticity=0.6,
        is_static=True
    ))

def main():
    # Configuration
    WIDTH = 800
    HEIGHT = 600
    FPS_LIMIT = 60

    renderer = Renderer(width=WIDTH, height=HEIGHT, title="Educational Physics Simulator")
    engine = PhysicsEngine(gravity=(0.0, 500.0), drag=0.05) # Realistic gravity & air resistance

    # Setup demo scene
    create_demo_scene(engine, WIDTH, HEIGHT)

    clock = pygame.time.Clock()
    running = True
    paused = False
    
    # Mouse drag variables for slingshot launching
    drag_start = None
    drag_current = None

    print("--- Physics Simulator Main Initialized ---")
    print("Controls:")
    print("  [SPACE] - Pause / Resume simulation")
    print("  [R]     - Reset simulation to default demo scene")
    print("  [C]     - Clear all dynamic bodies")
    print("  [Left-Click & Drag] - Launch a new body (slingshot)")
    print("  [Right-Click]       - Spawn static circular barrier")

    while running:
        # Time tracking
        dt = clock.tick(FPS_LIMIT) / 1000.0  # Convert milliseconds to seconds
        
        # Limit max time-step to prevent physics explosion during lag spikes
        dt = min(dt, 0.1)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    create_demo_scene(engine, WIDTH, HEIGHT)
                elif event.key == pygame.K_c:
                    # Clear dynamic bodies, keep static ones
                    engine.bodies = [b for b in engine.bodies if b.is_static]
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click (start dragging dynamic ball)
                    drag_start = np.array(event.pos, dtype=np.float64)
                    drag_current = np.array(event.pos, dtype=np.float64)
                elif event.button == 3:  # Right click (spawn static body)
                    engine.add_body(Body(
                        position=event.pos,
                        velocity=[0.0, 0.0],
                        mass=1e9,
                        radius=random.randint(25, 45),
                        elasticity=0.6,
                        is_static=True
                    ))
            
            elif event.type == pygame.MOUSEMOTION:
                if drag_start is not None:
                    drag_current = np.array(event.pos, dtype=np.float64)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drag_start is not None:
                    drag_end = np.array(event.pos, dtype=np.float64)
                    
                    # Launch vector (from drag end to drag start to simulate slingshot pull-back)
                    launch_vector = drag_start - drag_end
                    
                    # Velocity proportional to drag distance (e.g. factor of 3)
                    initial_velocity = launch_vector * 3.5
                    
                    # Randomize size & mass
                    radius = random.uniform(12.0, 25.0)
                    mass = (radius ** 2) * np.pi * 0.01 # Mass proportional to area
                    elasticity = random.uniform(0.7, 0.9)
                    
                    engine.add_body(Body(
                        position=drag_start,
                        velocity=initial_velocity,
                        mass=mass,
                        radius=radius,
                        elasticity=elasticity
                    ))
                    
                    drag_start = None
                    drag_current = None

        # Simulation update
        if not paused:
            engine.step(dt, width=WIDTH, height=HEIGHT)

        # Drawing / Rendering
        renderer.clear()
        
        # Draw physical bodies
        for body in engine.bodies:
            if body.is_static:
                # Static bodies are colored gray/white
                renderer.draw_body(body, body_color=(120, 130, 140))
            else:
                # Dynamic bodies colored light blue
                renderer.draw_body(body, body_color=(80, 160, 240))

        # Visual indicator for slingshot launch
        if drag_start is not None and drag_current is not None:
            # Draw line representing pullback vector
            pygame.draw.line(renderer.screen, (255, 200, 50), drag_start.astype(int), drag_current.astype(int), 3)
            # Draw preview ball at launch position
            pygame.draw.circle(renderer.screen, (255, 200, 50, 128), drag_start.astype(int), 15, 2)

        # Text Overlay
        active_fps = int(clock.get_fps())
        renderer.draw_text(f"FPS: {active_fps}", 15, 15)
        renderer.draw_text(f"Bodies: {len(engine.bodies)}", 15, 35)
        state_str = "PAUSED" if paused else "SIMULATING"
        state_color = (255, 100, 100) if paused else (100, 255, 100)
        renderer.draw_text(f"State: {state_str}", 15, 55, color=state_color)
        
        # Help overlay in the bottom corner
        renderer.draw_text("[SPACE] Pause | [R] Reset | [C] Clear Dynamic", 15, HEIGHT - 55)
        renderer.draw_text("[Left-Click + Drag] Slingshot Ball | [Right-Click] Spawn Wall", 15, HEIGHT - 35)

        renderer.update()

    renderer.quit()

if __name__ == "__main__":
    main()
