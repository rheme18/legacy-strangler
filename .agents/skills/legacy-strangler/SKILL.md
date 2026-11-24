---
name: legacy-strangler
description: >-
  Safely migrate, refactor, upgrade, or convert legacy codebases incrementally
  (including JavaScript to TypeScript, jQuery to React, PHP or Flask to
  Node.js/FastAPI, class components to hooks, and framework or runtime upgrades).
  Use whenever a user asks to migrate, refactor legacy code, upgrade, modernize,
  port, or convert an existing application or module. Enforces characterization
  tests, dependency-aware sequencing, parallel implementations, and reversible
  cutovers instead of a big-bang rewrite.
version: 1.0.0
---

# Legacy Strangler Migration

Migrate legacy systems in small, reversible slices. Preserve observable behavior unless the user explicitly approves a behavior change. Keep the old implementation available until its replacement is proven against the agreed test suite.

## Golden rules

- **Never change or replace the entire project in one migration step.** Work on one bounded module or capability at a time.
- **Never delete or overwrite a legacy file until its replacement passes all relevant characterization tests and the project's required checks.** Keep a rollback path until then.
- Map dependencies before choosing migration order. Start with low-coupling leaf candidates, then move toward shared/core modules.
- Do not silently “fix” legacy quirks during a behavior-preserving migration. Record them as business rules; propose behavior changes separately.
- Make every slice reviewable and reversible. Do not commit unrelated formatting, dependency upgrades, or cleanup with a migration slice.
- Respect repository instructions and existing test/build conventions. Do not claim checks passed unless they were actually run.
- If the working tree contains user changes, preserve them. Never use destructive reset/checkout commands on uncommitted work.

## Required workflow

### Phase 1 — Discover and map

1. Inspect repository instructions, working-tree status, language/runtime, test commands, and relevant module boundaries.
2. Run this skill's dependency mapper from the repository root:

   ```sh
   python .agents/skills/legacy-strangler/scripts/dependency_mapper.py . --format markdown
   ```

   Use `--format json` for machine-readable output. Review the detected edges; static import scanning is approximate and must not be treated as a complete runtime call graph.
3. Copy `.agents/skills/legacy-strangler/templates/MIGRATION_PLAN.md` to the project root as `MIGRATION_PLAN.md` if it does not exist. If it already exists, update it without discarding its history or user-authored content.
4. Record the target architecture, risky business rules, test baseline, and a migration order. Begin with leaf candidates (fewest dependencies and low incoming coupling); advance toward core modules only after slices are complete. Note cycles, dynamic imports, reflection, and unresolved edges as risks.
5. Establish a clean, identifiable rollback point. Do not commit or stash user work without authorization.

### Phase 2 — Characterization testing

1. Before transforming a module, write automated tests that capture its current externally observable inputs, outputs, errors, and side effects.
2. Include boundary values and edge cases found in code, callers, fixtures, and documentation: missing/null values, empty collections, rounding, ordering, time zones, retries, and error paths where applicable.
3. Run the tests against the legacy implementation and record the baseline in `MIGRATION_PLAN.md`. If existing behavior is ambiguous, document the uncertainty and preserve observed behavior.
4. Do not begin replacement work while the relevant baseline tests fail. Diagnose whether the failure is pre-existing and record it; do not disguise it as a migration pass.

### Phase 3 — Side-by-side strangler implementation

1. Add the modern implementation beside the legacy implementation, using the repository's naming and build conventions.
2. Route a bounded call path through an adapter, proxy, compatibility facade, or feature flag. Keep the old path available for immediate rollback. Choose a flag only if the application has a safe way to configure and observe it.
3. Run the characterization suite against both implementations. Compare outputs and relevant side effects; investigate every mismatch. Add migration-specific tests for the adapter and routing behavior.
4. Run the relevant unit, integration, type-check, lint, and build checks required by the repository. Record the exact results. Do not claim 100% parity beyond the exercised coverage.
5. If checks fail, stop the cutover, follow Rollback, and update the plan with the failure and next action.

### Phase 4 — Atomic commit and cleanup

1. Only after all required checks are green, route the bounded capability fully to the replacement.
2. Remove the legacy implementation only when the replacement is verified, no required caller still uses it, and rollback is no longer needed for the slice. If deletion is premature or unsafe, retain it and mark the slice incomplete.
3. Review the diff for scope, accidental behavior changes, secrets, and generated files. Update the plan's test status and commit hash.
4. Create one atomic commit for the slice with this exact subject pattern:

   ```text
   refactor(migration): [module_name] migrated via legacy-strangler
   ```

   Replace `[module_name]` with the module identifier. Create a commit only when repository policy permits and the working tree changes belong to this slice. Do not include unrelated or user-authored changes.
5. Proceed to the next module only after this slice is committed and the migration plan is current. If commits are not permitted or requested, stop after presenting the verified diff and mark the slice awaiting commit.

## Rollback protocol

When any characterization, integration, type, lint, or build check fails:

1. Stop migration and do not delete the legacy implementation or advance to another module.
2. Capture the failing command, relevant output, and current plan status. Identify whether the failure is in the adapter, new implementation, environment, or pre-existing baseline.
3. If the current slice has not been committed, revert only the files changed for this slice using targeted edits or `git restore -- <specific-paths>` after confirming those paths contain no user changes. Never run a blanket `git checkout -- .`, `git reset --hard`, or equivalent.
4. If the slice has a migration commit, use `git revert <migration-commit>` to make a safe rollback commit. Do not rewrite shared history. For a private, unpushed commit, discuss alternatives only if the repository's contribution policy requires it.
5. Confirm the adapter/flag routes traffic to the legacy path, rerun the baseline tests, and record the rollback and failure in `MIGRATION_PLAN.md`.
6. Resume only after the cause is understood and the relevant legacy baseline is green. Keep the new code isolated until it is ready for another controlled attempt.

## Completion criteria

A slice is complete only when its behavior contract and known edge cases are covered, required checks pass against the replacement, routing is verified, rollback is understood, and the migration plan records the resulting commit hash (or why no commit was made).
