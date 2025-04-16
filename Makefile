.PHONY: venv run tests clean

# Virtual environment name
VENV = dev
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
PWD = $(shell pwd)

# Create virtual environment only if it doesn't exist
venv: $(VENV)/bin/activate
$(VENV)/bin/activate: requirements.txt
	@echo "Setting up virtual environment..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@touch $(VENV)/bin/activate
	@echo "Virtual environment created."

# Run the server, ensuring venv exists
run: venv
	@echo "Starting the server..."
	PYTHONPATH=$(PWD)/src $(PYTHON) -m main

# Run tests, ensuring venv exists
tests: venv
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/

# Clean up virtual environment and cache files
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__
	rm -rf $(VENV)
	@echo "Cleanup complete."

