# Obsidian Bases — Syntax Reference

Complete syntax reference for `.base` files and embedded `base` code blocks.

---

## Full Schema Example

```yaml
filters:
  or:
    - file.hasTag("tag")
    - and:
        - file.hasTag("book")
        - file.hasLink("Textbook")
    - not:
        - file.hasTag("book")
        - file.inFolder("Required Reading")
formulas:
  formatted_price: 'if(price, price.toFixed(2) + " dollars")'
  ppu: "(price / age).toFixed(2)"
properties:
  status:
    displayName: Status
  formula.formatted_price:
    displayName: "Price"
  file.ext:
    displayName: Extension
summaries:
  customAverage: 'values.mean().round(3)'
views:
  - type: table
    name: "My table"
    limit: 10
    groupBy:
      property: note.age
      direction: DESC
    filters:
      and:
        - 'status != "done"'
        - or:
            - "formula.ppu > 5"
            - "price > 2.1"
    order:
      - file.name
      - file.ext
      - note.age
      - formula.ppu
      - formula.formatted_price
    summaries:
      formula.ppu: Average
```

---

## Top-Level Keys

| Key | Required | Description |
|---|---|---|
| `filters` | No | Global filter: narrows which files appear in all views |
| `formulas` | No | Map of formula name → expression string |
| `properties` | No | Display configuration for columns |
| `summaries` | No | Custom aggregate formula definitions |
| `views` | No | List of view configurations |

---

## Property Namespaces

Three kinds of properties can be referenced in filters and formulas:

| Prefix | Example | Source |
|---|---|---|
| *(none)* or `note.` | `status`, `note.status` | Note frontmatter |
| `file.` | `file.name`, `file.mtime` | Built-in file metadata |
| `formula.` | `formula.my_calc` | Formulas defined in this base |
| `this.` | `this.file.name` | Properties of the embedding/active file |

---

## Filter Syntax

### Structure

Filters are either:
1. A **string** — a filter expression that evaluates to boolean:
   ```yaml
   filters: 'status == "active"'
   ```

2. A **filter object** — one of `and`, `or`, or `not`, containing a list of sub-filters:
   ```yaml
   filters:
     and:
       - file.hasTag("source/paper")
       - 'read != true'
   ```

### Nesting

Filter objects compose recursively:

```yaml
filters:
  or:
    - file.hasTag("urgent")
    - and:
        - file.hasTag("important")
        - 'priority == "high"'
    - not:
        - file.inFolder("Archive")
```

### Filter Expressions (String Form)

When a filter is a string, it's a boolean expression evaluated per-note:

```
file.hasTag("MachineLearning")
file.inFolder("Atlas/Sources/Papers")
file.hasLink("causal inference")
'type == "effort"'
'read != true'
'priority == "high"'
'file.mtime > now() - "7d"'
'due_date < today()'
file.hasProperty("rating")
```

Note: YAML requires the expression string to be quoted. Use single quotes `'`
for the YAML string when the expression uses double quotes internally.

---

## Formula Syntax

Formulas are JavaScript-like expressions stored as YAML strings.

### Quoting Rules

Formula strings must be quoted in YAML. When the formula itself contains
string literals, use the other quote style for the outer YAML quoting:

```yaml
formulas:
  # Outer single quotes, inner double quotes:
  label: 'if(done, "✓ Done", "Pending")'

  # Outer double quotes, inner single quotes:
  label2: "if(done, '✓ Done', 'Pending')"

  # No inner string literals — either style works:
  age: '(now() - file.ctime) / 86400000'
```

### Referencing Properties

```yaml
formulas:
  # Shorthand (no prefix) = note property:
  total: 'price * quantity'

  # Explicit note prefix:
  total2: 'note.price * note.quantity'

  # File property:
  age_days: '(now() - file.ctime) / 86400000'

  # Another formula:
  total_with_tax: 'formula.total * 1.08'
```

### Formula Output Types

The output type is determined by what the formula computes:
- Arithmetic on numbers → number
- String concatenation → string
- Comparison → boolean
- Date arithmetic → date or number (milliseconds)
- `if()` → whatever the branch returns

---

## Operators

### Arithmetic

| Operator | Meaning |
|---|---|
| `+` | Addition (also string concat and date offset) |
| `-` | Subtraction |
| `*` | Multiply |
| `/` | Divide |
| `%` | Modulo |
| `( )` | Grouping |

### Comparison

| Operator | Meaning |
|---|---|
| `==` | Equal |
| `!=` | Not equal |
| `>` | Greater than |
| `<` | Less than |
| `>=` | Greater than or equal |
| `<=` | Less than or equal |

### Boolean

| Operator | Meaning |
|---|---|
| `!` | Logical NOT |
| `&&` | Logical AND |
| `\|\|` | Logical OR |

---

## Types

### Primitives

| Type | Syntax | Examples |
|---|---|---|
| String | Single or double quotes | `"hello"`, `'world'` |
| Number | Digits, optional decimal | `42`, `3.14`, `(2.5)` |
| Boolean | Unquoted keywords | `true`, `false` |

### Dates

Created by `date()`, `today()`, `now()`, or from frontmatter date properties.

```
date("2025-01-01")         → specific date
date("2025-01-01 12:00")   → date with time
today()                     → today at midnight
now()                       → current datetime
```

### Date Arithmetic

```
now() + "1d"          → tomorrow
now() - "1 week"      → 7 days ago
today() + "1M"        → one month from now
now() + "2h30m"       → 2.5 hours from now
date1 - date2         → milliseconds between dates
(now() - file.ctime) / 86400000   → age in days
```

Duration strings accept: `y/year/years`, `M/month/months`, `d/day/days`,
`w/week/weeks`, `h/hour/hours`, `m/minute/minutes`, `s/second/seconds`.

### Lists

```
[1, 2, 3]                  → list literal
tags                        → list from frontmatter list property
file.links                  → list of links
property[0]                → first element (0-based)
list.length                → element count
```

### Objects

```
property.subprop           → dot access
property["subprop"]        → bracket access
file.properties            → all frontmatter as object
```

### Links

Wikilinks in frontmatter are auto-recognized as Link objects.

```
link("Note Title")         → create a link
link("Note", "display")    → link with custom display text
file.asLink()              → file as link
author == this             → compare link to current file
authors.contains(this)     → check if current file in list
```

---

## Views

### Table View

```yaml
views:
  - type: table
    name: "View Name"              # Used in ![[File.base#View Name]] embeds
    limit: 50                      # Max rows
    groupBy:
      property: status             # Property to group by
      direction: ASC               # ASC or DESC
    filters:                       # View-level filters (ANDed with global)
      and:
        - 'status != "done"'
    order:                         # Sort order (list of properties)
      - file.name
      - formula.score
    summaries:                     # property: SummaryName
      rating: Average
      file.size: Sum
```

### Built-in Summary Names

For use in `views[n].summaries`:

- **Numbers**: `Average`, `Min`, `Max`, `Sum`, `Range`, `Median`, `Stddev`
- **Dates**: `Earliest`, `Latest`, `Range`
- **Booleans**: `Checked`, `Unchecked`
- **Any type**: `Empty`, `Filled`, `Unique`

---

## Embedding Syntax

### Standalone File Reference

```markdown
![[Reports.base]]
![[Reports.base#Unread Papers]]
```

### Inline Code Block

````markdown
```base
filters:
  and:
    - file.hasTag("Status/Current")
views:
  - type: table
    name: Active
```
````

---

## The `this` Context

| Context | `this` points to |
|---|---|
| Embedded in a note | The embedding note |
| Opened standalone | The `.base` file itself |
| Displayed in sidebar | The active file in main area |

```yaml
# Backlinks pane — show all files that link to the current note:
filters:
  - file.hasLink(this.file)

# Show notes in the same folder as the current note:
filters:
  - file.inFolder(this.file.folder)
```

---

## Common Patterns

### Filter by type (Metaconcert vault)

```yaml
filters:
  - 'type == "source"'
```

### Multi-tag filter

```yaml
filters:
  or:
    - file.hasTag("MachineLearning")
    - file.hasTag("CausalInference")
```

### Date range

```yaml
filters:
  and:
    - 'file.mtime > now() - "30d"'
    - 'file.mtime < now()'
```

### Conditional formula with null guard

```yaml
formulas:
  display_rating: 'if(rating, rating.toString() + "/5", "—")'
```

### Age in days

```yaml
formulas:
  age_days: '((now() - file.ctime) / 86400000).round(1)'
```

### Overdue check

```yaml
formulas:
  status_display: 'if(due_date && due_date < now() && status != "Done", "⚠️ Overdue", status)'
```
