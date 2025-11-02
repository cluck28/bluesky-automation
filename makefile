# Variables
VENV_DIR=bluesky
STATIC_DIR=./src/static
UPLOADS_DIR=$(STATIC_DIR)/uploads
SCHEDULE_DIR=$(STATIC_DIR)/schedule
LOGS_DIR=./logs
SCHEDULE_FILE=$(SCHEDULE_DIR)/schedule.csv
RULES_FILE=$(SCHEDULE_DIR)/rules.csv
REQ_FILE=requirements.txt
ENV_TEMPLATE=.env.dev
ENV_FILE=.env
CRON_JOB="15 * * * * cd $(shell pwd) && . $(VENV_DIR)/bin/activate && python src/run_scheduler.py >> logs/run_scheduler.log 2>&1"

# Default target
setup: venv dirs csvs cron
	@echo "Setup complete."

teardown: clean clean-cron
	@echo: "Teardown complete"

# Create virtual environment
venv:
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)/"
	@if [ -f $(REQ_FILE) ]; then \
		echo "Installing dependencies from $(REQ_FILE)..."; \
		. $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install -r $(REQ_FILE); \
	else \
		echo "No $(REQ_FILE) found, skipping dependency installation."; \
	fi

# Create required directories
dirs:
	@mkdir -p $(UPLOADS_DIR)
	@mkdir -p $(SCHEDULE_DIR)
	@mkdir -p $(LOGS_DIR)
	@echo "Directories created: $(UPLOADS_DIR), $(SCHEDULE_DIR), $(LOGS_DIR)"

# Create CSV files
csvs:
	@echo "path,text,date,status" > $(SCHEDULE_FILE)
	@echo "path,text,date,status" > $(RULES_FILE)
	@echo "CSV files created in $(SCHEDULE_DIR)/"
	@touch $(LOGS_DIR)/run_scheduler.log
	@echo "Log files created in $(LOGS_DIR)/"

# Copy .env.dev to .env if not exists
env:
	@if [ -f $(ENV_FILE) ]; then \
		echo "$(ENV_FILE) already exists, skipping copy."; \
	elif [ -f $(ENV_TEMPLATE) ]; then \
		cp $(ENV_TEMPLATE) $(ENV_FILE); \
		echo "Copied $(ENV_TEMPLATE) to $(ENV_FILE)."; \
	else \
		echo "No $(ENV_TEMPLATE) found, skipping .env creation."; \
	fi

cron:
	@echo "Setting up cron job..."
	@tmpfile=$$(mktemp); \
	crontab -l 2>/dev/null | grep -v -F "$(CRON_JOB)" > $$tmpfile; \
	echo "$(CRON_JOB)" >> $$tmpfile; \
	crontab $$tmpfile; \
	rm -f $$tmpfile; \
	echo "Cron job installed (duplicates avoided)."

# Clean up
clean:
	@rm -rf $(VENV_DIR)
	@rm -rf $(UPLOADS_DIR)
	@rm -rf $(SCHEDULE_DIR)
	@rm -rf $(LOGS_DIR)
	@echo "Cleaned up environment and generated files."

clean-cron:
	@echo "Removing cron job..."
	@tmpfile=$$(mktemp); \
	crontab -l 2>/dev/null | grep -v -F "$(CRON_JOB)" > $$tmpfile; \
	crontab $$tmpfile; \
	rm -f $$tmpfile; \
	echo "Cron job removed (if it existed)."