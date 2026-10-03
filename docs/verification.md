# Local verification

The maintained GitHub default is `feat/data-pipeline`. Use the repository root
unless a command below explicitly changes directory. This is an Xcode iOS app
and a Python data pipeline, not a Swift package: there is no root `Package.swift`.

## Safe pipeline smoke

Use Python 3.12 and uv with an isolated virtual environment. The source
requirements retain their lower bounds; `requirements.lock` records exact
versions and package hashes. The setup script installs from that lock and
verifies a pinned FlatBuffers 25.12.19 compiler release checksum. Linux x86_64
and macOS arm64/x86_64 are supported; other architectures fail explicitly.
Installation downloads packages and the compiler, but never geographic data.
From the repository root:

```sh
bash data-pipeline/setup.sh
. data-pipeline/venv/bin/activate
cd data-pipeline
python -m pytest tests/test_flavor_engine.py -q
```

The focused tests construct synthetic arrays in memory. They do not download
geographic data, generate production resources or contact enrichment services.
For validation or overlay changes, select the matching `tests/test_validate.py`
or `tests/test_bake_overlays.py` module from this same directory.

The broader suite includes encoding tests that import generated FlatBuffers
bindings. The setup script supplies `flatc` inside the virtual environment
(the Python `flatbuffers` package alone is not the compiler). Activate the
environment, then from `data-pipeline/`:

```sh
make schema
python -m pytest tests/ -v
```

`make schema` runs `flatc --python --gen-object-api terroir.fbs` and writes the
ignored `data-pipeline/Terroir/` bindings. No lint/format/typecheck tool is
configured for this pipeline. The root `make smoke` and `make test` delegate to
these lanes; the latter requires `flatc` and generates bindings first.

Do not run `01_download_sources.sh`, `make run`, `make synthetic`, or cleanup
just to verify instructions. They download data or write/replace generated
outputs. Real-data accuracy and production resource generation are separate
acceptance lanes; synthetic tests do not establish either.

To deliberately refresh the lock after requirement changes, use uv 0.12.22:

```sh
uv pip compile data-pipeline/requirements.txt --universal --python-version 3.12 \
  --generate-hashes -o data-pipeline/requirements.lock
```

Review the resulting graph and run the synthetic suite before committing.
Re-running setup retains valid dependency/compiler caches; it synchronizes
packages to the committed lock and rejects corrupt compiler archives. A Mac
pass does not establish Linux or iOS runtime behavior.

## iOS build and behavior

The checked-in project is `terroir-ios/Terroir.xcodeproj`; the optional XcodeGen
spec is `terroir-ios/project.yml`. Use macOS, Xcode 15+ and an iOS 17+ simulator;
XcodeGen 2.35+ is only needed to regenerate the project from that directory.
Swift packages are resolved through the project's checked-in `Package.resolved`.

A fresh checkout lacks ignored resources in `terroir-ios/Terroir/Resources/`.
Prepare valid data/assets before app or UI tests. The resource preparation in
[GitHub CI](../.github/workflows/ci.yml) creates compilation placeholders only;
its `xcodebuild build` does not prove the flavor grid loads or UI behavior works.
With appropriate resources, from the repository root:

```sh
xcodebuild build -project terroir-ios/Terroir.xcodeproj -scheme Terroir \
  -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO
```

For broader tests use `xcodebuild test` with the same project/scheme and an
available named simulator or UUID (discover locally with `xcrun simctl list devices available`).
The unit tests import `Testing`, so the test toolchain must provide Swift Testing.
The `TerroirTests` and `TerroirUITests` targets live in the Xcode project, not a
Swift package. For changed screens, exercise tap-to-card and sharing in the
simulator with valid synthetic resources. More Detail uses bundled mock data,
not a network backend. Globe taps await CLGeocoder reverse geocoding before
showing the card; this may contact a service and falls back to coordinates on
failure. Disable networking and avoid location permission for an offline check.
iOS has no browser lane.
No archive, signing, App Store upload or deployment is needed for local verification.
