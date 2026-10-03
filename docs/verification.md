# Local verification

The maintained GitHub default is `feat/data-pipeline`. Use the repository root
unless a command below explicitly changes directory. This is an Xcode iOS app
and a Python data pipeline, not a Swift package: there is no root `Package.swift`.

## Safe pipeline smoke

Use Python 3.12+ and an isolated virtual environment. The requirements file
contains lower bounds, not a lock; dependency installation may download packages.
From the repository root:

```sh
python3 -m venv data-pipeline/venv
. data-pipeline/venv/bin/activate
python -m pip install -r data-pipeline/requirements.txt
cd data-pipeline
python -m pytest tests/test_flavor_engine.py -q
```

The focused tests construct synthetic arrays in memory. They do not download
geographic data, generate production resources or contact enrichment services.
For validation or overlay changes, select the matching `tests/test_validate.py`
or `tests/test_bake_overlays.py` module from this same directory.

The broader suite includes encoding tests that import generated FlatBuffers
bindings. Install the separate `flatc` compiler (the Python `flatbuffers` package
is not the compiler), activate the environment, then from `data-pipeline/`:

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
The `TerroirTests` and `TerroirUITests` targets live in the Xcode project, not a
Swift package. For changed screens, exercise tap-to-card and sharing in the
simulator with valid synthetic resources; avoid location permission and online
More Detail/enrichment actions for an offline check. iOS has no browser lane.
No archive, signing, App Store upload or deployment is needed for local verification.
