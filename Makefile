SHELL := bash
WORKFLOW_FOLDER := $(CURDIR)/workflows/
PYTHON_VENV_DIR := venv/dev

all: setup validate test
setup: create_env requirements test_requirements
validate: lint_dryrun


## Common targets
create_env:
	@echo "Creating venv environment in ${PYTHON_VENV_DIR}"
	python3 -m venv ${PYTHON_VENV_DIR}

requirements:
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python3 -m pip install -r requirements.txt

## Engine Development
test_requirements:
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python3 -m pip install -r test_requirements.txt

test:
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python3 -m pytest -v --cov=daggr tests/

tdd:
	ptw --runner "python -m pytest --cov=daggr tests/"

mypy:
	python3 -m mypy . \
		--disable-error-code import

lint_dryrun: 
	@echo "> LINTING..."

	@echo ""
	@echo ">> Step: isort"
	python3 -m isort --skip venv --check ./ 

	@echo ""
	@echo ">> Step: autoflake"
	python3 -m autoflake -r --exclude venv --remove-all-unused-imports --check ./

	@echo ""
	@echo ">> Step: black"
	python3 -m black --exclude venv --check ./ 

lint: 
	@echo "> LINTING..."

	@echo ""
	@echo ">> Step: isort"
	python3 -m isort --skip venv ./ 

	@echo ""
	@echo ">> Step: autoflake"
	python3 -m autoflake -r --in-place --exclude venv --remove-all-unused-imports ./
	
	@echo ""
	@echo ">> Step: black"
	python3 -m black --exclude venv ./