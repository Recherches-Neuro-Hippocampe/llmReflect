lint:
	python -m flake8 --ignore migrations/**
run:
	python main.py
doc:
	pdoc --output-dir=docs llmreflect
test:
	pytest -s