# 2. Fixed Timestep Simulation Loop

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
