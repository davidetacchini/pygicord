.PHONY: clean
clean:
	rm -rf ./__pycache__
	rm -rf */__pycache__

.PHONY: install
install:
	@pip install --upgrade pip
	@pip install -r requirements.txt -r requirements-dev.txt

.PHONY: format
format:
	isort .
	black --exclude=env --line-length=88 .
	flake8 .
