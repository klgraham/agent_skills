---
name: obsidian-bases
description: >
  Expert assistance for Obsidian Bases — the native database/query layer in Obsidian.
  Use this skill whenever the user wants to: create or edit a .base file, write filter
  expressions, build formulas, design table views, embed a base in a note, or query
  vault notes using the Bases syntax. Trigger on keywords like "base file", ".base",
  "Obsidian database", "obsidian query", "bases filter", "bases formula", "create a
  base", "show me my notes as a table", or any request to use Obsidian Bases to
  organize, filter, or display notes. Always use this skill when the user is working
  with Obsidian Bases — even if they just describe the concept without using the
  exact term.
---

# Obsidian Bases Skill

Obsidian Bases is a native Obsidian feature that lets users create structured,
database-like views of their vault using `.base` files. Think of it as a
purpose-built query language for Obsidian — simpler than Dataview, directly
integrated into the app, with no plugin required.

Your job is to help the user write correct, idiomatic `.base` files and embedded
`base` code blocks, and to explain how the system works. The vault's `CLAUDE.md`
ontology is authoritative for what properties notes in this vault actually have —
use it to write relevant, accurate queries.

## What a Base File Is

A `.base` file is valid YAML conforming to the Bases schema. It defines:

- **filters** — which notes to include (global, applied to all views)
- **formulas** — computed properties derived from note/file data
- **properties** — display configuration for columns (e.g. display names)
- **summaries** — custom aggregation formulas
- **views** — how the data is rendered (currently: `table`)

Bases can be opened standalone or **embedded** in any Markdown note.

---

## File Format

Save base files with the `.base` extension. The content is YAML:

```yaml
filters:
  and:
    - file.hasTag("source/paper")
    - 'read != true'
formulas:
  age_days: '(now() - file.ctime) / 86400000'
properties:
  file.name:
    displayName: Title
  formula.age_days:
    displayName: Days Old
views:
  - type: table
    name: Unread Papers
    limit: 50
    order:
      - file.ctime
    summaries:
      formula.age_days: Average
```

---

## Embedding Bases

**In a note (inline code block):**
````
```base
filters:
  and:
    - file.hasTag("Status/Current")
views:
  - type: table
    name: Active Efforts
```
````

**Linking to a standalone .base file:**
```
![[MyBase.base]]
![[MyBase.base#View Name]]   ← opens a specific view by name
```

---

## Filters

Filters narrow the dataset. By default a base includes every file in the vault.
Filters can be applied **globally** (top-level `filters:`) or **per-view** (`views[n].filters:`).
Both levels are ANDed together when evaluating a view.

Filter structure — one of:
- A string (a filter expression): `'status == "done"'`
- An object with key `and`, `or`, or `not` containing a list of sub-filters

```yaml
filters:
  or:
    - file.hasTag("MachineLearning")
    - and:
        - file.hasTag("source/paper")
        - file.hasLink("causal inference")
    - not:
        - file.inFolder("Archive")
```

**Key filter functions** (see `references/functions.md` for the full list):

| Expression | What it does |
|---|---|
| `file.hasTag("tag")` | True if file has `#tag` (including nested like `#tag/sub`) |
| `file.hasLink("Note Title")` | True if file links to that note |
| `file.inFolder("path/to/folder")` | True if file is in that folder or sub-folder |
| `file.hasProperty("prop")` | True if frontmatter has that property |
| `'prop == "value"'` | Compare a note property |
| `'prop != null'` | Check property is present |
| `'file.mtime > now() - "7d"'` | Modified in the last week |

---

## Formulas

Formulas compute derived values for display in views. Define them in the top-level
`formulas:` section; reference them as `formula.name` in views, filters, and other
formulas.

```yaml
formulas:
  days_since_modified: '(now() - file.mtime) / 86400000'
  overdue: 'if(due_date < now() && status != "Done", "⚠️ Overdue", "")'
  full_name: 'first_name + " " + last_name'
```

**Property namespaces in formulas:**
- `status` or `note.status` → frontmatter property `status`
- `file.name`, `file.size`, `file.mtime` → built-in file properties
- `formula.other_formula` → another formula in the same base

**Nested quotes:** YAML requires formula strings to be quoted. When you need a
string literal inside the formula, use the opposite quote style:
- Outer double quotes: `"if(x, 'yes', 'no')"`
- Outer single quotes: `'if(x, "yes", "no")'`

See `references/functions.md` for the complete function reference.

---

## Properties Section

Configure display metadata for columns:

```yaml
properties:
  status:
    displayName: Status
  formula.overdue:
    displayName: "Due?"
  file.ext:
    displayName: Ext
```

Display names appear as column headers in table views. They are not usable in
filters or formulas.

---

## Summaries

Define custom aggregate formulas. In the formula, `values` is the list of all
values for that property across the result set.

```yaml
summaries:
  customMedian: 'values.filter(value.isType("number")).reduce(if(acc == null || value > acc, value, acc), null)'
```

**Built-in summaries** (usable by name in view `summaries:` config):

Numbers: `Average`, `Min`, `Max`, `Sum`, `Range`, `Median`, `Stddev`
Dates: `Earliest`, `Latest`, `Range`
Booleans: `Checked`, `Unchecked`
Any: `Empty`, `Filled`, `Unique`

---

## Views

Each entry in `views:` is a separate rendering of the same data. Currently only
`table` type is supported.

```yaml
views:
  - type: table
    name: "Active Papers"
    limit: 25
    filters:
      and:
        - 'read != true'
    groupBy:
      property: status
      direction: ASC
    order:
      - file.ctime
      - formula.age_days
    summaries:
      formula.age_days: Average
      file.size: Sum
```

Key view options:
- `type` — `table` (only current option)
- `name` — display name; used in `![[File.base#Name]]` embeds
- `limit` — cap number of rows shown
- `filters` — additional filters (ANDed with global filters)
- `groupBy.property` + `groupBy.direction` (`ASC` / `DESC`) — group rows by a property
- `order` — list of properties to sort by
- `summaries` — map of `property: SummaryName` to show aggregations in the footer

---

## The `this` Object

When a base is **embedded in a note**, `this` refers to the embedding note.
When **opened standalone**, `this` refers to the base file itself.
When **in a sidebar**, `this` refers to the active note.

This enables context-aware queries:

```yaml
# Show all notes that link back to the current note (backlinks pane replacement)
filters:
  - file.hasLink(this.file)
```

---

## Vault-Specific Patterns (Metaconcert)

This vault uses a rich frontmatter ontology (see `CLAUDE.md`). Common base patterns:

**All unread papers:**
```yaml
filters:
  and:
    - file.hasTag("source/paper")
    - 'read != true'
```

**Active efforts:**
```yaml
filters:
  and:
    - 'type == "effort"'
    - file.hasTag("Status/Current")
```

**People to follow up with:**
```yaml
filters:
  and:
    - 'type == "person"'
    - 'follow_up == true'
```

**Recent daily notes:**
```yaml
filters:
  and:
    - 'type == "daily"'
    - 'file.ctime > now() - "14d"'
```

**Sources not yet digested:**
```yaml
filters:
  and:
    - 'type == "source"'
    - 'read == true'
    - 'digested != true'
```

---

## Workflow

When helping the user build a base:

1. **Clarify the goal** — What notes should be included? What properties matter?
   What does the user want to see or compute?

2. **Check the vault ontology** — Use `CLAUDE.md` to identify the right `type:`,
   tags, and frontmatter fields for the target note type. Don't invent property
   names that don't exist in the vault.

3. **Start with filters** — Get the right set of notes first, then layer in
   formulas and view configuration.

4. **Write the YAML carefully** — String literals in formulas need proper quoting.
   Filter expressions must be strings (quoted in YAML). Compound filters use
   `and`/`or`/`not` objects containing lists.

5. **Produce the output** — Either as:
   - A standalone `.base` file saved to an appropriate vault location
   - An embedded `base` code block to paste into a note

6. **Explain the key choices** — Briefly note anything non-obvious, especially
   around filter logic and formula syntax.

---

## Common Pitfalls

- **No `from` clause** — Bases always start from all vault files. Use `filters` to restrict.
- **Quoting in YAML** — Formula strings containing `"` need outer `'` quotes and vice versa.
- **`note.` prefix is optional** — `status` and `note.status` are equivalent.
- **`file.backlinks` is expensive** — Doesn't auto-refresh when the vault changes. Prefer
  `file.links` and reverse the lookup when possible.
- **Circular formula references** — A formula can't reference itself, directly or indirectly.
- **Filter vs. formula context** — Filters evaluate to boolean (include/exclude); formulas
  return any value for display.
- **String equality** — Use `==` and `!=`, not `is` or `===`.

---

## Reference Files

- `references/functions.md` — Complete function reference (Global, String, Number, Date,
  List, Link, File, Object, Regexp functions with signatures and examples)
- `references/syntax.md` — Full syntax: operators, types, property namespaces, date
  arithmetic, and annotated complete examples
