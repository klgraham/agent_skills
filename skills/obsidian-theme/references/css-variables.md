# Obsidian CSS Variables Reference

## Table of Contents
1. [Color System](#color-system)
2. [Background Colors](#background-colors)
3. [Text Colors](#text-colors)
4. [Interactive & Accent Colors](#interactive--accent-colors)
5. [Typography](#typography)
6. [Spacing & Sizing](#spacing--sizing)
7. [Border Radius](#border-radius)
8. [Component Variables](#component-variables)
9. [Editor Variables](#editor-variables)

---

## Color System

Obsidian uses a layered color system. Base colors are defined as HSL components so you can shift them consistently.

```css
body {
  --color-red: #e06c75;
  --color-orange: #d19a66;
  --color-yellow: #e5c07b;
  --color-green: #98c379;
  --color-cyan: #56b6c2;
  --color-blue: #61afef;
  --color-purple: #c678dd;
  --color-pink: #ff6ac1;
}
```

Accent color (used for links, active states, highlights):
```css
body {
  --color-accent: #7c3aed;       /* Primary accent */
  --color-accent-1: #8b5cf6;     /* Lighter accent */
  --color-accent-2: #6d28d9;     /* Darker accent */
  --interactive-accent: var(--color-accent);
  --interactive-accent-hover: var(--color-accent-1);
}
```

---

## Background Colors

```css
.theme-dark {
  --background-primary: #1e1e2e;        /* Main editor background */
  --background-primary-alt: #181825;    /* Slight variation of primary */
  --background-secondary: #181825;      /* Sidebars, panels */
  --background-secondary-alt: #11111b;  /* Deeper secondary */
  --background-modifier-border: #313244; /* Borders, dividers */
  --background-modifier-form-field: #1e1e2e;
  --background-modifier-box-shadow: rgba(0,0,0,0.3);
  --background-modifier-success: rgba(152,195,121,0.2);
  --background-modifier-error: rgba(224,108,117,0.2);
  --background-modifier-error-rgb: 224,108,117;
  --background-modifier-cover: rgba(0,0,0,0.6); /* Modal overlay */
}

.theme-light {
  --background-primary: #fafafa;
  --background-primary-alt: #f0f0f0;
  --background-secondary: #ebebeb;
  --background-secondary-alt: #e0e0e0;
  --background-modifier-border: #d0d0d0;
  --background-modifier-form-field: #ffffff;
}
```

---

## Text Colors

```css
.theme-dark {
  --text-normal: #cdd6f4;       /* Primary text */
  --text-muted: #a6adc8;        /* Secondary/muted text */
  --text-faint: #585b70;        /* Very subtle text, placeholders */
  --text-on-accent: #ffffff;    /* Text on accent-colored backgrounds */
  --text-error: #f38ba8;
  --text-warning: #fab387;
  --text-success: #a6e3a1;
  --text-accent: var(--color-accent);        /* Inline accent text */
  --text-accent-hover: var(--color-accent-1);
  --text-selection: rgba(124,58,237,0.3);   /* Selected text highlight */
  --text-highlight-bg: rgba(229,192,123,0.3); /* ==highlighted== text */
}
```

---

## Interactive & Accent Colors

```css
body {
  --interactive-normal: var(--background-secondary);
  --interactive-hover: var(--background-modifier-border);
  --interactive-accent: var(--color-accent);
  --interactive-accent-rgb: 124,58,237;
  --interactive-accent-hover: var(--color-accent-1);
  --interactive-success: #a6e3a1;
}
```

---

## Typography

### Font Families

```css
body {
  --font-interface: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-text: var(--font-interface);          /* Prose/reading text */
  --font-monospace: 'Source Code Pro', monospace; /* Code */
  --font-monospace-override: '';               /* User override */
  --font-text-override: '';                    /* User override */
}
```

### Font Sizes

```css
body {
  --font-smallest: 0.75em;
  --font-smaller: 0.875em;
  --font-small: 0.9em;
  --font-ui-smaller: 11px;
  --font-ui-small: 13px;
  --font-ui-medium: 15px;
  --font-ui-large: 20px;
  --font-text-size: 16px;   /* Base prose size, user-configurable */
}
```

### Heading Sizes

```css
body {
  --h1-size: 2em;
  --h2-size: 1.6em;
  --h3-size: 1.37em;
  --h4-size: 1.25em;
  --h5-size: 1.12em;
  --h6-size: 1em;

  --h1-weight: 700;
  --h2-weight: 600;
  --h3-weight: 600;
  --h4-weight: 600;
  --h5-weight: 600;
  --h6-weight: 600;

  --h1-color: var(--text-normal);
  --h2-color: var(--text-normal);
  --h3-color: var(--text-normal);
  --h4-color: var(--text-normal);
  --h5-color: var(--text-normal);
  --h6-color: var(--text-normal);

  --h1-font: var(--font-text);
  --h2-font: var(--font-text);
  --h3-font: var(--font-text);
  --h4-font: var(--font-text);
  --h5-font: var(--font-text);
  --h6-font: var(--font-text);

  --h1-line-height: 1.2;
  --h2-line-height: 1.2;
  --h3-line-height: 1.3;

  --h1-style: normal;  /* normal | italic */
  --h2-style: normal;
  --h3-style: normal;
}
```

### Line Height & Letter Spacing

```css
body {
  --line-height-normal: 1.5;
  --line-height-tight: 1.3;
  --letter-spacing: 0;
  --line-width: 700px;           /* Max reading line width */
  --line-width-adaptive: 700px;
  --max-width: 100%;
  --max-col-width: 600px;        /* Column width in multi-column layouts */
}
```

---

## Spacing & Sizing

Obsidian uses a base-4 size scale:

```css
body {
  --size-2-1: 2px;
  --size-2-2: 4px;
  --size-2-3: 6px;
  --size-4-1: 8px;
  --size-4-2: 12px;
  --size-4-3: 16px;
  --size-4-4: 20px;
  --size-4-5: 24px;
  --size-4-6: 32px;
  --size-4-7: 40px;
  --size-4-8: 48px;
  --size-4-9: 56px;
  --size-4-10: 64px;
}
```

---

## Border Radius

```css
body {
  --radius-s: 4px;
  --radius-m: 8px;
  --radius-l: 16px;
  --radius-xl: 24px;

  /* Component-specific (inherit from above by default) */
  --input-radius: var(--radius-s);
  --tab-radius-active: var(--radius-s);
  --checkbox-radius: var(--radius-s);
  --toggle-radius: var(--radius-l);
  --toggle-thumb-radius: var(--radius-l);
  --slider-thumb-radius: 50%;
  --button-radius: var(--radius-s);
  --card-radius: var(--radius-m);
  --prompt-radius: var(--radius-m);
  --modal-radius: var(--radius-m);
}
```

---

## Component Variables

### Links

```css
body {
  --link-color: var(--color-accent);
  --link-color-hover: var(--color-accent-1);
  --link-unresolved-color: var(--text-muted);
  --link-unresolved-opacity: 0.7;
  --link-unresolved-decoration-style: dashed;
  --link-unresolved-decoration-color: var(--text-faint);
  --link-external-color: var(--color-accent);
  --link-external-color-hover: var(--color-accent-1);
}
```

### Code

```css
body {
  --code-normal: var(--text-muted);
  --code-background: var(--background-secondary);
  --code-comment: #5c6370;
  --code-function: #61afef;
  --code-important: #c678dd;
  --code-keyword: #c678dd;
  --code-operator: #56b6c2;
  --code-property: #e06c75;
  --code-punctuation: var(--text-muted);
  --code-string: #98c379;
  --code-tag: #e06c75;
  --code-value: #d19a66;
  --code-size: var(--font-smaller);
  --code-radius: var(--radius-s);
  --code-padding: 2px 4px;
}
```

### Callouts

```css
body {
  --callout-radius: var(--radius-m);
  --callout-padding: var(--size-4-3);
  --callout-title-padding: 0;
  --callout-title-size: inherit;
  --callout-content-padding: var(--size-4-1) 0 0;
  --callout-content-background: transparent;

  /* Callout type colors */
  --callout-default: var(--color-blue);
  --callout-info: var(--color-blue);
  --callout-todo: var(--color-blue);
  --callout-tip: var(--color-cyan);
  --callout-success: var(--color-green);
  --callout-question: var(--color-yellow);
  --callout-warning: var(--color-orange);
  --callout-failure: var(--color-red);
  --callout-danger: var(--color-red);
  --callout-bug: var(--color-red);
  --callout-example: var(--color-purple);
  --callout-quote: var(--text-muted);
}
```

### Blockquotes

```css
body {
  --blockquote-border-thickness: 2px;
  --blockquote-border-color: var(--color-accent);
  --blockquote-color: var(--text-muted);
  --blockquote-font-style: italic;
  --blockquote-background-color: transparent;
}
```

### Tables

```css
body {
  --table-background: transparent;
  --table-border-width: 1px;
  --table-border-color: var(--background-modifier-border);
  --table-header-background: var(--background-secondary);
  --table-header-background-hover: var(--background-secondary-alt);
  --table-header-border-width: var(--table-border-width);
  --table-header-border-color: var(--background-modifier-border);
  --table-text-size: inherit;
  --table-column-max-width: none;
  --table-column-alt-background: transparent;
  --table-row-background-hover: transparent;
  --table-row-alt-background: transparent;
  --table-add-button-background: transparent;
  --table-cell-padding: 4px 10px;
}
```

### Tags

```css
body {
  --tag-color: var(--color-accent);
  --tag-background: rgba(124,58,237,0.1);
  --tag-background-hover: rgba(124,58,237,0.2);
  --tag-border-color: transparent;
  --tag-border-width: 0;
  --tag-font-size: var(--font-small);
  --tag-padding: 2px 6px;
  --tag-radius: var(--radius-xl);
  --tag-weight: inherit;
}
```

### Checkboxes & Tasks

```css
body {
  --checkbox-radius: var(--radius-s);
  --checkbox-size: 15px;
  --checkbox-marker-color: var(--text-on-accent);
  --checkbox-color: var(--interactive-accent);
  --checkbox-color-hover: var(--interactive-accent-hover);
  --checkbox-border-color: var(--text-faint);
  --checkbox-border-color-hover: var(--text-muted);
  --checklist-done-decoration: line-through;
  --checklist-done-color: var(--text-faint);
}
```

### Scrollbars

```css
body {
  --scrollbar-active-thumb-bg: rgba(128,128,128,0.4);
  --scrollbar-bg: transparent;
  --scrollbar-thumb-bg: rgba(128,128,128,0.2);
  --scrollbar-thumb-bg-hover: rgba(128,128,128,0.3);
}
```

### Modals & Prompts

```css
body {
  --modal-background: var(--background-primary);
  --modal-border-color: var(--background-modifier-border);
  --modal-border-width: 1px;
  --modal-max-width: 700px;
  --modal-max-height: 80vh;
  --modal-radius: var(--radius-m);
  --prompt-width: 550px;
  --prompt-max-height: 70vh;
}
```

### File Explorer / Navigation

```css
body {
  --nav-item-size: var(--font-ui-small);
  --nav-item-color: var(--text-muted);
  --nav-item-color-hover: var(--text-normal);
  --nav-item-color-active: var(--text-normal);
  --nav-item-color-highlighted: var(--color-accent);
  --nav-item-background-hover: var(--background-modifier-border);
  --nav-item-background-active: var(--background-modifier-border);
  --nav-item-padding: 2px 8px 2px 24px;
  --nav-item-parent-padding: 2px 8px;
  --nav-item-weight: inherit;
  --nav-item-weight-hover: inherit;
  --nav-item-weight-active: inherit;
  --nav-indentation-guide-width: 1px;
  --nav-indentation-guide-color: var(--background-modifier-border);
  --nav-collapse-icon-color: var(--text-faint);
  --nav-collapse-icon-color-collapsed: var(--text-muted);
}
```

---

## Editor Variables

```css
body {
  --caret-color: var(--text-normal);
  --cursor: text;
  --hr-color: var(--background-modifier-border);
  --hr-thickness: 2px;
  --list-indent: 2em;
  --bold-weight: 700;
  --bold-color: inherit;
  --italic-color: inherit;
  --strikethrough-color: inherit;
  --highlight-mix-blend-mode: darken;  /* 'darken' for light, 'lighten' for dark */

  /* Inline title (when shown) */
  --inline-title-color: var(--h1-color);
  --inline-title-font: var(--h1-font);
  --inline-title-size: var(--h1-size);
  --inline-title-style: var(--h1-style);
  --inline-title-variant: normal;
  --inline-title-weight: var(--h1-weight);
  --inline-title-line-height: var(--h1-line-height);
}
```
