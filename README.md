# Agent Skills

Agent Skills for AI coding assistants.

## Installation

### Claude Code

#### Marketplace

```bash
/plugin marketplace add klgraham/agent_skills
/plugin install obsidian-cli@agent_skills
```

#### Manually

```bash
# Clone the repository
git clone https://github.com/klgraham/agent_skills.git

# Copy skills to Claude Code's skills directory
cp -r agent_skills/obsidian-cli ~/.claude/skills/
```

See the [Claude Code skills folder](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/skills) documentation for more information.

### Cursor

Cursor supports both project-level and global skills installation.

#### Project-Level Installation

```bash
# Create project skills directory
mkdir -p .cursor/skills

# Copy skills to project
cp -r /path/to/agent_skills/obsidian-cli .cursor/skills/
```

#### Global Installation

```bash
# Create global skills directory
mkdir -p ~/.cursor/skills

# Copy skills globally
cp -r /path/to/agent_skills/obsidian-cli ~/.cursor/skills/
```

### Warp

Warp AI supports project-level and user-level skills.

#### Project-Level Installation

```bash
# Create project skills directory
mkdir -p .warp/skills/obsidian-cli

# Copy skill files (note: each skill needs its own subdirectory with SKILL.md)
cp agent_skills/obsidian-cli/SKILL.md .warp/skills/obsidian-cli/
```

#### User-Level Installation

```bash
# Create user skills directory
mkdir -p ~/.warp/skills/obsidian-cli

# Copy skill files
cp agent_skills/obsidian-cli/SKILL.md ~/.warp/skills/obsidian-cli/
```

**Important Note for Warp:**
- Each skill must be in its own subdirectory

**Usage in Warp**

Once installed, Warp AI will automatically use these skills when you ask questions about Obsidian operations or plugin development.

#### Codex CLI

Place the contents of this repository in `~/.codex/skills`. See the [Agent Skills specification](https://github.com/modelcontextprotocol/agent-skills) for more information.

## Skills

| Skill | Description |
|-------|-------------|
| [obsidian-cli](obsidian-cli/SKILL.md) | Interact with Obsidian vaults using CLI commands. Read, create, search notes, manage tasks, tags, properties, plugins, and more. 60+ commands for complete vault automation. |
| [obsidian-plugin](obsidian-plugin/skill.md) | Build and edit Obsidian plugins using TypeScript and the Obsidian API. Supports plugin development, feature implementation, and publishing workflows. |
| [zig-programming](zig-programming/SKILL.md) | Programming assistance for the Zig programming language. |
