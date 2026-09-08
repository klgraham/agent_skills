# Bundled PR Lens files

This skill includes four files from [coldteadotai/pr-lens](https://github.com/coldteadotai/pr-lens) under the MIT License:

- `graph-document.md`
- `config.md`
- `example.graph.json`
- `../LICENSE.pr-lens`

The files came from commit `b5309c353c79e536a3f6a69713b1b7eb276515a1`. The package versions at that commit were:

- `@coldtea/pr-lens-cli` `0.4.0`
- `@coldtea/pr-lens-agent-skill` `0.2.0`
- graph schema `0.1.1`

To update the bundle, copy the three reference files and the license from `skills/pr-lens` at one upstream commit. Update the commit, package pin, and version notes in this file. Then run `python3 scripts/verify_example.py` and the repository distribution validator.
