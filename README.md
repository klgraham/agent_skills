# Agent Skills

Agent Skills for AI coding assistants.

## Skills

| Skill | Description |
|-------|-------------|
| [obsidian-cli](obsidian-cli/skills/obsidian-cli/SKILL.md) | Interact with Obsidian vaults using CLI commands. Read, create, search notes, manage tasks, tags, properties, plugins, and more. 60+ commands for complete vault automation. |
| [obsidian-plugin](obsidian-plugin/skills/obsidian-plugin/SKILL.md) | Build and edit Obsidian plugins using TypeScript and the Obsidian API. Supports plugin development, feature implementation, and publishing workflows. |
| [obsidian-theme](obsidian-theme/skills/obsidian-theme/SKILL.md) | Create and publish Obsidian themes using CSS. Includes dark/light mode support, CSS variable reference, and community gallery publishing workflow. |
| [zig-programming](zig-programming/skills/zig-programming/SKILL.md) | Programming assistance for the Zig programming language. |

## Installation

### Claude Code

#### Marketplace

Add the marketplace, then install individual skills or all of them at once.

From your terminal:

```bash
# Add the marketplace
claude plugin marketplace add klgraham/agent_skills

# Or install individual skills
claude plugin install obsidian-cli@agent-skills-marketplace
claude plugin install obsidian-plugin@agent-skills-marketplace
claude plugin install obsidian-theme@agent-skills-marketplace
claude plugin install zig-programming@agent-skills-marketplace
```

Or from inside Claude Code's interactive chat:

```
/plugin marketplace add klgraham/agent_skills

# Or install individual skills
/plugin install obsidian-cli@agent-skills-marketplace
/plugin install obsidian-plugin@agent-skills-marketplace
/plugin install obsidian-theme@agent-skills-marketplace
/plugin install zig-programming@agent-skills-marketplace
```

For local development, you can add the marketplace from a local path:

```bash
claude plugin marketplace add /path/to/agent_skills
```

#### Manual Installation

```bash
# Clone the repository
git clone https://github.com/klgraham/agent_skills.git

# Or install individual skill plugins
cp -r agent_skills/obsidian-cli ~/.claude/plugins/
cp -r agent_skills/obsidian-plugin ~/.claude/plugins/
cp -r agent_skills/obsidian-theme ~/.claude/plugins/
cp -r agent_skills/zig-programming ~/.claude/plugins/

# Or copy individual skills to Claude Code's skills directory
cp -r agent_skills/obsidian-cli/skills/obsidian-cli ~/.claude/skills/
cp -r agent_skills/obsidian-plugin/skills/obsidian-plugin ~/.claude/skills/
cp -r agent_skills/obsidian-theme/skills/obsidian-theme ~/.claude/skills/
cp -r agent_skills/zig-programming/skills/zig-programming ~/.claude/skills/
```

See the [Claude Code plugins](https://docs.anthropic.com/en/docs/claude-code/plugin-marketplaces) and [skills](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/skills) documentation for more information.
