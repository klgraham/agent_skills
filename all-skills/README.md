# All Skills Plugin

A Claude Code plugin that bundles all agent skills into a single install.

## Included Skills

| Skill | Description |
|-------|-------------|
| [obsidian-cli](skills/obsidian-cli/SKILL.md) | Interact with Obsidian vaults using CLI commands. 60+ commands for complete vault automation. |
| [obsidian-plugin](skills/obsidian-plugin/SKILL.md) | Build and edit Obsidian plugins using TypeScript and the Obsidian API. |
| [zig-programming](skills/zig-programming/SKILL.md) | Programming assistance for the Zig language. |

## Installation

### Claude Code (Marketplace)

```bash
claude plugin marketplace add klgraham/agent_skills
claude plugin install all-skills@agent-skills-marketplace
```

Or from inside Claude Code's interactive chat:

```
/plugin marketplace add klgraham/agent_skills
/plugin install all-skills@agent-skills-marketplace
```

### Manual Installation

```bash
git clone https://github.com/klgraham/agent_skills.git
cp -r agent_skills/all-skills ~/.claude/plugins/
```

## Usage

Once installed, Claude will automatically use these skills when:

- You ask about Obsidian operations or CLI commands
- You're working on Obsidian plugin development
- You're writing or debugging Zig code

## License

MIT

## Author

Ken Graham (https://github.com/klgraham)
