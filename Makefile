SHELL := bash
WORKFLOW_FOLDER := $(CURDIR)/workflows/
PYTHON_VENV_DIR := venv/dev

all: setup validate test
setup: create_env requirements test_requirements
validate: lint_dryrun
 
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# Common targets
create_env: ## Creates Python virtual environment for development
	@echo "Creating venv environment in ${PYTHON_VENV_DIR}"
	python -m venv ${PYTHON_VENV_DIR}

requirements: ## Install DAGGR requirements
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m pip install -r requirements.txt

# Engine Development
test_requirements: ## Installs test requirements
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m pip install -r test_requirements.txt

test: ## Runs tests
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m pytest -v --cov=daggr tests/

cov_report: ## Generates code coverage report in XML and HTML
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m pytest --cov-report html --cov-report xml:coverage.xml --cov=daggr tests/

tdd: ## Runs Test Driven Development (TDD) plugin for pytest
	source ${PYTHON_VENV_DIR}/bin/activate && \
		ptw --runner "python -m pytest --cov=daggr tests/"

mypy: ## Static type checking
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m mypy . \
		--disable-error-code import

lint_dryrun: ## Checks if source code is linted and displays
	@echo "> LINTING..."

	@echo ""
	@echo ">> Step: isort"
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m isort --skip venv --check ./ 

	@echo ""
	@echo ">> Step: autoflake"
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m autoflake -r --exclude venv --remove-all-unused-imports --check ./

	@echo ""
	@echo ">> Step: black"
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m black --exclude venv --check ./ 

lint: ## Lint source code
	@echo "> LINTING..."

	@echo ""
	@echo ">> Step: isort"
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m isort --skip venv ./ 

	@echo ""
	@echo ">> Step: autoflake"
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m autoflake -r --in-place --exclude venv --remove-all-unused-imports ./
	
	@echo ""
	@echo ">> Step: black"
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python -m black --exclude venv ./