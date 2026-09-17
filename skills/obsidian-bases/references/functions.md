# Obsidian Bases — Function Reference

Complete reference for all functions available in Bases filters and formulas.
Functions are called on a value using dot notation: `value.function()`, except
for Global functions which are called without a receiver.

---

## Global Functions

Called without a receiver (not tied to a type).

| Function | Signature | Description |
|---|---|---|
| `if` | `if(condition, trueResult, falseResult?)` | Returns `trueResult` if condition is truthy, else `falseResult` (default `null`) |
| `now` | `now(): date` | Current date and time |
| `today` | `today(): date` | Current date with time set to midnight |
| `date` | `date(string): date` | Parse string as date; format: `"YYYY-MM-DD HH:mm:ss"` |
| `duration` | `duration(string): duration` | Parse string as duration (e.g. `"1d"`, `"2h"`, `"3M"`) |
| `number` | `number(any): number` | Coerce to number; dates → ms since epoch, booleans → 0/1 |
| `list` | `list(element): list` | Wrap a single value in a list; pass-through if already a list |
| `link` | `link(path, display?): Link` | Create a Link object; optional `display` text |
| `file` | `file(path): file` | Return a file object for the given path or link |
| `image` | `image(path): image` | Return an image object for rendering in views |
| `icon` | `icon(name): icon` | Return a Lucide icon by name (e.g. `"arrow-right"`) |
| `html` | `html(string): html` | Render a string as HTML in a view |
| `escapeHTML` | `escapeHTML(string): string` | Escape special HTML characters |
| `max` | `max(n1, n2, ...): number` | Largest of all provided numbers |
| `min` | `min(n1, n2, ...): number` | Smallest of all provided numbers |

**Examples:**
```
if(price, "$" + price.toFixed(2), "—")
if(due_date < now() && status != "Done", "Overdue", "")
now() - "7d"                          → date 7 days ago
today().format("YYYY-MM-DD")          → "2026-02-17"
date("2025-01-01") + "1M"             → 2025-02-01
number("3.14")                        → 3.14
list(tags)                            → wraps single tag string in list
link("My Note", "click here")        → Link object
```

---

## Any

Methods available on any value type.

| Function | Signature | Description |
|---|---|---|
| `isTruthy` | `any.isTruthy(): boolean` | Coerce to boolean |
| `isType` | `any.isType(type: string): boolean` | Check value type (`"string"`, `"number"`, `"boolean"`, `"date"`, `"list"`, `"object"`) |
| `toString` | `any.toString(): string` | String representation of the value |

**Examples:**
```
1.isTruthy()                → true
"".isTruthy()               → false
42.isType("number")         → true
[1,2,3].isType("list")      → true
123.toString()              → "123"
```

---

## Date

Functions for date and datetime values. Dates are created by `date()`, `today()`, `now()`,
or from frontmatter date properties.

**Fields:**

| Field | Type | Description |
|---|---|---|
| `date.year` | number | Year |
| `date.month` | number | Month (1–12) |
| `date.day` | number | Day of month |
| `date.hour` | number | Hour (0–23) |
| `date.minute` | number | Minute (0–59) |
| `date.second` | number | Second (0–59) |
| `date.millisecond` | number | Millisecond (0–999) |

**Methods:**

| Function | Signature | Description |
|---|---|---|
| `date` | `date.date(): date` | Strip time portion (set to midnight) |
| `format` | `date.format(fmt: string): string` | Format using Moment.js format string |
| `time` | `date.time(): string` | Return time as `"HH:mm:ss"` string |
| `relative` | `date.relative(): string` | Human-readable relative (e.g. `"3 days ago"`) |
| `isEmpty` | `date.isEmpty(): boolean` | Always `false` for a date value |

**Date arithmetic:** Add or subtract duration strings with `+` / `-`.

| Unit strings | Meaning |
|---|---|
| `y`, `year`, `years` | year |
| `M`, `month`, `months` | month |
| `d`, `day`, `days` | day |
| `w`, `week`, `weeks` | week |
| `h`, `hour`, `hours` | hour |
| `m`, `minute`, `minutes` | minute |
| `s`, `second`, `seconds` | second |

**Examples:**
```
file.mtime.format("YYYY-MM-DD")       → "2026-02-17"
file.ctime.relative()                 → "2 months ago"
now() - "1 week"                      → date 7 days ago
today() + "30d"                       → date 30 days from now
now().date()                          → today at midnight
now().year                            → 2026
file.mtime > now() - "7d"            → true if modified this week
(now() - file.ctime) / 86400000      → age in days
```

---

## String

Functions for string values.

**Fields:**

| Field | Type | Description |
|---|---|---|
| `string.length` | number | Number of characters |

**Methods:**

| Function | Signature | Description |
|---|---|---|
| `contains` | `string.contains(value): boolean` | True if string contains substring |
| `containsAll` | `string.containsAll(...values): boolean` | True if string contains all substrings |
| `containsAny` | `string.containsAny(...values): boolean` | True if string contains any substring |
| `startsWith` | `string.startsWith(query): boolean` | True if string starts with query |
| `endsWith` | `string.endsWith(query): boolean` | True if string ends with query |
| `isEmpty` | `string.isEmpty(): boolean` | True if empty string or not present |
| `lower` | `string.lower(): string` | Convert to lowercase |
| `title` | `string.title(): string` | Convert to Title Case |
| `trim` | `string.trim(): string` | Remove leading/trailing whitespace |
| `replace` | `string.replace(pattern, replacement): string` | Replace matches; pattern can be string or regexp |
| `split` | `string.split(separator, n?): list` | Split on delimiter; optional max count |
| `slice` | `string.slice(start, end?): string` | Substring from start to end (exclusive) |
| `repeat` | `string.repeat(count): string` | Repeat string N times |
| `reverse` | `string.reverse(): string` | Reverse the string |

**Examples:**
```
title.contains("causal")             → true if title has "causal"
status.isEmpty()                     → true if status not set
file.name.lower()                    → lowercase filename
"hello world".title()               → "Hello World"
" padded ".trim()                   → "padded"
"a:b:c".split(":")                  → ["a","b","c"]
"hello".slice(0, 3)                 → "hel"
"abc".replace("b", "B")            → "aBc"
file.name.startsWith("2026")        → true for files named like "2026-02-17"
```

---

## Number

Functions for numeric values.

| Function | Signature | Description |
|---|---|---|
| `abs` | `number.abs(): number` | Absolute value |
| `ceil` | `number.ceil(): number` | Round up to nearest integer |
| `floor` | `number.floor(): number` | Round down to nearest integer |
| `round` | `number.round(digits?): number` | Round to nearest integer; `digits` for decimal places |
| `toFixed` | `number.toFixed(precision): string` | Fixed-point string with given decimal places |
| `isEmpty` | `number.isEmpty(): boolean` | True if number is not present |

**Examples:**
```
(3.14159).toFixed(2)    → "3.14"
(2.7).round()           → 3
(2.7).floor()           → 2
(2.1).ceil()            → 3
(-5).abs()              → 5
(2.3333).round(2)       → 2.33
```

---

## List

Functions for list/array values.

**Fields:**

| Field | Type | Description |
|---|---|---|
| `list.length` | number | Number of elements |

**Methods:**

| Function | Signature | Description |
|---|---|---|
| `contains` | `list.contains(value): boolean` | True if list contains value |
| `containsAll` | `list.containsAll(...values): boolean` | True if list contains all values |
| `containsAny` | `list.containsAny(...values): boolean` | True if list contains any value |
| `filter` | `list.filter(expr): list` | Keep elements where `value` (current element) satisfies expr; `index` also available |
| `map` | `list.map(expr): list` | Transform each element; `value` = current, `index` = index |
| `reduce` | `list.reduce(expr, acc): any` | Fold; `value` = current, `index` = index, `acc` = accumulator |
| `flat` | `list.flat(): list` | Flatten one level of nesting |
| `sort` | `list.sort(): list` | Sort ascending |
| `reverse` | `list.reverse(): list` | Reverse order |
| `unique` | `list.unique(): list` | Remove duplicates |
| `slice` | `list.slice(start, end?): list` | Sublist from start to end (exclusive) |
| `join` | `list.join(separator): string` | Join elements into a string |
| `isEmpty` | `list.isEmpty(): boolean` | True if list has no elements |

**Examples:**
```
tags.contains("MachineLearning")               → true if tag present
[1,2,3,4].filter(value > 2)                   → [3,4]
[1,2,3].map(value * 2)                        → [2,4,6]
[1,2,3].reduce(acc + value, 0)               → 6
["a","b","b","c"].unique()                    → ["a","b","c"]
attendees.length                              → count of attendees
tags.join(", ")                              → "tag1, tag2"
file.links.map(value.asFile().file.name)     → list of linked file names
```

---

## Link

Functions for Link objects (wikilinks in frontmatter).

| Function | Signature | Description |
|---|---|---|
| `asFile` | `link.asFile(): file` | Resolve the link to a file object |
| `linksTo` | `link.linksTo(file): boolean` | True if the linked file links to another file |

**Notes:**
- Links can be compared with `==` and `!=` (equal if they point to the same file)
- Links can be compared to `file` or `this` objects
- `authors.contains(this)` — check if current file is in a list of links

---

## File

Functions on file objects (the `file` property, or returned by `file()` global).

**Fields:**

| Field | Type | Description |
|---|---|---|
| `file.name` | string | Filename with extension |
| `file.basename` | string | Filename without extension |
| `file.path` | string | Full vault-relative path |
| `file.folder` | string | Folder path |
| `file.ext` | string | File extension |
| `file.size` | number | File size in bytes |
| `file.properties` | object | All frontmatter properties |
| `file.tags` | list | All tags (content + frontmatter) |
| `file.links` | list | All internal links |
| `file.embeds` | list | All embeds |
| `file.ctime` | date | Creation time |
| `file.mtime` | date | Last modified time |
| `file.backlinks` | list | Files linking to this file (**expensive**, no auto-refresh) |
| `file.file` | file | The file object itself (for specific functions) |

**Methods:**

| Function | Signature | Description |
|---|---|---|
| `asLink` | `file.asLink(display?): Link` | Create a Link object from this file |
| `hasLink` | `file.hasLink(otherFile): boolean` | True if file links to `otherFile` |
| `hasTag` | `file.hasTag(...values): boolean` | True if file has any of the given tags (includes nested) |
| `hasProperty` | `file.hasProperty(name): boolean` | True if frontmatter has property |
| `inFolder` | `file.inFolder(folder): boolean` | True if file is in folder or sub-folder |

**Examples:**
```
file.hasTag("source/paper")                  → true for papers
file.hasTag("Status/Current", "Status/Ongoing") → matches either
file.inFolder("Atlas/Sources")               → true for any source
file.hasLink("causal inference")             → links to that note
file.mtime.relative()                        → "3 days ago"
file.size / 1024                             → size in KB
file.asLink(file.basename)                   → link with clean name
```

---

## Object

Functions for key-value objects.

| Function | Signature | Description |
|---|---|---|
| `isEmpty` | `object.isEmpty(): boolean` | True if object has no properties |
| `keys` | `object.keys(): list` | List of keys |
| `values` | `object.values(): list` | List of values |

---

## Regular Expression

Functions for regexp patterns (written as `/pattern/` or `/pattern/flags`).

| Function | Signature | Description |
|---|---|---|
| `matches` | `regexp.matches(value: string): boolean` | True if regexp matches the string |

**Examples:**
```
/^2026/.matches(file.name)            → true if file name starts with "2026"
/causal|inference/i.matches(title)   → case-insensitive match
```
