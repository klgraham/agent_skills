# Agent Skills

Agent Skills for AI coding assistants.

## Skills

| Skill | Description |
|-------|-------------|
| [dynamic-workflow](dynamic-workflow/SKILL.md) | Design and run script-backed multi-agent Codex workflows with isolated workers, structured outputs, verification stages, bounded loops, and resumable checkpoints. |
| [echo-skill](echo-skill/SKILL.md) | Create portable, evidence-grounded persona-and-work skills from source material about colleagues, mentors, collaborators, or public figures. |
| [interactive-walkthrough (Codex)](codex/interactive-walkthrough/SKILL.md) | Build evidence-grounded, self-contained interactive HTML walkthroughs of code, repositories, systems, and technical processes using Codex-native browser verification. |
| [interactive-walkthrough (Hermes)](hermes/interactive-walkthrough/SKILL.md) | Original Hermes version of the interactive walkthrough skill. |
| [obsidian-bases](obsidian-bases/SKILL.md) | Expert assistance for Obsidian Bases — the native database/query layer in Obsidian. Create and edit `.base` files, write filter expressions, build formulas, and design table views. |
| [obsidian-cli](obsidian-cli/SKILL.md) | Interact with Obsidian vaults using CLI commands. Read, create, search notes, manage tasks, tags, properties, plugins, and more. 60+ commands for complete vault automation. |
| [obsidian-plugin](obsidian-plugin/SKILL.md) | Build and edit Obsidian plugins using TypeScript and the Obsidian API. Supports plugin development, feature implementation, and publishing workflows. |
| [obsidian-theme](obsidian-theme/SKILL.md) | Create and publish Obsidian themes using CSS. Includes dark/light mode support, CSS variable reference, and community gallery publishing workflow. |
| [systems-thinking-reviewer](systems-thinking-reviewer/SKILL.md) | Review repositories, pull requests or diffs, ADRs, diagrams, and architecture descriptions through evidence-linked causal analysis of system behavior, feedback, coupling, failure propagation, operations, and evolution. |
| [zig-programming](zig-programming/SKILL.md) | Programming assistance for the Zig programming language. |

## Usage

Each skill is a self-contained markdown file (plus any referenced assets) that can be loaded by an AI agent that supports skill files.

## Installation

Choose a skill from the table above and replace the placeholders with its directory name and your agent's skills directory:

```bash
SKILL_NAME="<skill-name>"
AGENT_SKILLS_DIR="<path-to-agent-skills-directory>"
cp -r "agent_skills/$SKILL_NAME" "$AGENT_SKILLS_DIR/"
```

Restart the agent if necessary, then follow its documentation to load or invoke the skill.
