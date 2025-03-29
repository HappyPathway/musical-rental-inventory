.PHONY: venv install migrate run shell test clean superuser static collectstatic lint help kill

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
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type d -name ".eggs" -exec rm -rf {} +
	find . -type d -name "*.dist-info" -exec rm -rf {} +
	find . -type d -name "*output*" -exec rm -rf {} +

superuser:
	$(VENV_BIN)/$(MANAGE) createsuperuser

static:
	$(VENV_BIN)/$(MANAGE) collectstatic

lint:
	$(VENV_BIN)/flake8