APP_NAME = h2l_agent_caller

.PHONY: clean help

help:
	clear;
	@echo "================= Usage =================";
	@echo "build                        : Rebuild app container.";
	@echo "run                          : Run service standalone.";
	@echo "stop                         : Stop and keep all containers.";
	@echo "clean-pyc                    : Remove python artifacts.";
	@echo "clean-build                  : Remove build artifacts.";
	@echo "clean                        : Complex cleaning. Clean the folder from build/test related folders and orphans.";
	@echo "ruff_check                   : Run lint check using ruff.";
	@echo "ruff_fix                     : Run lint errors fixing using ruff (pls, use with caution)";
	@echo "ruff_format                  : Run code formatting using ruff (pls, use with caution).";

### APP LOCAL BUILDING AND RUNNING
## Rebuild app container.
build:
	@docker network create localai || true
	@docker compose build $(APP_NAME)

## Run service standalone.
run: build
	rm -f celerybeat.pid
	@docker compose up


### CLEANING AND STOPPING
## Stop and keep all containers.
stop:
	@docker compose stop $(docker ps -aq)

## Remove python artifacts.
clean-pyc:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +

## Remove build artifacts.
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

## Complex cleaning. Clean the folder from build/test related folders and orphans.
clean: clean-build clean-pyc
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -f .coverage
	@docker compose down --remove-orphans


### LINTERS, OTHER CHECKS AND AUTO FORMATTING
## Run lint check using ruff.
ruff_check:
	@echo "\033[0;32mLINT CHECK WITH RUFF COMMENCED\033[0m"
	@ruff check || true
	@echo "\033[0;31mLINT CHECK WITH RUFF COMPLETED\033[0m"

## Run lint errors fixing using ruff (pls, use with caution)
ruff_fix:
	@echo "\033[0;32mFIXING WITH RUFF COMMENCED\033[0m"
	@ruff check --fix || true
	@echo "\033[0;31mFIXING WITH RUFF COMPLETED\033[0m"

## Run code formatting using ruff (pls, use with caution)
ruff_format:
	@echo "\033[0;32mFORMATTING WITH RUFF COMMENCED\033[0m"
	@ruff format . --check || true
	@ruff format || true
	@echo "\033[0;31mFORMATTING WITH RUFF COMPLETED. PLS USE make diff TO CHECK CHANGES\033[0m"

## Check all changes in current commit (prefer to use after any authomatic fixes and formatting)
diff:
	@git diff
