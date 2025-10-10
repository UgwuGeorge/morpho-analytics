.PHONY: help build run test sbom

IMAGE := morpho-analytics

help:
	@echo "Targets: build, run, hub-run, test, sbom"

build:
	docker build -t $(IMAGE) .

run:
	@echo "Running $(IMAGE) on examples/synth.npy -> report.json/png"
	docker run --rm -u $$(id -u):$$(id -g) -v "$(PWD)/examples":/data $(IMAGE) report /data/synth.npy --out /data/report.json --fig /data/report.png

hub-run:
	@echo "Running eliotsystem/$(IMAGE):latest on examples/synth.npy -> report.json/png"
	docker run --rm -v "$(PWD)/examples":/data eliotsystem/$(IMAGE):latest report /data/synth.npy --out /data/report.json --fig /data/report.png

test:
	python -m unittest discover -s tests -p "test_*.py"

sbom:
	pip freeze > SBOM.txt
