# Terroir — Portfolio Disposition

**Status:** Active (iOS App Store prep arc) — SwiftUI iOS flavor-
profile app with **complete Phases 0–3** (data pipeline + iOS
scaffold). App Store prep is **partial**: DEVELOPMENT_TEAM and
PrivacyInfo.xcprivacy confirmed on `main`, but
**`APPSTORE-METADATA.md` does NOT exist yet**. **Tenth iOS App
Store cluster member, but the first classified as Active (prep arc
in flight)**, not Release Frozen. *(Branch divergence documented
below was resolved by `b95ab97 chore: merge feat/data-pipeline into
main` — both branches are now unified on `main`.)*

> Disposition uses strict `origin/HEAD` verification.
> **Documents two new trap shapes**:
> (1) origin/HEAD-points-to-feat-branch (PR base must be the feat
> branch, not main).
> (2) **Divergent-branches trap**: both `origin/main` and
> `origin/feat/data-pipeline` have substantive work, neither is a
> subset of the other.

---

## Verification posture

This repo has **only `origin`** (`saagpatel/Terroir`) — no
`legacy-origin` remote. Clean migration state.

**Two-branch divergence on canonical remote** observed during this
audit (load-bearing for ship-readiness):

- **`origin/HEAD → refs/heads/feat/data-pipeline`** (operator's
  stated canonical default).
- The two branches share a merge base at `453364a chore(ios): add
  Xcode project and gitignore iOS binary resources`.
- **`origin/main` has 6 commits BEYOND the merge base** that are
  NOT on `feat/data-pipeline`:
  - `88ad7da chore: add MIT license`
  - `3272fff fix(build): add DEVELOPMENT_TEAM for App Store signing`
  - `a4d106c fix(security): add PrivacyInfo.xcprivacy privacy
    manifest`
  - `1964379 Merge pull request #2 from saagpatel/feat/add-ci`
  - `3f86f79 feat: add GitHub Actions CI workflow`
  - `c7be806 Merge pull request #1 from saagpatel/feat/data-pipeline`
- **`origin/feat/data-pipeline` has 12 commits BEYOND the merge
  base** that are NOT on `main`:
  - Full OSS scaffolding wave (CHANGELOG, PR template, issue
    templates, CoC, Makefile, Dependabot, contributing, security
    policy, MIT license, README docs)
  - Includes a parallel `feat: add GitHub Actions CI workflow`
    commit (`53967cf`, distinct SHA from main's CI commit)
- **Neither branch has `APPSTORE-METADATA.md`**.

This is a **divergent-branches trap**. The operator must either:
- Merge `origin/main` → `origin/feat/data-pipeline` (or vice
  versa) to consolidate, then proceed with App Store prep, OR
- Cherry-pick the App Store prep commits from `main` onto
  `feat/data-pipeline` (or vice versa), then resolve which
  branch is canonical going forward.

Default branch on origin: `feat/data-pipeline` (per
`git ls-remote --symref origin HEAD`).

Specifically verified on `origin/feat/data-pipeline` (canonical
default):

- Tip: `0336d15` chore: add initial CHANGELOG
- OSS scaffolding wave on this branch: CHANGELOG, PR template,
  issue templates, CoC, Makefile, Dependabot, contributing,
  security policy, MIT license, README docs
- Substantive feat commits inherited from merge-base ancestry:
  Phase 0 data pipeline + Phase 1-3 iOS scaffold + xcodeproj.
- **MISSING (relative to origin/main)**: DEVELOPMENT_TEAM,
  PrivacyInfo.xcprivacy, original GitHub Actions CI workflow
  commit
- **MISSING**: `APPSTORE-METADATA.md`

---

## Current state in one paragraph

Terroir is a SwiftUI iOS flavor-profile app (per memory: track and
visualize flavor profiles for foods / wines / etc.). The Phase 0
data pipeline (likely flavor-data ingestion / normalization)
plus Phases 1-3 iOS app scaffold are complete. Per memory: Phases
0-3 done, pending App Store. **The canonical state is
`origin/feat/data-pipeline`**, which has the full OSS scaffolding
wave (MIT, security policy, CoC, Dependabot, etc.) but is
**missing the App Store prep commits that landed on `origin/main`**:
DEVELOPMENT_TEAM, PrivacyInfo.xcprivacy. Neither branch has an
`APPSTORE-METADATA.md` file. This row is **Active**, not Release
Frozen, because the App Store prep is partial and the two-branch
divergence is unresolved.

---

## Why "Active (iOS App Store prep arc)" — distinct from other iOS cluster members

The first 9 iOS cluster members (Calibrate, Chromafield, Ghost
Routes, Nocturne, Tide Engine, Liminal, Redact, Room Tone,
Seismoscope) all reached **Release Frozen** with the full prep
signature: DEVELOPMENT_TEAM + Privacy Manifest + APPSTORE-METADATA
+ ExportOptions + privacy policy + (optional fastlane deliver) +
(optional AI icon).

Terroir is **mid-prep**:

| Signal | Other iOS cluster members | **Terroir** |
|---|---|---|
| DEVELOPMENT_TEAM | All ✓ | ✓ on `main` |
| Privacy Manifest | All ✓ | ✓ on `main` |
| APPSTORE-METADATA.md | All ✓ | **MISSING from both branches** |
| Privacy policy | All ✓ | **MISSING from both branches** (only via the CI / MIT scaffolding) |
| Branch divergence | None | **Divergent-branches trap** |

This is Active — the arc to complete is App Store prep + branch
consolidation. Once both branches converge and APPSTORE-METADATA
lands, Terroir transitions to Release Frozen iOS App Store cluster
member.

---

## Cluster taxonomy update

| Cluster | Count | Notes |
|---|---|---|
| **iOS App Store** | **10** | 9 Release Frozen + **1 Active (Terroir, prep arc)** |
| (others unchanged) | | |

Terroir is the first iOS cluster member to be Active, not Release
Frozen. The cluster is mature enough to hold both states — same
disposition lattice principle established by the PyPI cluster
(MCPAudit Release Frozen + mcpforge Active).

---

## Unblock trigger (operator)

This row's blocker is **operator-side branch consolidation +
metadata authoring**, not Apple credentials:

1. ~~**Resolve branch divergence.**~~ **DONE** — `b95ab97 chore:
   merge feat/data-pipeline into main`.
2. **Author `APPSTORE-METADATA.md`** with the identity / keywords /
   description / category / pricing fields. Follow the established
   pattern from R12-R14 iOS dispositions.
3. **Privacy policy file** (`PRIVACY.md`) — local-first flavor data
   has low data-collection surface; the policy can be brief.
4. Standard App Store prep continuation:
   - Copyright in metadata + ExportOptions.plist
   - App Store archive prep (signing, icons, screenshots)
   - Optional fastlane deliver config
   - Optional AI-generated final icon (replacing placeholder)
5. **App Store Connect record** + pricing tier decision (Free vs
   Paid — flavor profile apps could go either direction).
6. **Submit for Review.**

Estimated operator time once branch divergence is resolved: ~6-8
hours to reach App-Store-ready (same prep cadence as Liminal /
Chromafield / etc., plus the upfront branch merge work).

---

## Portfolio operating system instructions

| Aspect | Posture |
|---|---|
| Portfolio status | `Active (iOS App Store prep arc)` |
| Distribution channel | **App Store Connect** (planned; not yet metadata-prepared) |
| Current branch state | **Merged** — `feat/data-pipeline` merged into `main` (`b95ab97`); `main` is now canonical |
| Canonical default | `main` (merged; see note above) |
| Review cadence | Active — driven by branch consolidation + metadata authoring |
| Resurface conditions | (a) Branch consolidation, (b) `APPSTORE-METADATA.md` authored, (c) full prep cadence applied, then transition to Release Frozen, or (d) decision to abandon iOS direction |
| Co-batch with | iOS App Store cluster — **now 10 repos** (9 Release Frozen + 1 Active) |
| Special concern | **DIVERGENT-BRANCHES TRAP.** Operator must consolidate before proceeding with App Store prep. This is the same trap class as the local-main-ahead trap (Tide Engine), but bilateral on origin rather than local-vs-origin. |
| Special concern | **Default branch trap.** `origin/HEAD → feat/data-pipeline`, not `main`. Any tooling defaulting to `origin/main` (CI workflows, README badges, IDE branch UI) needs verification. |
| Special concern | **No APPSTORE-METADATA.md yet.** Operator needs to author this from scratch (or import the pattern from a sibling cluster member's metadata file). |

---

## Why this row documents two new trap shapes

The portfolio disposition campaign has now seen many flavors of
branch trap (legacy-origin, master-tracks-legacy, no-local-main,
master-default, feat-branch-as-default for BHV). Terroir adds:

1. **origin/HEAD points to a feat branch that is NOT the most-
   prepared branch.** Variant of the BrowserHistoryVisualizer
   feat-branch-default trap: in BHV, `feat/initial-release` was
   the most-developed branch and `main` was empty. In Terroir,
   `feat/data-pipeline` is the operator's stated canonical, but
   `origin/main` actually has the App Store prep commits that
   `feat/data-pipeline` lacks. Operator intent and substantive
   state disagree.

2. **Divergent-branches trap.** Both branches have substantive
   work, neither is a subset of the other. The operator's
   workflow forked at the merge base. This is different from the
   local-main-ahead trap (Tide Engine), where the divergence is
   between local clone and origin. Here both divergent branches
   are on origin.

These shapes belong on the cluster-taxonomy session-lessons list.

---

## Reactivation procedure

1. ~~**Re-confirm `origin/HEAD`**~~ **DONE** — `main` is now
   canonical (`b95ab97` merge).
2. ~~**Resolve branch divergence**~~ **DONE** — merged.
3. Review stash `r14-terroir-stash` (CLAUDE.md mod, untracked
   `.claude/`).
4. Once consolidated, follow the standard iOS App Store cluster
   prep cadence (author APPSTORE-METADATA, copyright, archive
   prep, fastlane deliver, AI icon).
5. Run `xcodebuild test` on the consolidated branch.

---

## Last known reference

| Field | Value |
|---|---|
| `origin/HEAD` | `refs/heads/main` (post-merge; branches unified) |
| `origin/main` tip | `7b6b940` docs: lean CLAUDE.md (claude-md-lint) |
| Default branch | **`main`** |
| Build system | iOS / Swift / SwiftUI / XCTest + Python (data pipeline; numpy, pillow, rasterio per Dependabot configs) |
| Phases shipped | Phases 0–3 (data pipeline + iOS scaffold) — all confirmed in code |
| Release scaffolding state | **Partial.** DEVELOPMENT_TEAM + PrivacyInfo.xcprivacy present on `main`. `APPSTORE-METADATA.md` still missing. |
| Distribution channel (planned) | App Store Connect — $4.99 one-time |
| Blocker | **APPSTORE-METADATA authoring (operator-only)** |
| Migration state | No `legacy-origin` remote |
| Distinguishing feature | **Tenth iOS App Store cluster member AND first Active state in the cluster.** Introduces two new trap shapes: (1) origin/HEAD-on-feat-branch with substantive work split, (2) divergent-branches trap on origin (bilateral, not local-vs-origin). |
