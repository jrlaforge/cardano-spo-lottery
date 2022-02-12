test:
	pytest --tb=short

watch-tests:
	ls *.py | entr pytest --tb=short

black:
	black -l 119 $$(find . -name "*.py" -not -path "./venv/*")
