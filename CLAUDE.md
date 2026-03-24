# Terroir

## Overview
Terroir is a premium iOS app (Swift/SwiftUI + SceneKit) that translates real geographic and environmental data into flavor profiles using sommelier vocabulary. Users spin a 3D globe, tap any location on Earth, and receive a flavor card — a radial chart and templated prose built from soil type, climate, vegetation index, elevation, and coastal proximity. Targets $4.99 one-time pricing on the App Store.

## Tech Stack
- Language: Swift 5.10+
- UI Framework: SwiftUI — iOS 16+ deployment target
- 3D Globe: SceneKit — bundled with iOS, no third-party dependency
- Binary Format: FlatBuffers 23.x — random-access offline flavor grid without full decompression
- Compression: LZ4 via Apple's `Compression` framework (COMPRESSION_LZ4 mode)
- Data Pipeline: Python 3.11+ with rasterio, numpy, pyproj (offline, not part of iOS build)
- Enrichment Backend: CloudKit Functions (primary) / Vercel Edge Functions (fallback)
- CI: Xcode Cloud

## Development Conventions
- SwiftUI for all UI; SceneKit for globe rendering only — do not mix UIKit into SwiftUI views except via UIViewRepresentable for SCNView
- Swift strict concurrency — all async work via async/await, no DispatchQueue.main.async unless bridging legacy SceneKit callbacks
- PascalCase for types and files; camelCase for properties and functions
- Unit tests for all data transforms before committing (FlavorLookup, TemplateEngine, GeoCoordinate math)
- Conventional commits: feat:, fix:, chore:, test:
- No third-party Swift packages except FlatBuffers Swift runtime (via SPM)
- No third-party analytics or tracking SDKs — privacy label must stay clean

## Current Phase
**Phase 0: Data Pipeline**
See IMPLEMENTATION-ROADMAP.md for full phase details and acceptance criteria.

## Key Decisions
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

## Do NOT
- Do not open Xcode until Phase 0 (`terroir.bin`) is complete and passes validation — the data pipeline blocks all downstream iOS work
- Do not add features not in the current phase of IMPLEMENTATION-ROADMAP.md
- Do not use UIKit directly — globe is SCNView wrapped in UIViewRepresentable; all other UI is SwiftUI
- Do not block the UI thread for flavor lookups — all file I/O and geocoder calls are async
- Do not use localStorage, UserDefaults, or CoreData — the flavor grid is a static bundled binary; no user data is persisted in v1
- Do not add any third-party analytics, crash reporting, or tracking SDKs
- Do not use bilinear interpolation for grid lookups — nearest-neighbor is locked and sufficient at 0.5° resolution
