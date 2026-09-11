# Coupling and cohesion

Evaluate:

- temporal coupling: components must be available at the same time;
- deployment coupling: components must release together;
- schema coupling: consumers depend on internal data shape;
- storage coupling: components mutate the same database or files;
- behavioral coupling: undocumented ordering or side effects are required;
- organizational coupling: changes require cross-team manual coordination.

Ask whether components can evolve, fail, test, deploy, and recover independently where independence is valuable.

Do not assume all coupling is bad. Essential domain invariants may require tight coupling. Determine whether coupling is deliberate, visible, governed, and owned.
