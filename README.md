# Agent Skills

Reusable skills for Codex and Claude Code. The skill directories are the canonical source for both hosts: Codex loads them directly, while the Claude marketplace packages them into focused plugins.

The image-description skill is intentionally Codex-only and is not included in any Claude plugin.

## Claude Code marketplace

Add the GitHub repository as a marketplace:

```bash
claude plugin marketplace add klgraham/agent_skills
```

Then install any plugin:

```bash
claude plugin install obsidian-toolkit@klogram-agent-skills
claude plugin install systems-thinking@klogram-agent-skills
claude plugin install code-review@klogram-agent-skills
claude plugin install skill-development@klogram-agent-skills
claude plugin install zig-programming@klogram-agent-skills
```

Installations use user scope by default. Add `--scope project` or `--scope local` when a plugin should be limited to a project.

After installing or updating a plugin during a session, run `/reload-plugins` in Claude Code.

### Plugin contents

| Plugin | Skills |
|---|---|
| `obsidian-toolkit` | `obsidian-bases`, `obsidian-cli`, `obsidian-plugin`, `obsidian-theme` |
| `systems-thinking` | `systems-thinking` |
| `code-review` | `concurrency-code-review` |
| `skill-development` | `transcript-skill-miner` |
| `zig-programming` | `zig`, `write-legible-zig`, `zig-0-16-stdlib-patterns`, `zig-build-from-source`, `zig-build-system`, `zig-data-oriented-programming`, `zig-memory-safety-review`, `zig-mmap-project-template` |

Claude namespaces installed skills by plugin. For example, invoke `/code-review:concurrency-code-review` to audit concurrent code.

### Update Claude plugins

Refresh the marketplace and update an installed plugin:

```bash
claude plugin marketplace update klogram-agent-skills
claude plugin update code-review@klogram-agent-skills
```

The marketplace intentionally omits fixed plugin versions, so each new Git commit can be resolved as an update.

### Test a local checkout

From the repository root:

```bash
claude plugin validate .
claude plugin marketplace add .
claude plugin install code-review@klogram-agent-skills --scope local
```

## Codex installation

Clone the repository, choose a skill directory, and link or copy it into the Codex skills directory:

```bash
git clone https://github.com/klgraham/agent_skills.git
cd agent_skills
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/systems-thinking" "${CODEX_HOME:-$HOME/.codex}/skills/systems-thinking"
```

Restart Codex if the skill does not appear immediately. To update a linked installation, pull the repository:

```bash
git pull --ff-only
```

Every skill in the Claude plugins is also a Codex-compatible skill directory with a `SKILL.md`. Zig skills live under `zig-programming/`.

## Codex-only skills

| Skill | Description |
|---|---|
| [describe-image](describe-image/SKILL.md) | Convert an image into a faithful reconstruction prompt with objective subject analysis, estimated lighting, palette and style extraction, and independent validation. |

Image-description skills are excluded from `.claude-plugin/marketplace.json` and every directory under `plugins/`.

## Repository layout

```text
.claude-plugin/marketplace.json   Claude marketplace catalog
plugins/                         Claude plugin manifests and skill links
<skill>/SKILL.md                 Canonical portable skills
zig-programming/                 Canonical Zig skill family
```

The `code-review` plugin includes a standalone concurrency audit with Python-specific `asyncio`, thread, executor, process, and queue checks.

Claude plugin skill entries are relative symlinks to canonical directories in this repository. Claude Code dereferences same-marketplace links when it copies a plugin into its cache, so each installed plugin remains self-contained without maintaining duplicate skill copies.

## Systems thinking

The [systems-thinking skill](systems-thinking/SKILL.md) combines system analysis and software review in one entrypoint. It selects one of eight playbooks: understand, diagnose, review, design, choose an intervention, analyze failure, visualize, or verify a model. Each playbook loads relevant principles and small input modes as needed.

Use `$systems-thinking` in Codex or `/systems-thinking:systems-thinking` in Claude Code. Review requests retain the evidence gate, read-only boundary, and optional matching HTML and Obsidian reports. Understanding a system does not require recommending changes.

The former `systems-thinking-reviewer` skill is retired. Replace old local links or copies with the unified `systems-thinking` directory using the installation instructions above. Existing report JSON remains compatible with `systems-thinking/scripts/build_report.py`; the renderer and HTML asset move together.
