.PHONY: help build smoke test run
.DEFAULT_GOAL := help

help:
	@echo "See docs/verification.md for environments and resource prerequisites."
	@echo "smoke: synthetic Python flavor tests; test: full Python suite (requires flatc)"
	@echo "build: iOS Simulator compilation (requires Xcode and prepared resources)"

build:
	xcodebuild build -project terroir-ios/Terroir.xcodeproj -scheme Terroir -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO

smoke:
	cd data-pipeline && python -m pytest tests/test_flavor_engine.py -q

test:
	$(MAKE) -C data-pipeline schema
	cd data-pipeline && python -m pytest tests/ -v

run:
	@echo "Prepare valid generated resources, then open terroir-ios/Terroir.xcodeproj; see docs/verification.md."
