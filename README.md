# Agent Skills

Agent Skills for AI coding assistants.

## Skills

| Skill | Description |
|-------|-------------|
| [obsidian-cli](obsidian-cli/skills/obsidian-cli/SKILL.md) | Interact with Obsidian vaults using CLI commands. Read, create, search notes, manage tasks, tags, properties, plugins, and more. 60+ commands for complete vault automation. |
| [obsidian-plugin](obsidian-plugin/skills/obsidian-plugin/SKILL.md) | Build and edit Obsidian plugins using TypeScript and the Obsidian API. Supports plugin development, feature implementation, and publishing workflows. |
| [zig-programming](zig-programming/skills/zig-programming/SKILL.md) | Programming assistance for the Zig programming language. |

## Installation

### Claude Code

#### Marketplace

Add the marketplace, then install individual skills or all of them at once.

From your terminal:

```bash
# Add the marketplace
claude plugin marketplace add klgraham/agent_skills

# Install all skills at once
claude plugin install all-skills@agent-skills-marketplace

# Or install individual skills
claude plugin install obsidian-cli@agent-skills-marketplace
claude plugin install obsidian-plugin@agent-skills-marketplace
claude plugin install zig-programming@agent-skills-marketplace
```

Or from inside Claude Code's interactive chat:

```
/plugin marketplace add klgraham/agent_skills

# Install all skills at once
/plugin install all-skills@agent-skills-marketplace

# Or install individual skills
/plugin install obsidian-cli@agent-skills-marketplace
/plugin install obsidian-plugin@agent-skills-marketplace
/plugin install zig-programming@agent-skills-marketplace
```

For local development, you can add the marketplace from a local path:

```bash
claude plugin marketplace add /path/to/agent_skills
claude plugin install all-skills@agent-skills-marketplace
```

#### Manual Installation

```bash
# Clone the repository
git clone https://github.com/klgraham/agent_skills.git

# Install all skills as a single plugin
cp -r agent_skills/all-skills ~/.claude/plugins/

# Or install individual skill plugins
cp -r agent_skills/obsidian-cli ~/.claude/plugins/
cp -r agent_skills/obsidian-plugin ~/.claude/plugins/
cp -r agent_skills/zig-programming ~/.claude/plugins/

# Or copy individual skills to Claude Code's skills directory
cp -r agent_skills/obsidian-cli/skills/obsidian-cli ~/.claude/skills/
cp -r agent_skills/obsidian-plugin/skills/obsidian-plugin ~/.claude/skills/
cp -r agent_skills/zig-programming/skills/zig-programming ~/.claude/skills/
```

See the [Claude Code plugins](https://docs.anthropic.com/en/docs/claude-code/plugin-marketplaces) and [skills](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/skills) documentation for more information.

### Cursor

Cursor supports both project-level and global skills installation.

#### Project-Level Installation

```bash
# Create project skills directory
mkdir -p .cursor/skills

# Copy individual skills to project
cp -r /path/to/agent_skills/obsidian-cli/skills/obsidian-cli .cursor/skills/
cp -r /path/to/agent_skills/obsidian-plugin/skills/obsidian-plugin .cursor/skills/
cp -r /path/to/agent_skills/zig-programming/skills/zig-programming .cursor/skills/
```

#### Global Installation

```bash
# Create global skills directory
mkdir -p ~/.cursor/skills

# Copy skills globally
cp -r /path/to/agent_skills/obsidian-cli/skills/obsidian-cli ~/.cursor/skills/
cp -r /path/to/agent_skills/obsidian-plugin/skills/obsidian-plugin ~/.cursor/skills/
cp -r /path/to/agent_skills/zig-programming/skills/zig-programming ~/.cursor/skills/
```

### Warp

Warp AI supports project-level and user-level skills.

#### Project-Level Installation

```bash
# Create project skills directories
mkdir -p .warp/skills/obsidian-cli .warp/skills/obsidian-plugin .warp/skills/zig-programming

# Copy skill files (note: each skill needs its own subdirectory with SKILL.md)
cp agent_skills/obsidian-cli/skills/obsidian-cli/SKILL.md .warp/skills/obsidian-cli/
cp agent_skills/obsidian-plugin/skills/obsidian-plugin/SKILL.md .warp/skills/obsidian-plugin/
cp agent_skills/zig-programming/skills/zig-programming/SKILL.md .warp/skills/zig-programming/
```

#### User-Level Installation

```bash
# Create user skills directories
mkdir -p ~/.warp/skills/obsidian-cli ~/.warp/skills/obsidian-plugin ~/.warp/skills/zig-programming

# Copy skill files
cp agent_skills/obsidian-cli/skills/obsidian-cli/SKILL.md ~/.warp/skills/obsidian-cli/
cp agent_skills/obsidian-plugin/skills/obsidian-plugin/SKILL.md ~/.warp/skills/obsidian-plugin/
cp agent_skills/zig-programming/skills/zig-programming/SKILL.md ~/.warp/skills/zig-programming/
```

**Important Note for Warp:**
- Each skill must be in its own subdirectory

**Usage in Warp**

Once installed, Warp AI will automatically use these skills when you ask questions about Obsidian operations or plugin development.

#### Codex CLI

Place the contents of this repository in `~/.codex/skills`. See the [Agent Skills specification](https://github.com/modelcontextprotocol/agent-skills) for more information.
