include .env
lint:
	python -m flake8 --ignore migrations/**
run:
	python main.py