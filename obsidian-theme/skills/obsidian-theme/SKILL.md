---
name: obsidian-theme
description: Create and publish Obsidian themes using CSS. Use when the user wants to build a new Obsidian theme from scratch, customize the look and feel of Obsidian with CSS variables, add dark/light mode support, style specific UI components, or publish a theme to the Obsidian community theme gallery.
---

# Obsidian Theme Development

Obsidian themes are single-file CSS packages. All styles go in `theme.css`. The theme repository also contains `manifest.json`, `versions.json`, and optional automation scripts.

## Workflow

### 1. Setup Repository

Use [obsidianmd/obsidian-sample-theme](https://github.com/obsidianmd/obsidian-sample-theme) as the template. Clone it, then update `manifest.json`:

```json
{
  "name": "Your Theme Name",
  "version": "1.0.0",
  "minAppVersion": "1.0.0",
  "author": "Your Name",
  "authorUrl": "https://yoursite.com"
}
```

Verify `versions.json` maps the theme version to the minimum compatible Obsidian version:
```json
{
  "1.0.0": "1.0.0"
}
```

### 2. Design the Theme

**All CSS goes in `theme.css` at the repository root.** No build step required—plain CSS only.

Obsidian uses an extensive CSS variable system. Override variables on `body` for global changes:

```css
body {
  /* Colors */
  --color-accent: #7c3aed;
  --color-accent-1: #8b5cf6;
  --color-accent-2: #6d28d9;

  /* Typography */
  --font-text: 'Georgia', serif;
  --font-monospace: 'JetBrains Mono', monospace;
  --font-text-size: 16px;

  /* Spacing / shape */
  --radius-s: 4px;
  --radius-m: 8px;
  --radius-l: 12px;
}
```

**Dark and light mode**: Obsidian applies `.theme-dark` or `.theme-light` to `body`. Target both:

```css
.theme-dark {
  --background-primary: #1e1e2e;
  --background-secondary: #181825;
  --text-normal: #cdd6f4;
  --text-muted: #a6adc8;
  --text-faint: #585b70;
}

.theme-light {
  --background-primary: #eff1f5;
  --background-secondary: #e6e9ef;
  --text-normal: #4c4f69;
  --text-muted: #6c6f85;
  --text-faint: #9ca0b0;
}
```

See `references/css-variables.md` for the full variable reference organized by category.

**Test locally**: Copy `theme.css` and `manifest.json` to `<vault>/.obsidian/themes/<Theme Name>/`. In Obsidian: Settings → Appearance → Themes → select your theme.

Use the Obsidian developer console (Cmd+Option+I / Ctrl+Shift+I) to inspect elements and find the right selectors.

### 3. Publish to the Community Gallery

**Prepare a screenshot:**
- File name: anything (e.g., `screenshot.png`)
- Aspect ratio: 16:9
- Recommended size: 512×288px
- Show both dark and light modes if supported

**Create a GitHub Release:**
1. Tag the release with the version number (e.g., `1.0.0`)
2. Upload `manifest.json` and `theme.css` as release assets

**Submit to the theme gallery** via PR to [obsidianmd/obsidian-releases](https://github.com/obsidianmd/obsidian-releases):

Edit `community-themes.json` and add an entry:
```json
{
  "name": "Your Theme Name",
  "author": "Your Name",
  "repo": "github-username/repo-name",
  "screenshot": "screenshot.png",
  "modes": ["dark", "light"]
}
```

`modes` should list `"dark"` and/or `"light"` depending on what your theme supports.

### 4. Release New Versions

1. Update the version in `manifest.json`
2. Run `npm run version` to sync `versions.json` automatically (uses `version-bump.mjs`)
3. Create a new GitHub Release with the new tag
4. Upload the updated `manifest.json` and `theme.css` as assets

`versions.json` must be updated for each release so users on older Obsidian versions don't get incompatible updates:
```json
{
  "1.0.0": "1.0.0",
  "1.1.0": "1.0.0"
}
```

## Key Selectors

| Component | Selector |
|-----------|----------|
| Main editor | `.cm-editor`, `.markdown-source-view` |
| Reading view | `.markdown-reading-view` |
| Sidebar | `.nav-folder`, `.nav-file` |
| Tabs | `.workspace-tab-header` |
| Active tab | `.workspace-tab-header.is-active` |
| Modals | `.modal` |
| Menus | `.menu`, `.menu-item` |
| Headings (preview) | `.markdown-preview-view h1` through `h6` |
| Code blocks | `.HyperMD-codeblock`, `code` |
| Tags | `.tag` |
| Links | `.internal-link`, `.external-link` |
| Callouts | `.callout` |
| Checkboxes | `.task-list-item-checkbox` |

## Resources

- **`references/css-variables.md`**: Full reference of Obsidian CSS variables organized by category (colors, typography, spacing, components). Read when designing a theme or looking up specific variables.
