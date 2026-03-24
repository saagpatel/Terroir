.PHONY: schema setup run validate clean test synthetic

schema:
	flatc --python --gen-object-api terroir.fbs
	@echo "Python bindings generated in Terroir/"

setup: schema
	pip install -r requirements.txt

synthetic: schema
	python generate_synthetic.py
	python 03_flavor_engine.py
	@echo "Synthetic pipeline complete — run 'make validate' to check"

run: schema
	python 02_rasterize.py
	python 03_flavor_engine.py
	python 04_validate.py
	python 05_encode_binary.py
	python 06_bake_overlays.py
	@echo "Full pipeline complete — terroir.bin ready"

validate:
	python 04_validate.py

test:
	pytest tests/ -v

clean:
	rm -rf intermediate/*.npy Terroir/ terroir.bin
	@echo "Cleaned intermediate files and outputs"
