# Terroir

![Swift](https://img.shields.io/badge/Swift-5.10-FA7343?logo=swift&logoColor=white)
![iOS](https://img.shields.io/badge/iOS-17.0%2B-000000?logo=apple&logoColor=white)
![Xcode](https://img.shields.io/badge/Xcode-15%2B-147EFB?logo=xcode&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue)

Explore the flavor identity of any place on Earth. Terroir maps a 12-dimensional flavor profile — earthy, mineral, bright, citric, floral, herbaceous, smoky, woody, saline, tannic, vegetal, aromatic — to every coordinate on the globe, derived from soil type, climate, elevation, vegetation, and geology.

Tap anywhere on an interactive 3D globe to get an instant flavor card for that location. Switch overlays to see the underlying soil, climate, or vegetation layers that shape the profile.

## Features

- **Interactive 3D globe** — tap any point to retrieve its flavor profile
- **12-axis radar chart** — visualizes the full flavor vector for the selected location
- **Overlay modes** — toggle soil, climate, and vegetation layers on the globe
- **Ocean zone handling** — distinct flavor profiles for ocean regions based on zone
- **Enrichment detail** — expanded location context on demand
- **Share card** — render and export a styled flavor card as an image
- **"My Location" shortcut** — jump directly to your current coordinates

## Tech Stack

| Layer | Technology |
|---|---|
| UI | SwiftUI (dark mode enforced) |
| 3D Globe | SceneKit via `GlobeScene` |
| Data format | FlatBuffers (Google) — `terroir.fbs` schema |
| Compression | LZ4 raw — flavor grid decompressed at launch |
| Location | CoreLocation via `LocationService` |
| Data pipeline | Python 3 — soil/climate/NDVI/geology → NumPy → `.bin` |
| State management | `@Observable` / `AppState` |

## Data Pipeline

The `data-pipeline/` directory contains the offline build scripts that produce `terroir.bin` — the binary flavor grid bundled into the app:

1. `01_download_sources.sh` — fetch raw geodata
2. `02_rasterize.py` — rasterize sources to a 360×720 grid (259,200 cells)
3. `03_flavor_engine.py` — apply soil/climate/NDVI/geology weight matrices → 12-dim flavor vectors
4. `04_validate.py` — sanity-check the output grid
5. `05_encode_binary.py` — serialize to FlatBuffers and LZ4-compress
6. `06_bake_overlays.py` — bake soil/climate/vegetation image overlays

The pipeline does not need to be re-run to use the app; a prebuilt `terroir.bin` is included in the bundle.

## Prerequisites

- Xcode 15 or later
- iOS 17.0+ deployment target
- [XcodeGen](https://github.com/yonaskolb/XcodeGen) 2.35+ (to regenerate the `.xcodeproj` from `project.yml`)

## Getting Started

```bash
# Clone the repository
git clone <repo-url>
cd Terroir/terroir-ios

# (Optional) regenerate the Xcode project if project.yml was modified
xcodegen generate

# Open in Xcode
open Terroir.xcodeproj
```

Build and run the `Terroir` scheme on a simulator or device running iOS 17+. No API keys or additional configuration are required.

## Project Structure

```
terroir-ios/
  Terroir/
    App/          # TerroirApp entry point, AppState, GlobeOverlay enum
    Engine/       # FlavorLookup (FlatBuffers actor), FlavorVector, OceanHandler, TemplateEngine
    Models/       # FlavorDimension, GeoCoordinate, EnrichmentData
    Services/     # LocationService (CoreLocation), EnrichmentService
    Views/        # GlobeView, FlavorCardView, RadarChartView, ShareCardView, FlavorCardDetailView
  TerroirTests/
  TerroirUITests/
  project.yml     # XcodeGen project definition
data-pipeline/    # Offline Python scripts to rebuild terroir.bin
```

## Screenshot

<!-- Add a screenshot here -->

## License

MIT — see [LICENSE](LICENSE).
