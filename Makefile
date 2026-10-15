.PHONY: setup eda pipeline test
setup:
	python -m venv venv && ./venv/bin/pip install -r requirements.txt
eda:
	python -m src.eda
pipeline:
	python -m src.pipeline
test:
	pytest -q
