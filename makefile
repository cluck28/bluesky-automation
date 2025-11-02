
---

### **Makefile**
```makefile
# Variables
VENV_DIR=bluesky
STATIC_DIR=./src/static
UPLOADS_DIR=$(STATIC_DIR)/uploads
SCHEDULE_DIR=$(STATIC_DIR)/schedule
SCHEDULE_FILE=$(SCHEDULE_DIR)/schedule.csv
RULES_FILE=$(SCHEDULE_DIR)/rules.csv

# Default target
setup: venv dirs csvs
	@echo "Setup complete."

# Create virtual environment
venv:
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)/"

# Create required directories
dirs:
	@mkdir -p $(UPLOADS_DIR)
	@mkdir -p $(SCHEDULE_DIR)
	@echo "Directories created: $(UPLOADS_DIR), $(SCHEDULE_DIR)"

# Create CSV files
csvs:
	@echo "path,text,date,status" > $(SCHEDULE_FILE)
	@echo "path,text,date,status" > $(RULES_FILE)
	@echo "CSV files created in $(SCHEDULE_DIR)/"

# Clean up
clean:
	@rm -rf $(VENV_DIR)
	@rm -rf $(UPLOADS_DIR)
	@rm -rf $(SCHEDULE_DIR)
	@echo "Cleaned up environment and generated files."
