# Terroir

[![Swift](https://img.shields.io/badge/Swift-f05138?style=flat-square&logo=swift)](#) [![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](#)

> Every place on Earth has a flavor profile. Tap to taste it.

Terroir maps a 12-dimensional flavor profile — earthy, mineral, bright, citric, floral, herbaceous, smoky, woody, saline, tannic, vegetal, aromatic — to every coordinate on the globe. Derived from soil type, climate, elevation, vegetation, and geology, it turns a location into a sommelier's vocabulary.

## Features

- **Interactive 3D globe** — tap any point to retrieve its 12-axis flavor profile instantly
- **Radar chart** — visualizes the full flavor vector for the selected location
- **Overlay modes** — toggle soil, climate, and vegetation layers on the globe
- **Prebuilt binary grid** — 360×720 cell flavor grid (259,200 locations) compressed with LZ4 and loaded at launch
- **Share card** — renders and exports a styled flavor card as an image
- **"My Location" shortcut** — jump to your current coordinates

## Quick Start

### Prerequisites
- Xcode 15+, iOS 17.0+
- XcodeGen (`brew install xcodegen`)

### Installation
```bash
git clone https://github.com/saagpatel/Terroir.git
cd Terroir
xcodegen generate
open Terroir.xcodeproj
```

### Usage
Build and run on simulator or device. The prebuilt `terroir.bin` is included — no data pipeline run required.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Swift 5.10 |
| UI | SwiftUI (dark mode enforced) |
| 3D Globe | SceneKit (GlobeScene) |
| Data format | FlatBuffers (terroir.fbs schema) |
| Compression | LZ4 raw |
| Location | CoreLocation |
| Data pipeline | Python 3 + NumPy (dev-time only) |

## License

MIT
