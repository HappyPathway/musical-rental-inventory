.PHONY: venv install migrate run shell test clean superuser static collectstatic lint help kill reset test-selenium test-selenium-inventory test-selenium-rentals test-selenium-users test-selenium-payments

PYTHON = python3
PIP = pip3
MANAGE = python manage.py
VENV_NAME = venv
VENV_ACTIVATE = . $(VENV_NAME)/bin/activate
VENV_BIN = $(VENV_NAME)/bin

kill:
	@echo "Killing all Django server processes..."
	@ps auxw | grep runserver | grep -v grep | awk '{ print $$2 }' | xargs kill -9 2>/dev/null || echo "No Django server processes found."

help:
	@echo "Available commands:"
	@echo "  make venv          - Create a virtual environment"
	@echo "  make install       - Install dependencies"
	@echo "  make migrate       - Apply migrations"
	@echo "  make run           - Run development server"
	@echo "  make shell         - Open Django shell"
	@echo "  make test          - Run tests"
	@echo "  make superuser     - Create a superuser"
	@echo "  make static        - Collect static files"
	@echo "  make lint          - Run linting"
	@echo "  make clean         - Remove Python artifacts"
	@echo "  make startapp      - Create a new Django app (usage: make startapp app=myapp)"
	@echo "  make makemigrations - Create new migrations (usage: make makemigrations app=myapp)"
	@echo "  make kill          - Kill all running Django server processes"
	@echo "  make reset         - Kill server, collect static files, and restart server"
	@echo "  make test-selenium - Run all Selenium tests headlessly"
	@echo "  make test-selenium-inventory - Run inventory Selenium tests"
	@echo "  make test-selenium-rentals   - Run rentals Selenium tests"
	@echo "  make test-selenium-users     - Run users Selenium tests"
	@echo "  make test-selenium-payments  - Run payments Selenium tests"
	@echo "  make test-selenium-visual    - Run Selenium tests with visible browser"

venv:
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "Virtual environment created. Activate it with:"
	@echo "  source $(VENV_NAME)/bin/activate"

install: venv
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements.txt

startproject:
	$(VENV_BIN)/django-admin startproject music_rental .

migrate:
	$(VENV_BIN)/$(MANAGE) migrate

makemigrations:
ifdef app
	$(VENV_BIN)/$(MANAGE) makemigrations $(app)
else
	$(VENV_BIN)/$(MANAGE) makemigrations
endif

startapp:
ifndef app
	@echo "Usage: make startapp app=myapp"
else
	$(VENV_BIN)/$(MANAGE) startapp $(app)
endif

run:
	$(VENV_BIN)/$(MANAGE) runserver 0.0.0.0:8000

shell:
	$(VENV_BIN)/$(MANAGE) shell

test:
ifdef app
	$(VENV_BIN)/$(MANAGE) test $(app)
else
	$(VENV_BIN)/$(MANAGE) test
endif

clean:
	@echo "Cleaning up temporary and unnecessary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "*.egg" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".DS_Store" -delete
	@find . -type f -name "*.bak" -delete
	@find . -type f -name "*.swp" -delete
	@find . -type f -name "*.orig" -delete
	@find . -type d -name ".cache" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".coverage" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@rm -rf .coverage coverage.xml coverage_html_report/
	@echo "Clean completed!"

superuser:
	$(VENV_BIN)/$(MANAGE) createsuperuser

static:
	$(VENV_BIN)/$(MANAGE) collectstatic

lint:
	$(VENV_BIN)/flake8

reset: kill static run
	@echo "Reset complete: server restarted with updated static files."

# Selenium Test Targets
test-selenium:
	$(VENV_ACTIVATE) && ./run_selenium_tests.py --headless

test-selenium-inventory:
	$(VENV_ACTIVATE) && ./run_selenium_tests.py --headless tests.functional.test_inventory

test-selenium-rentals:
	$(VENV_ACTIVATE) && ./run_selenium_tests.py --headless tests.functional.test_rentals

test-selenium-users:
	$(VENV_ACTIVATE) && ./run_selenium_tests.py --headless tests.functional.test_users

test-selenium-payments:
	$(VENV_ACTIVATE) && ./run_selenium_tests.py --headless tests.functional.test_payments

# Visual browser tests (non-headless)
test-selenium-visual:
	$(VENV_ACTIVATE) && ./run_selenium_tests.py