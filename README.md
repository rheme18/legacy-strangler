<p align="center">
  <img src=".agents/skills/legacy-strangler/assets/icon.svg" alt="Legacy Strangler icon" width="84">
</p>

<hr>

<h1 align="center">Legacy Strangler</h1>

<p align="center"><em>Modernize legacy systems one verified boundary at a time.</em></p>

<p align="center">
  <a href="https://github.com/rheme18/legacy-strangler/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/rheme18/legacy-strangler?style=flat-square"></a>
  <a href="https://github.com/rheme18/legacy-strangler/blob/main/LICENSE"><img alt="MIT License" src="https://img.shields.io/github/license/rheme18/legacy-strangler?style=flat-square"></a>
  <a href="https://github.com/rheme18/legacy-strangler/commits/main/"><img alt="Last commit" src="https://img.shields.io/github/last-commit/rheme18/legacy-strangler?style=flat-square"></a>
  <img alt="Python standard library only" src="https://img.shields.io/badge/Python-standard%20library-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="No runtime dependencies" src="https://img.shields.io/badge/runtime%20dependencies-none-2E8B57?style=flat-square">
  <img alt="Codex, Claude Code, Cursor, Antigravity" src="https://img.shields.io/badge/agents-Codex%20%7C%20Claude%20%7C%20Cursor%20%7C%20Antigravity-6C5CE7?style=flat-square">
</p>

<hr>

`legacy-strangler` is a portable Agent Skill for incremental software modernization. It gives coding agents a disciplined migration workflow based on the Strangler Fig pattern: understand the dependency graph, lock current behavior with characterization tests, introduce a parallel implementation behind a seam, and cut over only when the evidence supports it.

It is designed for migrations such as JavaScript → TypeScript, jQuery → React, Flask/PHP → Node.js/FastAPI, class components → hooks, framework upgrades, and replacement of legacy services. The package includes a dependency mapper, a migration-plan template, and a deliberately tricky shopping-cart fixture.

## Why AI agents fail at large migrations

“Rewrite this project in TypeScript” sounds like one task, but it combines many hidden contracts: public APIs, persistence formats, ordering, rounding, error behavior, side effects, operational assumptions, and caller expectations. Legacy code often has no complete specification. An agent can produce a coherent replacement while unknowingly changing those contracts across dozens of files.

This is the **Big Bang Rewrite Trap**:

1. A broad request encourages a broad diff.
2. The replacement is designed from intent or conventions instead of observed behavior.
3. Tests cover the new implementation's assumptions rather than the old system's contract.
4. The original path disappears before production behavior has been compared.
5. Failures become difficult to localize and expensive to reverse.

Legacy Strangler narrows the blast radius. It asks the agent to make one capability explicit, measure what the old code does, build the replacement beside it, and switch callers at a controlled boundary. A migration is complete when behavior is covered, checks pass, ownership has moved, rollback is understood, and the plan records the result.

## Engineering model

The workflow is a small feedback loop rather than a one-shot rewrite:

```text
Inventory → Characterize → Implement beside legacy → Compare → Route → Retire
     ↑                                                               │
     └────────────── rollback if evidence turns red ─────────────────┘
```

### 1. Dependency-aware sequencing

`dependency_mapper.py` scans common source files and extracts static `import`, `require`, and `include` references. It reports:

- **Out-degree:** the number of scanned modules this file depends on.
- **In-degree:** the number of scanned modules that depend on this file.
- **Leaf candidates:** modules with no detected outgoing dependencies, sorted with low incoming coupling first.
- **Unresolved references:** imports that could not be mapped to one scanned file.

Start with leaf candidates that are bounded and low risk. Move toward shared/core modules after callers have stable migrated boundaries. The graph is a planning aid, not a proof: aliases, package exports, dependency injection, reflection, generated files, dynamic imports, and runtime calls may be invisible. Review the unresolved list and verify important edges against actual callers and runtime behavior.

### 2. Characterization before conversion

Tests capture the behavior the current system actually exposes. Include ordinary cases, edge cases, errors, and side effects. Useful dimensions include null and missing values, coercion, empty data, ordering, rounding, date/time assumptions, retries, state mutation, and callback/event order. Preserve surprising behavior during a compatibility migration; propose product behavior changes separately.

### 3. A reversible strangler seam

Create the replacement beside the legacy implementation. Route a bounded call path through an adapter, facade, proxy, or a feature flag that can safely return traffic to the old path. Compare both implementations using the same characterization inputs and observe relevant side effects. Keep the legacy path until the replacement and its callers have been verified.

### 4. Evidence-based cleanup

Run the repository's required tests, type checks, lint, integration checks, and build. Document the exact commands and results. Remove old code only after no required caller depends on it and rollback no longer needs it. Keep each slice reviewable and use the commit subject prescribed in the skill.

## Repository contents

```text
legacy-strangler/
├── .agents/skills/legacy-strangler/
│   ├── SKILL.md
│   ├── assets/icon.svg
│   ├── scripts/dependency_mapper.py
│   └── templates/MIGRATION_PLAN.md
├── examples/js-to-ts-sample/
│   ├── legacy_cart.js
│   └── README.md
├── LICENSE
└── README.md
```

## Install into an agent

### Recommended: Skills CLI

Install from the published GitHub repository in your target project:

```sh
npx skills add rheme18/legacy-strangler --skill legacy-strangler
```

The CLI can prompt you for the agent(s) and scope. To select an agent explicitly, for example:

```sh
npx skills add rheme18/legacy-strangler --skill legacy-strangler --agent codex
npx skills add rheme18/legacy-strangler --skill legacy-strangler --agent claude-code
npx skills add rheme18/legacy-strangler --skill legacy-strangler --agent cursor
```

Run `npx skills add --help` for current options. The CLI supports many agents and installs into their expected skill location. You can install per project (default) or globally with `-g`. For Antigravity, keep the skill in the workspace `.agents/skills/` directory or install it into Antigravity's global skills directory as described below.

### Manual install: workspace

Copy the complete `.agents/skills/legacy-strangler/` folder into the target repository's `.agents/skills/legacy-strangler/`. Keep the script and template beside `SKILL.md`; the instructions call them by their relative paths.

```text
your-project/
└── .agents/skills/legacy-strangler/
    ├── SKILL.md
    ├── assets/icon.svg
    ├── scripts/dependency_mapper.py
    └── templates/MIGRATION_PLAN.md
```

### Agent-specific discovery

| Agent | Project installation | Global installation | How to invoke |
|---|---|---|---|
| **Google Antigravity** | `.agents/skills/legacy-strangler/` | `~/.gemini/config/skills/legacy-strangler/` | Automatic selection when relevant; CLI supports `/legacy-strangler`. |
| **Claude Code** | `.claude/skills/legacy-strangler/` | `~/.claude/skills/legacy-strangler/` | Ask for the migration; or invoke the skill by name when supported by the installed version. |
| **Cursor** | `.agents/skills/legacy-strangler/` with Skills CLI, or `.cursor/skills/legacy-strangler/` for native project skills | Skills CLI global scope, or Cursor's configured global skills location | Ask in Agent chat; explicitly say “Use the `legacy-strangler` skill.” |
| **OpenAI Codex** | `.agents/skills/legacy-strangler/` | `~/.agents/skills/legacy-strangler/` | Automatic selection when relevant; explicitly ask Codex to use `legacy-strangler`. |

For manual Claude Code installation, copy this folder to `.claude/skills/legacy-strangler/`. For native Cursor Skills installation, copy it to `.cursor/skills/legacy-strangler/`. Antigravity and Codex use `.agents/skills/` directly. The Skills CLI can create agent-specific copies; avoid editing only one copy if you later update the source repository.

Restart the agent session or reload its skills after installing. Discovery behavior depends on the product and version. If the agent does not activate it automatically, invoke it explicitly or ask it to read the installed `SKILL.md`.

### Install from a local checkout

While developing this repository, use the Skills CLI's local source support if available:

```sh
npx skills add . --skill legacy-strangler
```

If the CLI does not find this nested skill in the local checkout, install it manually by copying `.agents/skills/legacy-strangler/` into the target location shown above.

## Use it effectively

Start with one bounded capability and state the behavior contract you need to preserve. Examples:

**Antigravity**

```text
/legacy-strangler Migrate the invoice formatter to TypeScript. Map its callers, characterize current output and error behavior, and migrate only this capability.
```

**Claude Code**

```text
Use the legacy-strangler skill to migrate the checkout pricing module. Create or update MIGRATION_PLAN.md, run the mapper, write characterization tests before conversion, and keep the existing route available until parity checks pass.
```

**Cursor**

```text
Use legacy-strangler for this jQuery-to-React migration. Start with one widget, add the React version beside the current one, preserve DOM events and analytics side effects, and leave the old widget in place until tests pass.
```

**Codex**

```text
Apply the legacy-strangler workflow to this Flask endpoint as it moves to FastAPI. Inspect repository instructions, map dependencies, capture response and error behavior, then stop after one verified and reviewable slice.
```

For any agent, an effective migration prompt includes: target capability, target technology, behavior constraints, required checks, and scope boundaries. Do not ask an agent to migrate every module in a single pass.

## Run the dependency mapper

The mapper requires Python 3 and only Python standard-library modules. From the repository root:

```sh
python .agents/skills/legacy-strangler/scripts/dependency_mapper.py .
python .agents/skills/legacy-strangler/scripts/dependency_mapper.py . --format json
python .agents/skills/legacy-strangler/scripts/dependency_mapper.py examples/js-to-ts-sample --format markdown
python .agents/skills/legacy-strangler/scripts/dependency_mapper.py . --format json --output dependency-map.json
```

The default output is a readable Markdown report. `--format json` provides a machine-readable graph. `--help` lists the command options. Review the scan root and unresolved references before using the report to decide migration order.

## Try the fixture

The sample cart is intentionally realistic and irregular. It includes global event state, in-place mutation, callbacks, permissive quantity coercion, loose ID matching, per-line rounding, coupon rules, tax allocation, and free shipping at a threshold. These are precisely the behaviors a naive rewrite may silently change.

```sh
python .agents/skills/legacy-strangler/scripts/dependency_mapper.py examples/js-to-ts-sample
```

Then ask your agent to migrate `legacy_cart.js` to TypeScript with characterization tests first. Suggested cases are listed in the sample's [README](examples/js-to-ts-sample/README.md).

## Migration plan and completion gates

The template at `.agents/skills/legacy-strangler/templates/MIGRATION_PLAN.md` is copied to the target repository root as `MIGRATION_PLAN.md`. It tracks target architecture, risky business rules, module order, test state, and commit hashes. Existing plans should be updated without removing their history or owner-authored content.

A slice is ready to close only when:

- The old behavior has a documented, executable characterization baseline.
- Relevant boundary cases and side effects have been checked against the replacement.
- The adapter/cutover path and rollback path have both been understood.
- The repository's required checks pass, with results recorded accurately.
- No required caller still depends on the implementation being removed.
- The plan and migration commit identify the completed module.

If a check fails, stop, preserve the legacy route, record the failure, and roll back only the current slice. Never use a blanket reset that could discard unrelated work.

## Comparison

| Concern | Unstructured broad migration | With `legacy-strangler` |
|---|---|---|
| Planning | Rewrite scope is chosen before coupling is understood | Dependency map informs a leaf-to-core sequence |
| Behavior | Replacement is built from inferred intent | Current behavior is captured before conversion |
| Cutover | Existing implementation may be replaced at once | Parallel implementation uses a reversible seam |
| Regression scope | Many modules change before failures surface | One bounded capability changes at a time |
| Failure response | Large partial rewrite is difficult to unwind | Current slice stops and rolls back safely |
| Cleanup | Legacy code can disappear early | Removal follows caller and test verification |

## Compatibility and boundaries

The skill is plain Markdown plus a Python standard-library script and SVG asset. It does not require a hosted service, API key, runtime dependency, or agent-specific execution framework. Cross-agent compatibility means agents can read the open `SKILL.md` bundle; each product may still use different discovery paths and invocation behavior. The skill's dependency graph is heuristic, and tests provide evidence only for behaviors they exercise.

## Before publishing

1. Check that the install command points to `rheme18/legacy-strangler` and works from a clean project.
2. Run the mapper against both the sample and repository root, and inspect JSON output.
3. Validate the `SKILL.md` frontmatter, check all referenced paths, and render the SVG icon in a browser or image viewer.
4. Copy the skill to each agent's native discovery path and confirm the agent can load its script and plan template.
5. Review the diff and `git diff --check`; verify that no generated caches, secrets, or temporary files are included.
6. Try a small migration in a disposable project before adopting the workflow on production code.

## License

MIT. See [LICENSE](LICENSE).
