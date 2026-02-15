---
name: obsidian-cli
description: Interact with Obsidian vaults using the Obsidian CLI tool. Read, create, search, and manage notes, tasks, tags, properties, plugins, and more. Use when the user wants to interact with their Obsidian vault from the terminal. Requires the Obsidian app to be running.
---

# Obsidian CLI Skill

## Overview

The Obsidian CLI (`obsidian`) is a command-line tool for interacting with Obsidian vaults. It supports reading/writing notes, searching, managing tasks, tags, properties, plugins, templates, and more. It requires the Obsidian desktop app to be running.

## When to Use This Skill

Use this skill when the user wants to:
- Read, create, edit, or manage notes in their Obsidian vault
- Search their vault for content
- Manage tasks, tags, properties, or bookmarks
- Work with daily notes
- Manage plugins, themes, or snippets
- Interact with Obsidian Sync or Publish
- Execute Obsidian commands from the terminal
- Use developer tools (screenshots, console, eval, DOM inspection)
- Any vault operation that can be done via CLI instead of the Obsidian UI

## Prerequisites

- The Obsidian desktop app must be running. If not running, the first CLI command will launch it.
- The `obsidian` command must be installed and available in PATH.

## Command Syntax

```
obsidian <command> [parameters] [flags]
```

- **Parameters** take values: `parameter=value` or `parameter="value with spaces"`
- **Flags** are boolean switches with no value: `silent`, `overwrite`, `verbose`
- **Multiline content**: Use `\n` for newlines, `\t` for tabs
- **Vault targeting**: Use `vault=<name>` as the **first** parameter to target a specific vault. If cwd is inside a vault, that vault is used by default.
- **File targeting**: Use `file=<name>` (wiki-link style resolution) or `path=<path>` (exact path from vault root). Defaults to the active file if omitted.
- **Copy output**: Add `--copy` to any command to copy output to clipboard.

## Command Reference

### General

| Command | Description |
|---------|-------------|
| `help` | Show all available commands |
| `version` | Show Obsidian version |
| `reload` | Reload the app window |
| `restart` | Restart the app |

### Files and Folders

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `file` | Show file info | `file=`, `path=` |
| `files` | List vault files | `folder=`, `ext=`, `total` |
| `folder` | Show folder info | `path=` (required), `info=files\|folders\|size` |
| `folders` | List vault folders | `folder=`, `total` |
| `open` | Open a file | `file=`, `path=`, `newtab` |
| `create` | Create/overwrite a file | `name=`, `path=`, `content=`, `template=`, `overwrite`, `silent`, `newtab` |
| `read` | Read file contents | `file=`, `path=` |
| `append` | Append to file | `file=`, `path=`, `content=` (required), `inline` |
| `prepend` | Prepend after frontmatter | `file=`, `path=`, `content=` (required), `inline` |
| `move` | Move/rename a file | `file=`, `path=`, `to=` (required) |
| `delete` | Delete a file (trash) | `file=`, `path=`, `permanent` |

### Daily Notes

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `daily` | Open daily note | `paneType=`, `silent` |
| `daily:read` | Read daily note contents | — |
| `daily:append` | Append to daily note | `content=` (required), `inline`, `silent` |
| `daily:prepend` | Prepend to daily note | `content=` (required), `inline`, `silent` |

### Search

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `search` | Search vault | `query=` (required), `path=`, `limit=`, `format=text\|json`, `total`, `matches`, `case` |
| `search:open` | Open search view | `query=` |

### Tasks

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `tasks` | List tasks | `file=`, `path=`, `status=`, `all`, `daily`, `total`, `done`, `todo`, `verbose` |
| `task` | Show/update a task | `ref=path:line`, `file=`, `line=`, `status=`, `toggle`, `daily`, `done`, `todo` |

### Tags

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `tags` | List tags | `file=`, `path=`, `sort=count`, `all`, `total`, `counts` |
| `tag` | Get tag info | `name=` (required), `total`, `verbose` |

### Properties (Frontmatter)

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `properties` | List properties | `file=`, `name=`, `sort=count`, `format=yaml\|tsv`, `all`, `total`, `counts` |
| `property:set` | Set a property | `name=` (required), `value=` (required), `type=`, `file=`, `path=` |
| `property:remove` | Remove a property | `name=` (required), `file=`, `path=` |
| `property:read` | Read a property value | `name=` (required), `file=`, `path=` |

### Links

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `backlinks` | List backlinks | `file=`, `path=`, `counts`, `total` |
| `links` | List outgoing links | `file=`, `path=`, `total` |
| `unresolved` | List unresolved links | `total`, `counts`, `verbose` |
| `orphans` | Files with no incoming links | `total`, `all` |
| `deadends` | Files with no outgoing links | `total`, `all` |

### Outline

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `outline` | Show headings | `file=`, `path=`, `format=tree\|md`, `total` |

### Bookmarks

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `bookmarks` | List bookmarks | `total`, `verbose` |
| `bookmark` | Add a bookmark | `file=`, `subpath=`, `folder=`, `search=`, `url=`, `title=` |

### Templates

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `templates` | List templates | `total` |
| `template:read` | Read template content | `name=` (required), `title=`, `resolve` |
| `template:insert` | Insert into active file | `name=` (required) |

### Plugins

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `plugins` | List installed plugins | `filter=core\|community`, `versions` |
| `plugins:enabled` | List enabled plugins | `filter=core\|community`, `versions` |
| `plugins:restrict` | Toggle restricted mode | `on`, `off` |
| `plugin` | Get plugin info | `id=` (required) |
| `plugin:enable` | Enable a plugin | `id=` (required), `filter=` |
| `plugin:disable` | Disable a plugin | `id=` (required), `filter=` |
| `plugin:install` | Install community plugin | `id=` (required), `enable` |
| `plugin:uninstall` | Uninstall community plugin | `id=` (required) |
| `plugin:reload` | Reload plugin (dev) | `id=` (required) |

### Themes and Snippets

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `themes` | List installed themes | `versions` |
| `theme` | Show active theme | `name=` |
| `theme:set` | Set active theme | `name=` (required) |
| `theme:install` | Install theme | `name=` (required), `enable` |
| `theme:uninstall` | Uninstall theme | `name=` (required) |
| `snippets` | List CSS snippets | — |
| `snippets:enabled` | List enabled snippets | — |
| `snippet:enable` | Enable snippet | `name=` (required) |
| `snippet:disable` | Disable snippet | `name=` (required) |

### Command Palette and Hotkeys

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `commands` | List command IDs | `filter=` |
| `command` | Execute a command | `id=` (required) |
| `hotkeys` | List hotkeys | `total`, `all`, `verbose` |
| `hotkey` | Get hotkey for command | `id=` (required), `verbose` |

### Vault

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `vault` | Show vault info | `info=name\|path\|files\|folders\|size` |
| `vaults` | List known vaults | `total`, `verbose` |

### Workspace

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `workspace` | Show workspace tree | `ids` |
| `workspaces` | List saved workspaces | `total` |
| `workspace:save` | Save workspace | `name=` |
| `workspace:load` | Load workspace | `name=` (required) |
| `workspace:delete` | Delete workspace | `name=` (required) |
| `tabs` | List open tabs | `ids` |
| `tab:open` | Open new tab | `group=`, `file=`, `view=` |
| `recents` | Recently opened files | `total` |

### Aliases

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `aliases` | List aliases | `file=`, `path=`, `all`, `total`, `verbose` |

### Word Count

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `wordcount` | Count words/chars | `file=`, `path=`, `words`, `characters` |

### Sync

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `sync` | Pause/resume sync | `on`, `off` |
| `sync:status` | Show sync status | — |
| `sync:history` | List sync history | `file=`, `path=`, `total` |
| `sync:read` | Read sync version | `file=`, `path=`, `version=` (required) |
| `sync:restore` | Restore sync version | `file=`, `path=`, `version=` (required) |
| `sync:open` | Open sync history | `file=`, `path=` |
| `sync:deleted` | List deleted files in sync | `total` |

### Publish

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `publish:site` | Show publish site info | — |
| `publish:list` | List published files | `total` |
| `publish:status` | List publish changes | `total`, `new`, `changed`, `deleted` |
| `publish:add` | Publish a file | `file=`, `path=`, `changed` |
| `publish:remove` | Unpublish a file | `file=`, `path=` |
| `publish:open` | Open on published site | `file=`, `path=` |

### File History

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `diff` | List/compare versions | `file=`, `path=`, `from=`, `to=`, `filter=local\|sync` |
| `history` | List file recovery versions | `file=`, `path=` |
| `history:list` | List all files with history | — |
| `history:read` | Read a history version | `file=`, `path=`, `version=` |
| `history:restore` | Restore a history version | `file=`, `path=`, `version=` (required) |
| `history:open` | Open file recovery | `file=`, `path=` |

### Bases

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `bases` | List .base files | — |
| `base:views` | List views in base | — |
| `base:create` | Create item in base view | `name=`, `content=`, `silent`, `newtab` |
| `base:query` | Query a base | `file=`, `path=`, `view=`, `format=json\|csv\|tsv\|md\|paths` |

### Random Notes

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `random` | Open random note | `folder=`, `newtab`, `silent` |
| `random:read` | Read random note | `folder=` |

### Unique Notes

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `unique` | Create unique note | `name=`, `content=`, `paneType=`, `silent` |

### Web Viewer

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `web` | Open URL in web viewer | `url=` (required), `newtab` |

### Developer Commands

| Command | Description | Key Parameters |
|---------|-------------|----------------|
| `devtools` | Toggle dev tools | — |
| `dev:debug` | Attach/detach CDP debugger | `on`, `off` |
| `dev:cdp` | Run CDP command | `method=` (required), `params=` |
| `dev:errors` | Show JS errors | `clear` |
| `dev:screenshot` | Take screenshot | `path=` |
| `dev:console` | Show console messages | `limit=`, `level=`, `clear` |
| `dev:css` | Inspect CSS | `selector=` (required), `prop=` |
| `dev:dom` | Query DOM | `selector=` (required), `attr=`, `css=`, `total`, `text`, `inner`, `all` |
| `dev:mobile` | Toggle mobile emulation | `on`, `off` |
| `eval` | Execute JavaScript | `code=` (required) |

## Usage Patterns

### Reading and writing notes

```bash
# Read the active file
obsidian read

# Read a specific file by name
obsidian read file=Recipe

# Read a file by exact path
obsidian read path="Projects/README.md"

# Create a note with content
obsidian create name="Meeting Notes" content="# Meeting\n\nAttendees:\n- Alice\n- Bob"

# Create from template
obsidian create name="Trip to Paris" template=Travel

# Append to a file silently
obsidian append file=Journal content="- Had a great day" silent

# Prepend content after frontmatter
obsidian prepend file=TODO content="- [ ] New urgent task"
```

### Daily notes

```bash
# Open today's daily note
obsidian daily

# Read daily note content
obsidian daily:read

# Add a task to daily note
obsidian daily:append content="- [ ] Buy groceries" silent

# Prepend to daily note
obsidian daily:prepend content="## Morning Review" silent
```

### Searching

```bash
# Search for text
obsidian search query="meeting notes"

# Search with match context
obsidian search query="TODO" matches

# Search in a folder, limited results, as JSON
obsidian search query="api" path=Projects limit=10 format=json

# Get total match count
obsidian search query="TODO" total
```

### Task management

```bash
# List all incomplete tasks
obsidian tasks todo

# List tasks from daily note
obsidian tasks daily

# List all tasks in vault
obsidian tasks all

# List completed tasks
obsidian tasks done

# Toggle a task
obsidian task ref="Recipe.md:8" toggle

# Mark daily note task as done
obsidian task daily line=3 done

# List tasks with file/line info
obsidian tasks verbose
```

### Tags and properties

```bash
# List all tags in vault with counts
obsidian tags all counts

# Get tag info with file list
obsidian tag name=project verbose

# List all properties in vault
obsidian properties all

# Set a property on a file
obsidian property:set name=status value=draft file=MyNote

# Read a property value
obsidian property:read name=status file=MyNote
```

### Vault targeting

```bash
# Target a specific vault
obsidian vault=Notes daily
obsidian vault="My Vault" search query="test"

# Show vault info
obsidian vault
obsidian vault info=path
```

### Developer use

```bash
# Take a screenshot
obsidian dev:screenshot path=screenshot.png

# Execute JavaScript in the Obsidian console
obsidian eval code="app.vault.getFiles().length"

# Reload a plugin being developed
obsidian plugin:reload id=my-plugin

# Show JS errors
obsidian dev:errors
```

## Best Practices

1. **Use `silent` flag** when modifying files programmatically to avoid switching the user's view.
2. **Use `file=` for convenience** (wiki-link resolution) and `path=` for precision (exact path).
3. **Quote values with spaces**: `content="Hello world"`, `name="My Note"`.
4. **Use `\n` for multiline content** in create/append/prepend commands.
5. **Use `--copy`** to pipe results to clipboard when needed.
6. **Use `format=json`** for search results when parsing output programmatically.
7. **Use `total` flag** to get counts instead of full listings.
8. **Use `verbose` flag** to get additional context (file paths, line numbers).
9. **Target vaults explicitly** with `vault=` when cwd isn't inside a vault.
10. **Prefer `toggle` over explicit status** for task completion when you just need to flip state.
