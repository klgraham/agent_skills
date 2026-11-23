---
name: annotated-equations
description: Add or convert labeled LaTeX equations in Obsidian notes using the Annotated Equations plugin. Use when the user wants to label, explain, or highlight individual terms in an equation, convert existing equation annotations, or check whether the plugin is installed and enabled in a vault.
---

# Annotated equations in Obsidian

## Check the target vault

Identify the vault containing the note. Use its active configuration folder, normally `.obsidian`. If the user uses a custom folder, pass it with `--config-dir`. Do not assume that a plugin enabled in another vault or on another device is enabled here.

Run this read-only check from the skill directory (or invoke the script by its full path):

```sh
python3 scripts/check_plugin.py "/path/to/vault"
python3 scripts/check_plugin.py "/path/to/vault" --config-dir ".obsidian-mobile"
```

If Python isn't available, inspect the same files directly: check `plugins/annotated-equations/` inside the active config folder for nonempty `main.js`, `styles.css`, and a manifest with ID `annotated-equations`. Check whether the ID appears in that config folder's `community-plugins.json`.

- **Installed and listed as enabled:** Use the plugin syntax. Saved settings don't prove the plugin is running. If Obsidian is available, verify the note in Reading view or Live Preview; check Restricted Mode, the active config folder, and app compatibility if it doesn't render. Release 0.1.0 requires Obsidian 1.15.0 or later; the installed manifest supplies its own minimum.
- **Missing, incomplete, disabled, or unknown:** Use the standard math fallback below. If the user asked for the exact plugin format, provide a ready-to-paste block separately and explain what to check under **Settings → Community plugins**. For installation instructions, link the [plugin README](https://github.com/klgraham/obsidian-annotated-equations). Do not install or enable the plugin, change Restricted Mode, or edit configuration as part of a note request.

## Write the equation

Use a fenced `annotated-equation` block **instead of** the usual `$$` delimiters. Wrap only the term each label describes. Keep the original symbols, grouping, signs, alignment, and units. If changing a formula rather than its presentation would be necessary, flag the ambiguity instead of silently correcting it.

```annotated-equation
E = \annotate[above,blue]{\frac{1}{2}mv^2}{Kinetic energy}
  + \annotate[below,teal]{mgh}{Gravitational potential energy}
```

- Syntax: `\annotate[position,color]{LaTeX term}{label}`. Positions are `above` or `below`; colors are `accent`, `blue`, `teal`, `green`, `orange`, `red`, or `purple`. Omit both options for a label below in the theme accent color, or supply just the position.
- Use short plain-text labels or a single math expression wrapped in `$` signs. Keep meanings clear without relying on color alone. Use an `aligned` environment for multiline math.
- When editing a note, change only the intended equation and related explanation. Compare the equation before and after with the annotation wrappers removed; the underlying math should match. Read back the saved Markdown and, when possible, confirm labels and leader lines render without overlap. Distinguish a source check from a visual check.

## Standard math fallback

Use a normal display equation and explain the terms immediately underneath. This also works for notes shared with readers who do not have the plugin.

```markdown
$$
E = \frac{1}{2}mv^2 + mgh
$$

- $\frac{1}{2}mv^2$: kinetic energy.
- $mgh$: gravitational potential energy.
```
