# Agent Skills

Reusable skills for Claude Code, Codex, and other Agent Skills-compatible harnesses. The skill directories are the canonical portable source: compatible harnesses load them directly, while the Claude marketplace packages them into focused plugins.

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
claude plugin install workflows@klogram-agent-skills
claude plugin install skill-development@klogram-agent-skills
claude plugin install personas@klogram-agent-skills
claude plugin install zig-programming@klogram-agent-skills
```

Installations use user scope by default. Add `--scope project` or `--scope local` when a plugin should be limited to a project.

After installing or updating a plugin during a session, run `/reload-plugins` in Claude Code.

### Plugin contents

| Plugin | Skills |
|---|---|
| `obsidian-toolkit` | `obsidian-bases`, `obsidian-cli`, `obsidian-plugin`, `obsidian-theme` |
| `systems-thinking` | `systems-thinking`, `systems-thinking-reviewer` |
| `workflows` | `dynamic-workflow`, `interactive-walkthrough`, `pr-walkthrough` |
| `skill-development` | `echo-skill`, `transcript-skill-miner` |
| `personas` | `echo-alan-kay`, `echo-rich-hickey` |
| `zig-programming` | `zig`, `write-legible-zig`, `zig-0-16-stdlib-patterns`, `zig-build-from-source`, `zig-build-system`, `zig-data-oriented-programming`, `zig-memory-safety-review`, `zig-mmap-project-template` |

Claude namespaces installed skills by plugin. For example, invoke `/workflows:pr-walkthrough` or ask Claude naturally for an interactive PR walkthrough.

### Update Claude plugins

Refresh the marketplace and update an installed plugin:

```bash
claude plugin marketplace update klogram-agent-skills
claude plugin update workflows@klogram-agent-skills
```

The marketplace intentionally omits fixed plugin versions, so each new Git commit can be resolved as an update.

### Test a local checkout

From the repository root:

```bash
claude plugin validate .
claude plugin marketplace add .
claude plugin install workflows@klogram-agent-skills --scope local
```

## Codex and other Agent Skills harnesses

Clone the repository, choose a canonical skill directory, and link or copy it into the harness's skill-discovery directory. For Codex:

```bash
git clone https://github.com/klgraham/agent_skills.git
cd agent_skills
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/echo-rich-hickey" "${CODEX_HOME:-$HOME/.codex}/skills/echo-rich-hickey"
```

Restart Codex if the skill does not appear immediately. To update a linked installation, pull the repository:

```bash
git pull --ff-only
```

Every skill in the Claude plugins is also a portable skill directory with a `SKILL.md`; `agents/openai.yaml` is optional Codex interface metadata and does not change the portable runtime instructions. Other compatible harnesses can discover the same directory according to their own installation convention. The interactive walkthrough's canonical Codex path is `codex/interactive-walkthrough`; Zig skills live under `zig-programming/`.

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
<skill>/agents/openai.yaml       Optional Codex interface metadata
codex/interactive-walkthrough/   Canonical interactive walkthrough skill
zig-programming/                 Canonical Zig skill family
```

Claude plugin skill entries are relative symlinks to canonical directories in this repository. Claude Code dereferences same-marketplace links when it copies a plugin into its cache, so each installed plugin remains self-contained without maintaining duplicate skill copies.
