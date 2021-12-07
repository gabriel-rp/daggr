SHELL := bash
WORKFLOW_FOLDER := $(CURDIR)/workflows/
PYTHON_VENV_DIR := venv/dev

all: setup validate test
setup: create_env requirements test_requirements
validate: validate_schema lint_dryrun


## Common targets
create_env:
	@echo "Creating venv environment in ${PYTHON_VENV_DIR}"
	python3 -m venv ${PYTHON_VENV_DIR}

requirements:
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python3 -m pip install -r requirements.txt


## Engine Usage
validate_schema: 
	@echo "Validating workflow schemas in ${WORKFLOW_FOLDER}"
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python3 validation/validate_schema.py ${WORKFLOW_FOLDER}


## Engine Development
test_requirements:
	source ${PYTHON_VENV_DIR}/bin/activate && \
		python3 -m pip install -r test_requirements.txt

test:
	source ${PYTHON_VENV_DIR}/bin/activate && \
		pytest -v

lint_dryrun: 
	@echo "> LINTING..."

	@echo ""
	@echo ">> Step: isort"
	isort --skip venv --check ./ 

	@echo ""
	@echo ">> Step: autoflake"
	autoflake -r --exclude venv --remove-all-unused-imports --check ./

	@echo ""
	@echo ">> Step: black"
	black --exclude venv --check ./ 

lint: 
	@echo "> LINTING..."

	@echo ""
	@echo ">> Step: isort"
	isort --skip venv ./ 

	@echo ""
	@echo ">> Step: autoflake"
	autoflake -r --exclude venv --remove-all-unused-imports ./
	
	@echo ""
	@echo ">> Step: black"
	black --exclude venv ./