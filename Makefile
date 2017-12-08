all:
	@echo "Tetrad, a method of selecting CAR-T targets"
	@echo "\t\`make dev-install\` to install development version"
	@echo "\t\`make test\` to validate against known data sets."
	@echo "\t\`make package\` to package for distribution"

dev-install:
	@pipenv install --dev
	@pipenv run pip install -e . 
	@echo "installed development version"

test:
	@pipenv run pytest

typecheck:
	@pipenv run mypy tetrad --ignore-missing-imports
