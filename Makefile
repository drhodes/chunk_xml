SHELL = bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# -----------------------------------------------------------------------------
# Section: Python

VENV = source venv/bin/activate &&
PY = ${VENV} python



PYREQS = requirements.txt dev-requirements.txt
venv: ${BUILD_REQS} ${PYREQS} ## virtual environment for python
	python3 -m venv venv && \
	${VENV} pip install -r requirements.txt
	${VENV} pip install -r dev-requirements.txt
	touch venv

test: venv
	${VENV} pip install -e .
	${VENV} pytest
