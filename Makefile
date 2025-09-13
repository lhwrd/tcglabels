# Makefile for Pokemon TCG Labels Reflex App

APP_NAME=tcglabels
IMAGE_NAME=$(APP_NAME):latest


.PHONY: help install run dev clean docker-build docker-run docker-push version

help:
	@echo "Makefile commands:"
	@echo "  install       Install Python dependencies"
	@echo "  run           Run the Reflex app locally"
	@echo "  dev           Run the Reflex app in dev mode (with reload)"
	@echo "  clean         Remove Python cache and build artifacts"
	@echo "  docker-build  Build the Docker image"
	@echo "  docker-run    Run the app in Docker"
	@echo "  docker-push   Push the Docker image (set DOCKER_REPO env var)"
	@echo "  version       Show the current app version (from git tag or VERSION file)"
version:
	@if git describe --tags --abbrev=0 > /dev/null 2>&1; then \
	  git describe --tags --always; \
	elif [ -f VERSION ]; then \
	  cat VERSION; \
	else \
	  echo "unknown"; \
	fi


install:
	uv pip install -r requirements.txt


run:
	uv run reflex run


dev:
	uv run reflex run --dev

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .web .reflex

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run -it --rm -p 3000:3000 $(IMAGE_NAME)

docker-push:
ifndef DOCKER_REPO
	$(error DOCKER_REPO is not set)
endif
	VERSION=$$(if git describe --tags --abbrev=0 2>/dev/null; then git describe --tags --always; elif [ -f VERSION ]; then cat VERSION; else echo "unknown"; fi); \
	docker tag $(IMAGE_NAME) $(DOCKER_REPO)/$(APP_NAME):latest; \
	docker tag $(IMAGE_NAME) $(DOCKER_REPO)/$(APP_NAME):$$VERSION; \
	docker push $(DOCKER_REPO)/$(APP_NAME):latest; \
	docker push $(DOCKER_REPO)/$(APP_NAME):$$VERSION
