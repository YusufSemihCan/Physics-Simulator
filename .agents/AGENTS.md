# Physics Simulator - Project Rules & Context

## Project Goals
- **Educational Visualization:** The simulator aims to make difficult-to-understand physics subjects visual and accessible for education.
- **Scientific Tool:** Maintain accuracy and clean architecture so the project can also serve as a reliable scientific tool.

## Team Boundaries & Responsibilities
- **Physics Module:** The user's friend/collaborator is solely responsible for the physics module. **Do not modify or propose changes to the physics module/engine** unless explicitly requested.
- **User's Scope:** The user is responsible for UI rendering and other surrounding application features. Focus all assistance and edits on these areas.

## Version Control Constraints
- **No Automatic Commits:** **Never** run `git commit`, `git push`, or any destructive Git commands without the user's explicit knowledge and approval. Always confirm before committing.

## Optimization Guidelines
- Evaluate the most suitable control structure for each situation (e.g., `match/case`, dictionary dispatch, or concise `if/elif`) based on readability, maintainability, and performance considerations.
- Isolate domain‑specific logic into small helper methods to keep functions short and improve cache locality.
- Avoid repeated calculations inside tight loops; compute values once per frame when possible.
- Use explicit type annotations and avoid dynamic attribute lookups in performance‑critical paths.
- Separate UI rendering from heavy simulation calculations; keep the render loop lightweight.
- Batch file‑system operations (load, rename, save scenarios) to minimize redundant directory scans.
- Prefer lightweight data structures (`dataclasses`, `namedtuple`) over generic dictionaries for simple objects.

## Decision Guidance
- When multiple viable implementation approaches or tools exist, present their advantages and disadvantages before asking the user to decide.
