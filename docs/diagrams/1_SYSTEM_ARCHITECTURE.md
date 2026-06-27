# 1. System Architecture

This diagram shows the clean separation between the deterministic math engine (`PhysicsEngine`) and the Raylib visual rendering pipeline (`SimulationRenderer`) for educational physics software.

```mermaid
flowchart TD
    App["Application Entry (main.py)"] --> SimLoop["Simulation Loop Controller"]
    
    subgroup_math["Deterministic Physics Layer"]
    SimLoop --> PhysEngine["Physics Engine"]
    PhysEngine --> State["Entities & Bodies (Mass, Pos, Vel)"]
    PhysEngine --> Solver["Integrator / Collision Solver"]
    
    subgroup_render["Visual Rendering Layer (Raylib / GPU)"]
    SimLoop --> Renderer["SimulationRenderer (window.py)"]
    Renderer --> Cam3D["3D Orbital Camera"]
    Renderer --> Cam2D["2D Orthographic Viewport"]
    
    Renderer --> VizSubsystem["Educational Visualization Modules"]
    VizSubsystem --> Vectors["Vector Arrow Renderer (Velocity / Forces)"]
    VizSubsystem --> Trails["Trajectory Trail Renderer"]
    VizSubsystem --> Grid["GridRenderer (grid.py)"]
    VizSubsystem --> HUD["Heads-Up Display (UI / Sliders)"]
```
