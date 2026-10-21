DIST := dist
NAME := WaniKani.alfredworkflow
BUILD := $(DIST)/.build
RUN := uv run --no-sync
JSON_FILES := $(shell git ls-files '*.json')
export HOMEBREW_NO_AUTO_UPDATE := 1

.PHONY: setup icons test lint lint-shell lint-python lint-data lint-md lint-actions format format-check audit check ci clean build verify release sync-plist link-live

setup:
	brew bundle --quiet
	uv sync --group dev

icons:
	$(RUN) --with pillow python tools/gen_icons.py
	$(RUN) --with pillow python tools/gen_command_icons.py
	for icon in icons/icon_*.png; do icon-polish.sh "$$icon" "$$icon" --size 512; done

test:
	$(RUN) pytest

lint: lint-shell lint-python lint-data lint-md lint-actions

lint-shell:
	shellcheck src/maintenance.sh

lint-python:
	$(RUN) ruff check .
	$(RUN) --with pillow pyright

lint-data:
	plutil -lint info.plist
	$(if $(JSON_FILES),jq empty $(JSON_FILES))

lint-md:
	markdownlint-cli2 "**/*.md"

lint-actions:
	actionlint

format:
	$(RUN) ruff format .

format-check:
	$(RUN) ruff format --check .

audit:
	$(RUN) pip-audit --skip-editable

check: lint format-check test

ci: check audit

clean:
	find . -name '__pycache__' -not -path './.git/*' -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache

build: check
	rm -rf $(DIST)
	mkdir -p $(BUILD)/src/wkapi $(BUILD)/icons "$(BUILD)/List Filter Images" "$(BUILD)/images/about"
	cp info.plist $(BUILD)/
	cp icon.png $(BUILD)/
	cp *.png $(BUILD)/
	cp src/wkapi/*.py $(BUILD)/src/wkapi/
	cp images/about/*.png "$(BUILD)/images/about/"
	cp icons/*.png $(BUILD)/icons/
	cp icons/icon_summary.png icons/icon_levels.png icons/icon_stats.png \
		icons/icon_accuracy.png icons/icon_leeches.png icons/icon_lessons.png \
		icons/icon_reviews.png "$(BUILD)/List Filter Images/"
	mkdir -p $(BUILD)/src
	cp src/maintenance.sh $(BUILD)/src/
	cd $(BUILD) && zip -r -q ../$(NAME) .
	rm -rf $(BUILD)
	@echo "built $(DIST)/$(NAME)"

# audits the built bundle for local paths, baked-in tokens, junk files,
# unresolved script references, and import errors.
verify:
	$(RUN) python tools/verify_bundle.py $(DIST)/$(NAME)

release: build verify
	@test -n "$(VERSION)" || (echo "usage: make release VERSION=v1.0.0" && exit 1)
	git tag $(VERSION)
	git push origin $(VERSION)
	gh release create $(VERSION) $(DIST)/$(NAME) --generate-notes

# pulls info.plist from the live Alfred workflow bundle after editing
# keywords/objects/connections in the Alfred UI. WORKFLOW_DIR is
# machine-specific, never hardcoded here - pass it at invocation.
sync-plist:
	@test -n "$(WORKFLOW_DIR)" || (echo "usage: make sync-plist WORKFLOW_DIR=/path/to/bundle" && exit 1)
	cp "$(WORKFLOW_DIR)/info.plist" info.plist
	@echo "synced info.plist from $(WORKFLOW_DIR)"

# symlinks this repo's source/icons into the live Alfred workflow bundle so
# edits here take effect immediately, without a build/install step.
# WORKFLOW_DIR is machine-specific, never hardcoded here - pass it at
# invocation. Safe to re-run (idempotent).
link-live:
	@test -n "$(WORKFLOW_DIR)" || (echo "usage: make link-live WORKFLOW_DIR=/path/to/bundle" && exit 1)
	rm -f "$(WORKFLOW_DIR)/scripts"
	ln -sfn "$(CURDIR)/src" "$(WORKFLOW_DIR)/src"
	ln -sfn "$(CURDIR)/icons" "$(WORKFLOW_DIR)/icons"
	ln -sfn "$(CURDIR)/images" "$(WORKFLOW_DIR)/images"
	ln -sfn "$(CURDIR)/icon.png" "$(WORKFLOW_DIR)/icon.png"
	for icon in *.png; do \
		[ "$$icon" = "icon.png" ] || ln -sfn "$(CURDIR)/$$icon" "$(WORKFLOW_DIR)/$$icon"; \
	done
	ln -sfn "$(CURDIR)/Makefile" "$(WORKFLOW_DIR)/Makefile"
	mkdir -p "$(WORKFLOW_DIR)/List Filter Images"
	for name in summary levels stats accuracy leeches lessons reviews; do \
		ln -sfn "$(CURDIR)/icons/icon_$$name.png" "$(WORKFLOW_DIR)/List Filter Images/icon_$$name.png"; \
	done
	@echo "linked $(WORKFLOW_DIR) to this repo"
