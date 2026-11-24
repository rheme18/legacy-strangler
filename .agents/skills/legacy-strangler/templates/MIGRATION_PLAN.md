# Migration Plan

## Project

- **Baseline revision:** <!-- git commit or other stable identifier -->
- **Target architecture:** <!-- language, framework, runtime, major boundaries -->
- **Scope and exclusions:** <!-- what is and is not part of this migration -->
- **Baseline checks:** <!-- commands and current results -->

## Risky business rules

| Rule / observed behavior | Owning module | Characterization coverage | Risk / open question |
|---|---|---|---|
| <!-- e.g. tax rounds per line, not per order --> | | | |

## Module migration order

Order modules from low-coupling leaf candidates toward shared/core modules. Include cycles and unresolved dynamic dependencies as explicit risks.

| Order | Module (checkbox) | Dependencies / callers | Risk | Test status | Commit hash |
|---:|---|---|---|---|---|
| 1 | [ ] <!-- module --> | | | Not started | |

## Slice log

| Date | Module | Characterization baseline | Replacement checks | Cutover / rollback notes | Commit hash |
|---|---|---|---|---|---|
| | | | | | |
