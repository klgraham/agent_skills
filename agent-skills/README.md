# Agent Skills Plugin

A Claude Code plugin that bundles three powerful agent skills for enhanced productivity with Obsidian and Zig programming.

## Overview

This plugin provides three specialized agent skills:

1. **obsidian-cli**: Interact with Obsidian vaults using CLI commands
2. **obsidian-plugin**: Build and edit Obsidian plugins using TypeScript
3. **zig-programming**: Programming assistance for the Zig language

## Skills Included

### Obsidian CLI

Full command-line integration with Obsidian vaults. Includes 60+ commands for:

- Reading, creating, and managing notes
- Daily notes automation
- Search and navigation
- Task management
- Tag operations
- Frontmatter properties
- Link management
- Bookmarks
- Templates
- Plugin and theme management
- Workspace operations
- Sync and Publish control
- File history
- Developer tools

**When to use**: Automate Obsidian workflows, batch operations on notes, integrate with scripts and CI/CD, or perform complex vault queries.

### Obsidian Plugin Development

Comprehensive guide for building Obsidian community plugins. Covers:

- Plugin architecture and structure
- Manifest and configuration files
- Command registration
- Settings UI
- Modal dialogs
- Event handling
- File and editor operations
- Custom views and leaves
- Build system (esbuild/TypeScript)
- Publishing workflow
- Best practices and common patterns

**When to use**: Creating new Obsidian plugins, adding features to existing plugins, debugging plugin issues, or learning the Obsidian API.

### Zig Programming

Programming assistance for Zig development. Includes:

- Core language principles
- Error handling patterns
- Memory management
- Comptime programming
- Build system (build.zig)
- Testing strategies
- Common patterns and idioms
- Standard library essentials
- Performance optimization
- Debugging tips
- Reference documentation

**When to use**: Writing Zig code, configuring build systems, optimizing performance, or learning Zig best practices.

## Installation

### Claude Code

Install from the marketplace:

```bash
/plugin marketplace add klgraham/agent_skills
/plugin install agent-skills@agent-skills-marketplace
```

### Manual Installation

Clone the repository and copy this plugin directory to your Claude plugins folder:

```bash
git clone https://github.com/klgraham/agent_skills.git
cp -r agent_skills/agent-skills ~/.claude/plugins/
```

## Usage

Once installed, Claude will automatically use these skills when:

- You ask about Obsidian operations or CLI commands
- You're working on Obsidian plugin development
- You're writing or debugging Zig code

The skills are invoked automatically based on context, or you can explicitly reference them in your prompts.

## Requirements

### Obsidian CLI Skill

- Obsidian app must be running
- Obsidian CLI tool must be installed (available via Homebrew or npm)
- Active vault must be open in Obsidian

### Obsidian Plugin Skill

- Node.js and npm
- TypeScript
- Basic understanding of Obsidian's plugin structure

### Zig Programming Skill

- Zig compiler (latest stable or nightly)
- Basic understanding of systems programming concepts

## License

MIT

## Author

Ken Graham (https://github.com/klgraham)

## Repository

https://github.com/klgraham/agent_skills
