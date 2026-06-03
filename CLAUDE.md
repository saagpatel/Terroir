# Terroir

iOS app (Swift/SwiftUI + SceneKit) that translates real geographic and environmental data into flavor profiles using sommelier vocabulary. Users spin a 3D globe, tap any location, and get a flavor card — radial chart + templated prose from soil type, climate, vegetation index, elevation, and coastal proximity. $4.99 one-time App Store pricing.

## Stack

- Language: Swift 5.10+
- UI Framework: SwiftUI — iOS 17.0+ deployment target
- 3D Globe: SceneKit — bundled with iOS, no third-party dependency
- Binary Format: FlatBuffers 25.x — random-access offline flavor grid without full decompression
- Compression: LZ4 via Apple's `Compression` framework (COMPRESSION_LZ4_RAW mode)
- Data Pipeline: Python 3.11+ with rasterio, numpy, pyproj (offline, not part of iOS build)
- Enrichment Backend: CloudKit Functions (primary) / Vercel Edge Functions (fallback)
- CI: GitHub Actions

## Build / Test / Run

Build and run on simulator or device. The prebuilt `terroir.bin` is included — no data pipeline run required.

Run unit tests before committing any change to FlavorLookup, TemplateEngine, or GeoCoordinate math.

## Architecture Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Grid resolution | 0.5° (~25km equatorial) — 360×720 = 259,200 cells | Balances binary size (~45MB) vs. flavor distinctiveness; imperceptible difference vs 10km |
| Flavor dimensions | 12: earthy, mineral, bright, citric, floral, herbaceous, smoky, woody, saline, tannic, vegetal, aromatic | Full sommelier vocabulary without over-engineering |
| Binary format | FlatBuffers + LZ4 | Read-only spatial lookup by integer index — faster than SQLite, simpler than custom format |
| Flavor descriptions | Procedural templates only — no AI generation | Consistent, instant, zero API cost for core experience |
| Data delivery | Hybrid: offline bundle (base profile) + CloudKit/Vercel API (More Detail enrichment) | Core tap→card works offline; enrichment adds premium depth |
| Ocean handling | 3 maritime bands (polar/temperate/tropical) returning saline/mineral profiles | Better UX than blank card or error |
| Pricing | $4.99 one-time, no IAP in v1 | Niche audience pays for quality; avoid subscription complexity for first launch |
| Globe texture | 4096×2048 base, 2048×1024 overlay layers | Sharp on ProMotion; fits GPU memory on iPhone 12+ |

## Conventions

- Scope: implement only features in the current phase of IMPLEMENTATION-ROADMAP.md
- UI: use SwiftUI for all UI; globe is SCNView wrapped in UIViewRepresentable — keep UIKit out of SwiftUI views except via UIViewRepresentable
- Concurrency: all async work via async/await; avoid DispatchQueue.main.async except when bridging legacy SceneKit callbacks
- Grid lookups: nearest-neighbor only — bilinear interpolation is explicitly excluded at 0.5° resolution
- Persistence: the flavor grid is a static bundled binary; use no localStorage, UserDefaults, or CoreData — no user data is persisted in v1
- Privacy: no third-party analytics, crash reporting, or tracking SDKs — privacy label must stay clean
- Dependencies: FlatBuffers Swift runtime (via SPM) is the only permitted third-party Swift package
- Naming: PascalCase for types and files; camelCase for properties and functions
- Commits: conventional commits — feat:, fix:, chore:, test:

<!-- portfolio-context:start -->
# Portfolio Context

## What This Project Is

Terroir is a premium iOS app (Swift/SwiftUI + SceneKit) that translates real geographic and environmental data into flavor profiles using sommelier vocabulary. Users spin a 3D globe, tap any location on Earth, and receive a flavor card — a radial chart and templated prose built from soil type, climate, vegetation index, elevation, and coastal proximity. Targets $4.99 one-time pricing on the App Store.

## Current State

**Phases 0–3 complete; current phase: Phase 4 — TestFlight + App Store Submission**
See IMPLEMENTATION-ROADMAP.md for full phase details and acceptance criteria.

## Stack

- Language: Swift 5.10+
- UI Framework: SwiftUI — iOS 17.0+ deployment target
- 3D Globe: SceneKit — bundled with iOS, no third-party dependency
- Binary Format: FlatBuffers 25.x — random-access offline flavor grid without full decompression
- Compression: LZ4 via Apple's `Compression` framework (COMPRESSION_LZ4_RAW mode)
- Data Pipeline: Python 3.11+ with rasterio, numpy, pyproj (offline, not part of iOS build)
- Enrichment Backend: CloudKit Functions (primary) / Vercel Edge Functions (fallback)
- CI: GitHub Actions

## How To Run

Build and run on simulator or device. The prebuilt `terroir.bin` is included — no data pipeline run required.

## Known Risks

- Do not add features not in the current phase of IMPLEMENTATION-ROADMAP.md
- Do not use UIKit directly — globe is SCNView wrapped in UIViewRepresentable; all other UI is SwiftUI
- Do not block the UI thread for flavor lookups — all file I/O and geocoder calls are async
- Do not use localStorage, UserDefaults, or CoreData — the flavor grid is a static bundled binary; no user data is persisted in v1
- Do not add any third-party analytics, crash reporting, or tracking SDKs
- Do not use bilinear interpolation for grid lookups — nearest-neighbor is locked and sufficient at 0.5° resolution

## Next Recommended Move

Use this context plus the README and supporting docs to resume the next active task, then promote the repo beyond minimum-viable by capturing a dedicated handoff, roadmap, or discovery artifact.

<!-- portfolio-context:end -->

<!-- secondbrain-breadcrumb -->
## SecondBrain knowledge vault

Prior lessons, decisions, and context for this project live in SecondBrain at `wiki/maps/projects/terroir.md`. The whole vault is searchable via the `engraph` MCP — query it for this project + its stack before non-trivial work.
