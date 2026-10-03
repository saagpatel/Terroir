# Terroir

## Overview
Terroir is a premium iOS app (Swift/SwiftUI + SceneKit) that translates real geographic and environmental data into flavor profiles using sommelier vocabulary. Users spin a 3D globe, tap any location on Earth, and receive a flavor card — a radial chart and templated prose built from soil type, climate, vegetation index, elevation, and coastal proximity. Targets $4.99 one-time pricing on the App Store.

## Tech Stack
- Language: Swift 5.10+
- UI Framework: SwiftUI — iOS 17.0 deployment target
- 3D Globe: SceneKit — bundled with iOS, no third-party dependency
- Binary Format: FlatBuffers 25.12.19 — indexed offline flavor grid after full decompression at launch
- Compression: LZ4 via Apple's `Compression` framework (COMPRESSION_LZ4_RAW mode)
- Data Pipeline: Python 3.11+ with rasterio, numpy, pyproj (offline, not part of iOS build)
- Enrichment Backend: CloudKit Functions (primary) / Vercel Edge Functions (fallback) — planned (Phase 3); currently bundled mock data with an in-memory cache
- CI: GitHub Actions (`.github/workflows/ci.yml`); Xcode Cloud planned for Phase 4 archive/upload

## Development Conventions
- Do not use UIKit directly — globe is SCNView wrapped in UIViewRepresentable; all other UI is SwiftUI (known exception: `ShareSheet` wraps `UIActivityViewController`, TerroirApp.swift)
- Swift strict concurrency — all async work via async/await, no DispatchQueue.main.async unless bridging legacy SceneKit callbacks
- PascalCase for types and files; camelCase for properties and functions
- Unit tests for all data transforms before committing (FlavorLookup, TemplateEngine, GeoCoordinate math)
- Conventional commits: feat:, fix:, chore:, test:
- No third-party Swift packages except FlatBuffers Swift runtime (via SPM)
- No third-party analytics or tracking SDKs — privacy label must stay clean

## Current Phase
**Phase 3: Polish + Enrichment + App Store Prep** (Phases 0–2 code implemented; share card and overlays implemented; enrichment backend and App Store preparation remain pending). Generated resources must be prepared separately; roadmap acceptance checks are not recorded as complete.
See IMPLEMENTATION-ROADMAP.md for planned phase details and acceptance criteria; it is not a completion record.

## Key Decisions
| Decision | Choice | Why |
|----------|--------|-----|
| Grid resolution | 0.5° — 360×720 = 259,200 cells | Balances binary size (~45MB) vs. flavor distinctiveness; imperceptible difference vs 10km |
| Flavor dimensions | 12: earthy, mineral, bright, citric, floral, herbaceous, smoky, woody, saline, tannic, vegetal, aromatic | Full sommelier vocabulary without over-engineering |
| Binary format | FlatBuffers + LZ4 | Read-only spatial lookup by integer index — faster than SQLite, simpler than custom format |
| Flavor descriptions | Procedural templates only — no AI generation | Consistent, instant, zero API cost for core experience |
| Data delivery | Hybrid: offline bundle (base profile) + CloudKit/Vercel API (More Detail enrichment); currently bundled mock data, backend not yet implemented | Core tap→card works offline; enrichment adds premium depth |
| Ocean handling | 3 maritime bands (polar/temperate/tropical) returning saline/mineral profiles | Better UX than blank card or error |
| Pricing | $4.99 one-time, no IAP in v1 | Niche audience pays for quality; avoid subscription complexity for first launch |
| Globe texture | 4096×2048 base, 2048×1024 overlay layers | Sharp on ProMotion; fits GPU memory on iPhone 12+ |

Known gap: `AppState.handleGlobeTap` awaits reverse geocoding before showing the card, with coordinate fallback on failure. This deviates from the roadmap requirement to render the base card immediately and update its location name asynchronously.

## Do NOT
- Prepare valid generated resources before running the app or UI tests; CI placeholders support compilation only (see docs/verification.md)
- Do not add features not in the current phase of IMPLEMENTATION-ROADMAP.md
- Do not use UIKit directly — globe is SCNView wrapped in UIViewRepresentable; all other UI is SwiftUI (known exception: `ShareSheet` wraps `UIActivityViewController`, TerroirApp.swift)
- Do not block the UI thread for flavor lookups — all file I/O and geocoder calls are async
- Do not use localStorage, UserDefaults, or CoreData — the flavor grid is a static bundled binary; no user data is persisted in v1
- Do not add any third-party analytics, crash reporting, or tracking SDKs
- Do not use bilinear interpolation for grid lookups — nearest-neighbor is locked and sufficient at 0.5° resolution

<!-- portfolio-context:start -->
# Portfolio Context

## What This Project Is

Terroir is a premium iOS app (Swift/SwiftUI + SceneKit) that translates real geographic and environmental data into flavor profiles using sommelier vocabulary. Users spin a 3D globe, tap any location on Earth, and receive a flavor card — a radial chart and templated prose built from soil type, climate, vegetation index, elevation, and coastal proximity. Targets $4.99 one-time pricing on the App Store.

## Current State

**Phase 3: Polish + Enrichment + App Store Prep** (Phases 0–2 code implemented; share card and overlays implemented; enrichment backend and App Store preparation remain pending). Generated resources must be prepared separately; roadmap acceptance checks are not recorded as complete.
See IMPLEMENTATION-ROADMAP.md for planned phase details and acceptance criteria; it is not a completion record.

## Stack

- Language: Swift 5.10+
- UI Framework: SwiftUI — iOS 17.0 deployment target
- 3D Globe: SceneKit — bundled with iOS, no third-party dependency
- Binary Format: FlatBuffers 25.12.19 — indexed offline flavor grid after full decompression at launch
- Compression: LZ4 via Apple's `Compression` framework (COMPRESSION_LZ4_RAW mode)
- Data Pipeline: Python 3.11+ with rasterio, numpy, pyproj (offline, not part of iOS build)
- Enrichment Backend: CloudKit Functions (primary) / Vercel Edge Functions (fallback) — planned (Phase 3); currently bundled mock data with an in-memory cache
- CI: GitHub Actions (`.github/workflows/ci.yml`); Xcode Cloud planned for Phase 4 archive/upload

## How To Run

See [verification guidance](docs/verification.md) for safe synthetic checks and iOS resource prerequisites. Generated `terroir.bin` and resources are ignored and must be prepared before running the app.

## Known Risks

- Prepare valid generated resources before running the app or UI tests; CI placeholders support compilation only (see docs/verification.md)
- Do not add features not in the current phase of IMPLEMENTATION-ROADMAP.md
- Do not use UIKit directly — globe is SCNView wrapped in UIViewRepresentable; all other UI is SwiftUI (known exception: `ShareSheet` wraps `UIActivityViewController`, TerroirApp.swift)
- Do not block the UI thread for flavor lookups — all file I/O and geocoder calls are async
- Do not use localStorage, UserDefaults, or CoreData — the flavor grid is a static bundled binary; no user data is persisted in v1
- Do not add any third-party analytics, crash reporting, or tracking SDKs
- Do not use bilinear interpolation for grid lookups — nearest-neighbor is locked and sufficient at 0.5° resolution

## Next Recommended Move

Use this context plus the README and supporting docs to resume the next active task, then promote the repo beyond minimum-viable by capturing a dedicated handoff, roadmap, or discovery artifact.

<!-- portfolio-context:end -->
