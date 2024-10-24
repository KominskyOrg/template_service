# Makefile

# ==============================================================================
# Variables
# ==============================================================================

# General
REPO_NAME ?= stack_service

# Docker
DOCKER_COMPOSE = docker-compose -f ../devops_admin/docker-compose.yml
IMAGE_TAG ?= $(shell git rev-parse --short HEAD)

# Python
PIPENV = pipenv run
PYTEST = $(PIPENV) pytest
RUFF = $(PIPENV) ruff
BLACK = $(PIPENV) black

# Terraform
ENV ?= staging
BACKEND_DIR ?= ./tf
AWS_REGION ?= us-east-1
AWS_ACCOUNT_ID ?= $(AWS_ACCOUNT_ID)
ECR_REPO := $(REPO_NAME)_$(ENV)

# ==============================================================================
# Phony Targets
# ==============================================================================
.PHONY: help up down build logs lint lint-fix format format-fix test test-cov install clean init plan apply push ecr-login

# ==============================================================================
# Default Target
# ==============================================================================

help:
	@echo "Usage:"
	@echo "  make build          Build the Docker image"
	@echo "  make up             Start the Docker containers"
	@echo "  make down           Stop the Docker containers"
	@echo "  make logs           Show logs from the Docker containers"
	@echo "  make lint           Run ruff for linting"
	@echo "  make lint-fix       Fix linting issues using ruff"
	@echo "  make format         Check code formatting with black"
	@echo "  make format-fix     Format code using black"
	@echo "  make test           Run tests"
	@echo "  make test-cov       Run tests with coverage"
	@echo "  make install        Install dependencies"
	@echo "  make clean          Clean up Docker containers and images"
	@echo "  make init           Initialize Terraform"
	@echo "  make plan           Generate Terraform plan"
	@echo "  make apply          Apply Terraform configuration"
	@echo "  make push           Push Docker image to ECR"
	@echo "  make ecr-login      Authenticate Docker to Amazon ECR"

# ==============================================================================
# Docker Targets
# ==============================================================================

up:
	$(DOCKER_COMPOSE) up --build

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

build:
	@echo "Building Docker image $(ECR_REPO):$(IMAGE_TAG)..."
	docker build -t $(ECR_REPO):$(IMAGE_TAG) -f Dockerfile.$(ENV) .

clean:
	$(DOCKER_COMPOSE) down --rmi all --volumes --remove-orphans

# ==============================================================================
# Linting and Formatting
# ==============================================================================

lint:
	$(RUFF) check .

lint-fix:
	$(RUFF) check . --fix

format:
	@echo "Checking code formatting with black..."
	$(BLACK) --check .

format-fix:
	@echo "Formatting code with black..."
	$(BLACK) .

# ==============================================================================
# Testing
# ==============================================================================

test:
	$(PYTEST)

test-cov:
	$(PYTEST) --cov-report=xml

# ==============================================================================
# Dependency Management
# ==============================================================================

install:
	pipenv install

# ==============================================================================
# Terraform Targets
# ==============================================================================

init:
	@echo "Initializing Terraform for $(ENV) environment..."
	cd $(BACKEND_DIR) && terraform init -var env=$(ENV) -backend-config=backend-$(ENV).tfbackend

plan:
	@echo "Generating Terraform plan for $(ENV) environment..."
	cd $(BACKEND_DIR) && terraform plan -out=tfplan -var env=$(ENV) -var image_tag=$(IMAGE_TAG)

apply:
	@echo "Applying Terraform configuration for $(ENV) environment..."
	cd $(BACKEND_DIR) && terraform apply tfplan

# ==============================================================================
# AWS ECR Targets
# ==============================================================================

ecr-login:
	@echo "Logging into Amazon ECR..."
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

push: ecr-login build
	@echo "Tagging Docker image..."
	docker tag $(ECR_REPO):$(IMAGE_TAG) $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPO):$(IMAGE_TAG)
	@echo "Pushing Docker image to ECR..."
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPO):$(IMAGE_TAG)
