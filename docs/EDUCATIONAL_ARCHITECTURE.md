# Educational Visual Simulation Architecture

This document outlines the architecture, main loops, coordinate transformations, and interaction workflows for building visual, educational physics programs with Raylib and Python. 

When uploaded to GitHub, these Mermaid diagrams will render automatically as live interactive diagrams.

---

## 1. System Architecture

Shows the clean separation between the deterministic math engine (`PhysicsEngine`) and the Raylib visual rendering pipeline (`SimulationRenderer`).

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

---

## 2. Fixed Timestep Simulation Loop

To ensure scientific accuracy and repeatable educational results regardless of monitor refresh rates (60Hz vs 144Hz), the physics updates run at a constant fixed time step (`FIXED_DT`), decoupled from visual rendering.

```mermaid
flowchart LR
    Start["Frame Start"] --> CalcDT["Calculate Elapsed Time (frame_time)"]
    CalcDT --> AddAcc["Accumulator += frame_time"]
    
    AddAcc --> CheckAcc{"Accumulator >= FIXED_DT?"}
    CheckAcc -- Yes --> PhysStep["Update Physics (step FIXED_DT)"]
    PhysStep --> RecTrail["Record Trajectory Point"]
    RecTrail --> SubAcc["Accumulator -= FIXED_DT"]
    SubAcc --> CheckAcc
    
    CheckAcc -- No --> Interp["Calculate Visual Alpha Interpolation"]
    Interp --> Render["Render Visual Frame (Raylib GPU)"]
    Render --> End["Frame End / Wait Next"]
```

---

## 3. Coordinate Scaling & Transformation Pipeline

Educational programs must bridge the gap between SI units (meters, seconds, kilograms) and monitor screen spaces (pixels).

```mermaid
flowchart TD
    SI["Scientific World Coordinates (e.g. x = 5.0 meters)"] 
    --> Scale["Scale Conversion (e.g. 1 meter = 50 pixels)"]
    
    Scale --> WorldSpace["Virtual World Space (x = 250.0 units)"]
    
    WorldSpace --> CamTransform["Camera Matrix Transformation (2D / 3D Projection)"]
    CamTransform --> ScreenSpace["Screen Space Coordinates (Pixels on Window)"]
    ScreenSpace --> DrawCall["Raylib Hardware Draw Call"]
```

---

## 4. Interactive User Manipulation & Mouse Picking Pipeline

Enabling tactile interactivity (grabbing a ball, dragging vectors, tweaking sliders) follows this input pipeline:

```mermaid
flowchart TD
    Input["User Mouse Click / Drag"] --> GetPos["Get Screen Position (pr.get_mouse_position)"]
    
    GetPos --> ModeCheck{"Current Viewport Mode?"}
    
    ModeCheck -- "2D Mode" --> Unproject2D["Convert Screen to World 2D Point"]
    Unproject2D --> Collide2D["Check Point vs Circle / Bounding Box"]
    
    ModeCheck -- "3D Mode" --> CastRay["Cast Screen-to-World Ray (pr.get_screen_to_world_ray)"]
    CastRay --> Collide3D["Check Ray vs Sphere / Bounding Box Collision"]
    
    Collide2D --> Hit{"Entity Hit?"}
    Collide3D --> Hit
    
    Hit -- Yes --> Attach["Attach Mouse Constraint / Spring to Entity"]
    Attach --> Drag["Update Entity Position / Velocity on Mouse Move"]
    
    Hit -- No --> HUDCheck["Check UI Element / Slider Click"]
```
