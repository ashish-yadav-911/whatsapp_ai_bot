# Define variables
PYTHON = python3
PIP = pip3

# Default target when running `make`
all: install run

# Install dependencies from requirements.txt
install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt

# Run the Python application
run:
	@echo "Running the application..."
	$(PYTHON) run.py

# Clean command to remove unnecessary files (optional)
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +


