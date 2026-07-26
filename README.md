# Agent Skills

Agent Skills for AI coding assistants.

## Skills

| Skill | Description |
|-------|-------------|
| [dynamic-workflow](dynamic-workflow/SKILL.md) | Design and run script-backed multi-agent Codex workflows with isolated workers, structured outputs, verification stages, bounded loops, and resumable checkpoints. |
| [interactive-walkthrough (Codex)](codex/interactive-walkthrough/SKILL.md) | Build evidence-grounded, self-contained interactive HTML walkthroughs of code, repositories, systems, and technical processes using Codex-native browser verification. |
| [interactive-walkthrough (Hermes)](hermes/interactive-walkthrough/SKILL.md) | Original Hermes version of the interactive walkthrough skill. |
| [obsidian-bases](obsidian-bases/SKILL.md) | Expert assistance for Obsidian Bases — the native database/query layer in Obsidian. Create and edit `.base` files, write filter expressions, build formulas, and design table views. |
| [obsidian-cli](obsidian-cli/SKILL.md) | Interact with Obsidian vaults using CLI commands. Read, create, search notes, manage tasks, tags, properties, plugins, and more. 60+ commands for complete vault automation. |
| [obsidian-plugin](obsidian-plugin/SKILL.md) | Build and edit Obsidian plugins using TypeScript and the Obsidian API. Supports plugin development, feature implementation, and publishing workflows. |
| [obsidian-theme](obsidian-theme/SKILL.md) | Create and publish Obsidian themes using CSS. Includes dark/light mode support, CSS variable reference, and community gallery publishing workflow. |
| [zig-programming](zig-programming/SKILL.md) | Programming assistance for the Zig programming language. |

## Usage

Each skill is a self-contained markdown file (plus any referenced assets) that can be loaded by an AI agent that supports skill files.

## Installation

### Codex

Install the Codex-specific skills into your personal Codex skills directory:

```bash
cp -r agent_skills/dynamic-workflow ~/.codex/skills/
cp -r agent_skills/codex/interactive-walkthrough ~/.codex/skills/
```

### Hermes Agent

Many AI agents (Claude Code, Codex, Hermes) support a skills directory. Here is how to install and load these skills in Hermes specifically.

**1. Place the skill directory in `~/.hermes/skills/`**

The directory name must match the skill name. Hermes uses the folder name as the skill identifier.

**Copy (snapshot):**
```bash
for d in obsidian-cli obsidian-plugin obsidian-theme zig-programming obsidian-bases; do
  cp -r agent_skills/$d ~/.hermes/skills/
done
mkdir -p ~/.hermes/skills/creative
cp -r agent_skills/hermes/interactive-walkthrough ~/.hermes/skills/creative/
```

**Symlink (live updates as repo changes):**
```bash
for d in obsidian-cli obsidian-plugin obsidian-theme zig-programming obsidian-bases; do
  ln -s $(realpath agent_skills/$d) ~/.hermes/skills/$d
done
```

**2. Load in a session**

Start or restart a Hermes session, then run:
```
/skill obsidian-cli
/skill zig-programming
```

Or preload skills at startup:
```bash
hermes -s obsidian-cli -s zig-programming
```

**3. Verify**

```
skills_list
```

### Other Agents

```bash
# Example for an agent with a ~/.config/agent/skills/ directory
cp -r agent_skills/obsidian-cli ~/.config/agent/skills/
cp -r agent_skills/obsidian-plugin ~/.config/agent/skills/
cp -r agent_skills/obsidian-theme ~/.config/agent/skills/
cp -r agent_skills/zig-programming ~/.config/agent/skills/
cp -r agent_skills/obsidian-bases ~/.config/agent/skills/
```

Refer to your agent's documentation for the exact skill loading mechanism.
