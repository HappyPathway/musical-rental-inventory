.PHONY: venv install migrate run shell test clean superuser static collectstatic lint help kill reset test-selenium test-selenium-inventory test-selenium-rentals test-selenium-users test-selenium-payments infra import-fixtures docker-build docker-run docker-push gcp-auth deploy-cloud-run taint-sa-key fetch-pa-speakers load-pa-fixtures setup-pa-inventory test test-unit test-integration test-e2e test-e2e-visual test-e2e-inventory test-e2e-rentals test-e2e-users test-e2e-payments infra-apply

# Include environment variables if .env exists
-include .env

PYTHON = python3
PIP = pip3
MANAGE = python manage.py
VENV_NAME = venv
VENV_ACTIVATE = . $(VENV_NAME)/bin/activate
VENV_BIN = $(VENV_NAME)/bin

# GCP and Docker variables with defaults (override in .env)
GCP_PROJECT_ID ?= happypathway-1522441039906
GCP_REGION ?= us-central1
CONTAINER_REGISTRY ?= $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/roknsound-images
IMAGE_NAME ?= roknsound-rental-inventory
IMAGE_TAG ?= latest
FULL_IMAGE_NAME = $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

kill:
	@echo "Killing all Django server processes..."
	@ps auxw | grep runserver | grep -v grep | awk '{ print $$2 }' | xargs kill -9 2>/dev/null || echo "No Django server processes found."

help:
	@echo "========== ROKNSOUND MUSICAL RENTAL INVENTORY SYSTEM =========="
	@echo "Available commands:"
	@echo ""
	@echo "Development commands:"
	@echo "  make venv          - Create a virtual environment"
	@echo "  make install       - Install dependencies"
	@echo "  make migrate       - Apply migrations"
	@echo "  make makemigrations - Create new migrations (usage: make makemigrations app=myapp)"
	@echo "  make run           - Run development server"
	@echo "  make shell         - Open Django shell"
	@echo "  make superuser     - Create a superuser"
	@echo "  make static        - Collect static files"
	@echo "  make kill          - Kill all running Django server processes"
	@echo "  make reset         - Kill server, collect static files, and restart server"
	@echo "  make startapp      - Create a new Django app (usage: make startapp app=myapp)"
	@echo ""
	@echo "Testing commands:"
	@echo "  make test          - Run all Django tests (usage: make test app=myapp)"
	@echo "  make lint          - Run linting with flake8"
	@echo "  make clean         - Remove Python artifacts and cache files"
	@echo "  make test-selenium - Run all Selenium tests headlessly"
	@echo "  make test-selenium-inventory - Run inventory Selenium tests"
	@echo "  make test-selenium-rentals   - Run rentals Selenium tests"
	@echo "  make test-selenium-users     - Run users Selenium tests"
	@echo "  make test-selenium-payments  - Run payments Selenium tests"
	@echo "  make test-user-management-flow - Run user management flow tests"
	@echo "  make test-mobile   - Run mobile inventory tests"
	@echo "  make test-selenium-visual    - Run Selenium tests with visible browser"
	@echo ""
	@echo "Data management:"
	@echo "  make import-fixtures - Load fixture data (usage: make import-fixtures app=myapp)"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-build  - Build the Docker image"
	@echo "  make docker-run    - Run the Docker container locally"
	@echo "  make docker-stop   - Stop and remove the running Docker container"
	@echo "  make docker-tag    - Tag Docker image for GCP Artifact Registry"
	@echo "  make docker-push   - Push Docker image to GCP Artifact Registry"
	@echo ""
	@echo "GCP deployment commands:"
	@echo "  make gcp-auth      - Authenticate with Google Cloud"
	@echo "  make deploy-cloud-run - Deploy to Cloud Run"
	@echo "  make deploy-all    - Build, push, and deploy to Cloud Run"
	@echo ""
	@echo "Infrastructure commands:"
	@echo "  make infra         - Apply Terraform infrastructure changes"
	@echo "  make taint-sa-key  - Taint the service account key for rotation"
	@echo "  make backend-state-init - Initialize Terraform backend state"
	@echo "  make backend-state-apply - Apply Terraform backend state configuration"
	@echo "  make infra-init    - Initialize main infrastructure Terraform"
	@echo "  make setup-backend - Set up Terraform backend in GCS"
	@echo ""
	@echo "Note: Always use 'make reset' after making CSS or JavaScript changes"
	@echo "      to rebuild static files and restart the server."
	@echo "================================================================"

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

test: test-unit test-integration
	@echo "All tests complete (excluding E2E tests)"

test-quiet:
	@echo "Running tests (quiet mode)..."
	@$(VENV_ACTIVATE) && python -m pytest -q tests/

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
	@rm test-screenshots/*.png
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

test-user-management-flow:
	$(VENV_ACTIVATE) && ./run_selenium_tests.py --headless tests.functional.test_users.UserManagementFlowTestCase

# Mobile-specific test target
test-mobile:
	$(VENV_ACTIVATE) && ./run_mobile_inventory_tests.py

# Visual browser tests (non-headless)
test-selenium-visual:
	$(VENV_ACTIVATE) && ./run_selenium_tests.py

# Terraform Infrastructure Target
infra:
	@echo "Applying Terraform infrastructure changes..."
	cd infra && \
	terraform init && \
	terraform validate && \
	terraform plan && \
	terraform apply -auto-approve
	@echo "Terraform apply complete."

# Import fixtures
import-fixtures:
ifdef app
	$(VENV_BIN)/$(MANAGE) loaddata $(app)
else
	@echo "Loading fixtures for all apps..."
	$(VENV_BIN)/$(MANAGE) loaddata inventory/fixtures/*.json
	$(VENV_BIN)/$(MANAGE) loaddata users/fixtures/*.json
	$(VENV_BIN)/$(MANAGE) loaddata rentals/fixtures/*.json
	$(VENV_BIN)/$(MANAGE) loaddata payments/fixtures/*.json
endif

# Docker Targets
docker-build:
	@echo "Building Docker image for ROKNSOUND rental inventory..."
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "Docker image built successfully."

docker-run:
	@echo "Attempting to stop and remove existing container using port 8080..."
	@CONTAINER_ID=$$(docker ps -q --filter "publish=8080"); \
	if [ -n "$$CONTAINER_ID" ]; then \
		echo "Stopping container $$CONTAINER_ID..."; \
		docker stop $$CONTAINER_ID; \
		echo "Removing container $$CONTAINER_ID..."; \
		docker rm $$CONTAINER_ID; \
	else \
		echo "No running container found using port 8080."; \
	fi
	@echo "Killing any remaining process on port 8080..."
	@PID=$$(lsof -ti tcp:8080); \
	if [ -n "$$PID" ]; then \
		echo "Killing process $$PID on port 8080..."; \
		kill -9 $$PID 2>/dev/null || true; \
		sleep 1; \
	else \
		echo "No process found on port 8080."; \
	fi
	@echo "Running Docker container locally with GCP service account..."
	docker run -p 8080:8080 \
		-e DEBUG=1 \
		-e SECRET_KEY=localtesting \
		-e GS_BUCKET_NAME=roknsound-music-rental-inventory \
		-e GS_PROJECT_ID=happypathway-1522441039906 \
		-v $$(pwd)/gcp-service-account-key.json:/app/gcp-service-account-key.json \
		-e GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-service-account-key.json \
		$(IMAGE_NAME):$(IMAGE_TAG)

docker-stop:
	@echo "Attempting to stop and remove existing container using port 8080..."
	@CONTAINER_ID=$$(docker ps -q --filter "publish=8080"); \
	if [ -n "$$CONTAINER_ID" ]; then \
		echo "Stopping container $$CONTAINER_ID..."; \
		docker stop $$CONTAINER_ID; \
		echo "Removing container $$CONTAINER_ID..."; \
		docker rm $$CONTAINER_ID; \
	else \
		echo "No running container found using port 8080."; \
	fi
	
# GCP Auth and Deployment Targets
gcp-auth:
	@echo "Authenticating with Google Cloud..."
	gcloud auth login
	gcloud config set project $(GCP_PROJECT_ID)
	gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev

docker-tag:
	@echo "Tagging Docker image for GCP Artifact Registry..."
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(FULL_IMAGE_NAME)

create-ar-repo:
	@echo "Creating Google Artifact Registry repository if it doesn't exist..."
	gcloud artifacts repositories describe roknsound-images \
		--project=$(GCP_PROJECT_ID) \
		--location=$(GCP_REGION) \
		|| gcloud artifacts repositories create roknsound-images \
		--project=$(GCP_PROJECT_ID) \
		--location=$(GCP_REGION) \
		--repository-format=docker \
		--description="Docker repository for ROKNSOUND images"
	@echo "Repository roknsound-images is ready."

docker-push: create-ar-repo docker-tag
	@echo "Pushing Docker image to GCP Artifact Registry..."
	@echo "Authenticating with Google Container Registry..."
	gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev --quiet
	docker push $(FULL_IMAGE_NAME)

# Django database migration targets
django-migrate-prod:
	@echo "Running migrations on production database..."
	@echo "Building temporary migration image..."
	docker build -t $(IMAGE_NAME):migrate --build-arg="MIGRATIONS_ONLY=1" .
	@echo "Running migrations against production database..."
	gcloud run jobs create roknsound-migrations \
		--image=$(CONTAINER_REGISTRY)/$(IMAGE_NAME):migrate \
		--region=$(GCP_REGION) \
		--service-account=roknsound-storage-sa@$(GCP_PROJECT_ID).iam.gserviceaccount.com \
		--set-env-vars="DJANGO_SECRET_KEY=$(shell terraform output -state=infra/terraform.tfstate -raw django_secret_key 2>/dev/null || echo 'dummy-key'),DATABASE_URL=$(shell terraform output -state=infra/terraform.tfstate -raw database_url 2>/dev/null || echo 'dummy-url'),GS_BUCKET_NAME=$(GS_BUCKET_NAME),DEBUG=0,MIGRATE_ONLY=1" \
		--task-timeout=10m \
		--max-retries=2 \
		--execute-now \
		|| echo "Migration job already exists"
	gcloud run jobs execute roknsound-migrations --region=$(GCP_REGION)

# Update deploy-cloud-run to include migrations
deploy-cloud-run: docker-push django-migrate-prod
	@echo "Deploying to Cloud Run..."
	gcloud run deploy roknsound-rental-inventory \
		--image=$(FULL_IMAGE_NAME) \
		--region=$(GCP_REGION) \
		--platform=managed \
		--allow-unauthenticated \
		--service-account=roknsound-storage-sa@$(GCP_PROJECT_ID).iam.gserviceaccount.com \
		--set-env-vars=GS_BUCKET_NAME=$(GS_BUCKET_NAME),DEBUG=0

# Deploy everything (build, push, and deploy to Cloud Run)
deploy-all: docker-build docker-push deploy-cloud-run
	@echo "Full deployment completed successfully!"

# Terraform Backend State Management Targets
.PHONY: backend-state-init backend-state-apply infra-init setup-backend

backend-state-init:
	@echo "Initializing Terraform for backend state management..."
	cd backend-state && terraform init

backend-state-apply:
	@echo "Applying Terraform configuration to create the state bucket..."
	cd backend-state && terraform apply -auto-approve
	@echo "Terraform state bucket setup complete."

infra-init:
	@echo "Initializing main infrastructure Terraform with GCS backend..."
	@echo "Ensure the bucket name in infra/backend.tf matches the one created."
	cd infra && terraform init -migrate-state
	@echo "Main infrastructure backend initialized."


infra-apply:
	@echo "Applying main infrastructure Terraform configuration..."
	cd infra && terraform apply -auto-approve
	@echo "Main infrastructure applied successfully."
	
setup-backend: backend-state-init backend-state-apply infra-init
	@echo "Terraform backend setup complete. State is now managed in GCS."

# Taint the service account key to force its recreation
taint-sa-key:
	@echo "Tainting Google service account key..."
	cd infra && terraform init && terraform taint google_service_account_key.app_service_account_key
	@echo "Service account key tainted. Run 'make infra' to apply changes and generate a new key."

fetch-pa-speakers:
	@echo "Fetching PA speaker data from Sweetwater..."
	@python scripts/fetch_pa_speakers.py

load-pa-fixtures:
	@echo "Loading PA speaker fixtures..."
	@python manage.py loaddata inventory/fixtures/pa_speakers.json

setup-pa-inventory: fetch-pa-speakers load-pa-fixtures
	@echo "PA speaker inventory setup complete!"

# Test targets
.PHONY: test test-unit test-integration test-e2e test-all

test-unit:
	@echo "Running unit tests..."
	@/bin/bash -c 'source venv/bin/activate && python -m pytest tests/unit/'

test-integration:
	@echo "Running integration tests..."
	@. $(VENV_ACTIVATE) && PYTHONPATH=. pytest -q tests/integration/

test-e2e:
	@echo "Running end-to-end tests..."
	@. $(VENV_ACTIVATE) && PYTHONPATH=. pytest tests/e2e/ --tb=short

test-e2e-visual:
	@echo "Running end-to-end tests with browser visible..."
	@. $(VENV_ACTIVATE) && PYTHONPATH=. pytest tests/e2e/ --no-headless

test-e2e-inventory:
	@echo "Running inventory E2E tests..."
	@. $(VENV_ACTIVATE) && PYTHONPATH=. pytest tests/e2e/test_inventory.py

test-e2e-rentals:
	@echo "Running rentals E2E tests..."
	@. $(VENV_ACTIVATE) && PYTHONPATH=. pytest tests/e2e/test_rentals.py

test-e2e-users:
	@echo "Running user management E2E tests..."
	@. $(VENV_ACTIVATE) && PYTHONPATH=. pytest tests/e2e/test_users.py

test-e2e-payments:
	@echo "Running payment system E2E tests..."
	@. $(VENV_ACTIVATE) && PYTHONPATH=. pytest tests/e2e/test_payments.py

test-all: test-unit test-integration test-e2e
	@echo "All tests complete (including E2E tests)"

# Consolidated Cloud Build target with proper permissions
cloud-build:
	@echo "Setting up permissions and triggering Cloud Build..."
	source venv/bin/activate && gcloud config set project $(GCP_PROJECT_ID)
	source venv/bin/activate && gcloud services enable cloudbuild.googleapis.com
	source venv/bin/activate && gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) \
		--member=user:dave@roknsound.com \
		--role=roles/cloudbuild.builds.editor
	source venv/bin/activate && gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) \
		--member=serviceAccount:$(shell source venv/bin/activate && gcloud projects describe $(GCP_PROJECT_ID) --format="value(projectNumber)")@cloudbuild.gserviceaccount.com \
		--role=roles/cloudbuild.builds.builder
	source venv/bin/activate && gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) \
		--member=serviceAccount:$(shell source venv/bin/activate && gcloud projects describe $(GCP_PROJECT_ID) --format="value(projectNumber)")@cloudbuild.gserviceaccount.com \
		--role=roles/run.admin
	source venv/bin/activate && gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) \
		--member=serviceAccount:$(shell source venv/bin/activate && gcloud projects describe $(GCP_PROJECT_ID) --format="value(projectNumber)")@cloudbuild.gserviceaccount.com \
		--role=roles/iam.serviceAccountUser
	source venv/bin/activate && gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) \
		--member=serviceAccount:$(shell source venv/bin/activate && gcloud projects describe $(GCP_PROJECT_ID) --format="value(projectNumber)")@cloudbuild.gserviceaccount.com \
		--role=roles/artifactregistry.admin
	source venv/bin/activate && cd $(PWD) && gcloud builds submit --config=cloudbuild.yaml
	@echo "Cloud Build triggered. Check the GCP console for build progress."


# Fix Cloud Build permissions with service account setup
fix-cloudbuild:
	@echo "Setting up Cloud Build permissions..."
	source venv/bin/activate && gcloud services enable cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com iam.googleapis.com storage.googleapis.com serviceusage.googleapis.com
	@echo "Getting project number and setting up variables..."
	source venv/bin/activate && \
		PROJ_NUM=$$(gcloud projects describe $(GCP_PROJECT_ID) --format="value(projectNumber)") && \
		echo "Granting permissions to user and Cloud Build service account..." && \
		gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) --member=user:dave@roknsound.com --role=roles/cloudbuild.builds.editor && \
		gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) --member=user:dave@roknsound.com --role=roles/storage.admin && \
		gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) --member=user:dave@roknsound.com --role=roles/iam.serviceAccountTokenCreator && \
		gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) --member=serviceAccount:$$PROJ_NUM@cloudbuild.gserviceaccount.com --role=roles/cloudbuild.builds.builder && \
		gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) --member=serviceAccount:$$PROJ_NUM@cloudbuild.gserviceaccount.com --role=roles/run.admin && \
		gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) --member=serviceAccount:$$PROJ_NUM@cloudbuild.gserviceaccount.com --role=roles/iam.serviceAccountUser && \
		gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) --member=serviceAccount:$$PROJ_NUM@cloudbuild.gserviceaccount.com --role=roles/artifactregistry.admin && \
		gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) --member=serviceAccount:$$PROJ_NUM@cloudbuild.gserviceaccount.com --role=roles/storage.admin
	@echo "Making sure Cloud Build bucket exists and has correct permissions..."
	source venv/bin/activate && \
		gsutil mb -p $(GCP_PROJECT_ID) -l us-central1 gs://$(GCP_PROJECT_ID)_cloudbuild || echo "Bucket already exists" && \
		gsutil iam ch user:dave@roknsound.com:objectAdmin gs://$(GCP_PROJECT_ID)_cloudbuild
	@echo "Cloud Build permissions fixed. Now run 'make run-cloudbuild' to build and deploy."

# Simple Cloud Build trigger using impersonation
run-cloudbuild:
	@echo "Ensuring correct project: $(GCP_PROJECT_ID)"
	source venv/bin/activate && gcloud config set project $(GCP_PROJECT_ID)
	@echo "Refreshing application-default credentials..."
	source venv/bin/activate && gcloud auth application-default login
	@echo "Triggering Cloud Build for project $(GCP_PROJECT_ID)..."
	source venv/bin/activate && \
		PROJ_NUM=$$(gcloud projects describe $(GCP_PROJECT_ID) --format="value(projectNumber)") && \
		gcloud builds submit --config=cloudbuild.yaml --impersonate-service-account=$$PROJ_NUM@cloudbuild.gserviceaccount.com
	@echo "Cloud Build submitted."
