# Agent Skills

Agent Skills for AI coding assistants.

## Installation

### Marketplace

```bash
/plugin marketplace add klgraham/agent_skills
/plugin install obsidian-cli@agent_skills
/plugin install obsidian-plugin@agent_skills
```

### Manually

#### Claude Code

**Quick Install**

Use the npx installer:

```bash
# Install both skills at once
npx @claude-code/plugin-installer install klgraham/agent_skills
```

The installer will prompt you to select which skills to install (or choose "All skills").

**Manual Install**

```bash
# Clone the repository
git clone https://github.com/klgraham/agent_skills.git

# Copy skills to Claude Code's skills directory
cp -r agent_skills/obsidian-cli ~/.claude/skills/
cp -r agent_skills/obsidian-plugin ~/.claude/skills/
```

See the [Claude Code skills folder](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/skills) documentation for more information.

#### Cursor

Cursor supports both project-level and global skills installation.

**Project-Level Installation**

```bash
# Create project skills directory
mkdir -p .cursor/skills

# Copy skills to project
cp -r /path/to/agent_skills/obsidian-cli .cursor/skills/
cp -r /path/to/agent_skills/obsidian-plugin .cursor/skills/
```

**Global Installation**

```bash
# Create global skills directory
mkdir -p ~/.cursor/skills

# Copy skills globally
cp -r /path/to/agent_skills/obsidian-cli ~/.cursor/skills/
cp -r /path/to/agent_skills/obsidian-plugin ~/.cursor/skills/
```

**Usage in Cursor**

Invoke skills using slash commands in the chat:
- `/obsidian-cli` - For vault operations
- `/obsidian-plugin` - For plugin development

#### Warp

Warp AI supports project-level and user-level skills.

**Project-Level Installation**

```bash
# Create project skills directory
mkdir -p .warp/skills/obsidian-cli
mkdir -p .warp/skills/obsidian-plugin

# Copy skill files (note: each skill needs its own subdirectory with SKILL.md)
cp agent_skills/obsidian-cli/SKILL.md .warp/skills/obsidian-cli/
cp agent_skills/obsidian-plugin/skill.md .warp/skills/obsidian-plugin/SKILL.md
```

**User-Level Installation**

```bash
# Create user skills directory
mkdir -p ~/.warp/skills/obsidian-cli
mkdir -p ~/.warp/skills/obsidian-plugin

# Copy skill files
cp agent_skills/obsidian-cli/SKILL.md ~/.warp/skills/obsidian-cli/
cp agent_skills/obsidian-plugin/skill.md ~/.warp/skills/obsidian-plugin/SKILL.md
```

**Important Note for Warp:**
- Each skill must be in its own subdirectory
- The skill documentation file must be named `SKILL.md` (case-sensitive)

**Usage in Warp**

Once installed, Warp AI will automatically use these skills when you ask questions about Obsidian operations or plugin development.

#### Codex CLI

Place the contents of this repository in `~/.codex/skills`. See the [Agent Skills specification](https://github.com/modelcontextprotocol/agent-skills) for more information.

## Skills

| Skill | Description |
|-------|-------------|
| [obsidian-cli](obsidian-cli/SKILL.md) | Interact with Obsidian vaults using CLI commands. Read, create, search notes, manage tasks, tags, properties, plugins, and more. 60+ commands for complete vault automation. |
| [obsidian-plugin](obsidian-plugin/skill.md) | Build and edit Obsidian plugins using TypeScript and the Obsidian API. Supports plugin development, feature implementation, and publishing workflows. |
