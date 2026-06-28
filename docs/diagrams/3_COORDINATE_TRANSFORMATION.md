# 3. Coordinate Scaling & Transformation Pipeline

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

## 📋 Future Implementation Plan

### Scientific Scaling System
* [ ] **Coordinate Scaling Manager (`Graphics/Rendering/scale.py`)**: Define standard pixels-per-meter constants (e.g. `PPM = 50.0`), allowing physics formulas to compute in exact meters while expanding visually across any monitor resolution.
* [ ] **Bidirectional Transformers**: Implement `world_to_screen(vec_meters)` and `screen_to_world(vec_pixels)` helper utilities.
* [ ] **Dynamic Viewport Zoom & Pan**: Connect mouse scroll wheel input to adjust `PPM` scale dynamically while maintaining grid line spacing ratios.
