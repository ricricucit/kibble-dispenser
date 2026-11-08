# Feedr Outdoor — ESP32 Cat Dispenser
# Requires: Python 3, pip, ESP32 connected via USB
#
# mpremote commands are chained with '+' to keep a single serial session open.
# This prevents the board's main.py from restarting between file transfers.

SRC_DIR = src
SRC_FILES = $(wildcard $(SRC_DIR)/*.py)

# Build the mpremote cp chain: "cp src/a.py :a.py + cp src/b.py :b.py + ..."
CP_CHAIN = $(foreach f,$(SRC_FILES),cp $(f) :$(notdir $(f)) +)

# ── Setup ──────────────────────────────────────────────

.PHONY: setup
setup: ## Install development tools (mpremote, ruff)
	pip install -r requirements.txt

# ── Code quality ───────────────────────────────────────

.PHONY: lint
lint: ## Lint source files with ruff
	ruff check $(SRC_DIR)

.PHONY: format
format: ## Auto-format source files with ruff
	ruff format $(SRC_DIR)

.PHONY: check
check: lint ## Run all checks (alias for lint)

# ── Deploy ─────────────────────────────────────────────

.PHONY: deploy
deploy: ## Upload all src/ files to the board
	mpremote $(CP_CHAIN) reset

.PHONY: deploy-main
deploy-main: ## Upload only main.py and reset
	mpremote cp $(SRC_DIR)/main.py :main.py + reset

.PHONY: reset
reset: ## Soft-reset the board
	mpremote reset

# ── REPL & Debugging ──────────────────────────────────

.PHONY: repl
repl: ## Open interactive MicroPython REPL on the board
	mpremote repl

.PHONY: run
run: ## Run main.py on the board without saving it
	mpremote run $(SRC_DIR)/main.py

# ── Board filesystem ──────────────────────────────────

.PHONY: ls
ls: ## List files on the board
	mpremote ls

BACKUP_DIR = backups/$(shell date +%Y%m%d-%H%M%S)

.PHONY: backup
backup: ## Download all .py files from the board to backups/<timestamp>/
	@mkdir -p $(BACKUP_DIR)
	@echo "Backing up to $(BACKUP_DIR)/"
	mpremote cp :CatFeeder.py $(BACKUP_DIR)/CatFeeder.py + cp :main.py $(BACKUP_DIR)/main.py + cp :boot.py $(BACKUP_DIR)/boot.py 2>/dev/null; true
	@echo "Done. Contents:"
	@ls -la $(BACKUP_DIR)/

.PHONY: clean-board
clean-board: ## Remove all .py files from the board and old CatFeeder.py
	mpremote rm :main.py + rm :CatFeeder.py + rm :config.py + rm :hardware.py + rm :servo.py + rm :speaker.py + rm :buttons.py + rm :dispenser.py 2>/dev/null; true

# ── Help ───────────────────────────────────────────────

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
