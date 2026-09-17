# Agent Skills

Reusable skills for Claude Code, Cursor/Grok/GrokBot, Codex, and Hermes. Every canonical package lives under `skills/<skill-name>/` and follows the [Agent Skills specification](https://agentskills.io/specification): a required `SKILL.md` plus optional scripts, references, assets, and other supporting files.

The Agent Skills specification defines each skill package, while this repository uses `skills/` as its collection root so Hermes can consume the repository as a skills tap. Claude Code packages selected skills into focused plugins; other compatible clients can consume the canonical packages directly.

The image-description skill is intentionally excluded from the Claude marketplace plugins but remains available as a standard skill package to other clients.

## Hermes skills tap

Register the GitHub repository as a tap:

```bash
hermes skills tap add klgraham/agent_skills
```

Adding a tap registers the source; it does not install every skill. Search the tap and install the package you need:

```bash
hermes skills search systems-thinking
hermes skills install klgraham/agent_skills/skills/systems-thinking
```

Run `/reload-skills` or start a new Hermes session after installation.

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
claude plugin install epistemic-pass@klogram-agent-skills
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
| `zig-programming` | `zig-programming` |
| `epistemic-pass` | `epistemic-pass` |

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

Clone the repository, choose a package under `skills/`, and link or copy it into the Codex skills directory:

```bash
git clone https://github.com/klgraham/agent_skills.git
cd agent_skills
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/skills/systems-thinking" "${CODEX_HOME:-$HOME/.codex}/skills/systems-thinking"
```

Restart Codex if the skill does not appear immediately. To update a linked installation, pull the repository:

```bash
git pull --ff-only
```

## Other Agent Skills clients

Cursor, Grok, GrokBot, and other Agent Skills-compatible clients can consume any directory under `skills/` as an individual skill package. Link or copy the selected package into the client's supported skill location. Clients that implement cross-client project discovery commonly scan `.agents/skills/`; consult the client's documentation for its user-level and project-level paths.

## Direct-install skills

| Skill | Description |
|---|---|
| [describe-image](skills/describe-image/SKILL.md) | Convert an image into a faithful reconstruction prompt with objective subject analysis, estimated lighting, palette and style extraction, and independent validation. |

`describe-image` is excluded from `.claude-plugin/marketplace.json` and every directory under `plugins/`.

## Repository layout

```text
.claude-plugin/marketplace.json   Claude marketplace catalog
plugins/                         Claude plugin manifests and links into skills/
skills/
  <skill-name>/
    SKILL.md                     Required Agent Skills manifest and instructions
    references/                  Optional on-demand documentation
    scripts/                     Optional executable helpers
    assets/                      Optional templates and static resources
README.md
```

The directories under `skills/` are the canonical source for every host. Claude plugin skill entries are relative symlinks to those canonical directories. Claude Code dereferences same-marketplace links when it copies a plugin into its cache, so each installed plugin remains self-contained without maintaining duplicate skill copies.

## Systems thinking

The [systems-thinking skill](skills/systems-thinking/SKILL.md) combines system analysis and software review in one entrypoint. It selects one of eight playbooks: understand, diagnose, review, design, choose an intervention, analyze failure, visualize, or verify a model. Each playbook loads relevant principles and small input modes as needed.

Use `$systems-thinking` in Codex or `/systems-thinking:systems-thinking` in Claude Code. Review requests retain the evidence gate, read-only boundary, and optional matching HTML and Obsidian reports. Understanding a system does not require recommending changes.

The former `systems-thinking-reviewer` skill is retired. Replace old local links or copies with `skills/systems-thinking`. Existing report JSON remains compatible with `skills/systems-thinking/scripts/build_report.py`; the renderer and HTML asset move together.

## Zig programming

The [zig-programming skill](skills/zig-programming/SKILL.md) is one entrypoint for Zig implementation, builds, stdlib migration, memory-safety review, performance work, mmap formats, compiler bootstrapping, and release updates. It routes by intent to focused playbooks and loads principles and references only when needed.

Use `$zig-programming` in Codex or `/zig-programming:zig-programming` in Claude Code. The former eight Zig skill names are retired; replace local links or copies with `skills/zig-programming`.
