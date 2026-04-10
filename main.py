# ============================================================
# SECTION 1: IMPORTS
# Bring in the external modules this script needs
# ============================================================
import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path
# ============================================================
# SECTION 2: CONFIGURATION
# Define file paths as constants in one place
# so they're easy to find and change
# ============================================================
INPUT_FILE = "input.csv"
ERROR_FILE = "error_report.csv"
CONFIG_FILE = "config.json"
LOG_FILE = "run_log.csv"
# ============================================================
# SECTION 3: SAFETY CHECKS
# Verify required files exist before doing any work
# Fail immediately and clearly if something is missing
# ============================================================
if not os.path.exists(CONFIG_FILE):
    print(f"ERROR: Config file '{CONFIG_FILE}' not found.")
    print("Validation could not run. Autoload should not be triggered.")
    exit(1)

with open(CONFIG_FILE, "r") as f:
    CLIENT_CONFIG = json.load(f)

if not os.path.exists(INPUT_FILE):
    print(f"ERROR: File '{INPUT_FILE}' not found.")
    print("Validation could not run. Autoload should not be triggered.")
    exit(1)
    # ============================================================
# SECTION 4: RUN INITIALISATION
# Start the stopwatch and timestamp
# Initialise accumulators before the loop
# ============================================================
run_start = time.time()
run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

error_rows = []
total_rows = 0
# ============================================================
# SECTION 5: COLUMN VALIDATION
# Before processing any rows, confirm the file structure
# is what we expect. Fail early if columns are missing.
# ============================================================
with open(INPUT_FILE, newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    actual_columns = reader.fieldnames

    for client_name, rules in CLIENT_CONFIG.items():
        for field in rules["fields_to_check"]:
            if field not in actual_columns:
                print(f"ERROR: Expected column '{field}' not found in file.")
                print(f"Columns present: {actual_columns}")
                print("Validation could not run. Autoload should not be triggered.")
                exit(1)
                # ============================================================
# SECTION 6: MAIN PROCESSING LOOP
# Read every data row, apply client rules from config,
# collect all errors found into error_rows
# ============================================================
    for row_number, row in enumerate(reader, start=2):
        total_rows += 1

        account_id = row["account_id"]
        agency = row["agency"]
        client = row["client"]

        if client in CLIENT_CONFIG:
            client_rules = CLIENT_CONFIG[client]
            fields_to_check = client_rules["fields_to_check"]
            invalid_characters = client_rules["invalid_characters"]

            for field in fields_to_check:
                value = row[field]

                for char in invalid_characters:
                    if char in value:
                        error_rows.append({
                            "row_number": row_number,
                            "account_id": account_id,
                            "agency": agency,
                            "client": client,
                            "field": field,
                            "invalid_character": char,
                            "error_reason": f"Invalid character '{char}' found in {field}"
                        })
                        # ============================================================
# SECTION 7: ERROR REPORT
# Write all errors found to a fresh CSV file
# One row per error, regardless of which row it came from
# ============================================================
with open(ERROR_FILE, "w", newline="", encoding="utf-8") as file:
    fieldnames = [
        "row_number", "account_id", "agency", "client",
        "field", "invalid_character", "error_reason"
    ]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(error_rows)
    # ============================================================
# SECTION 8: RUN CONCLUSIONS
# Calculate summary statistics after the loop
# ============================================================
file_failed = len(error_rows) > 0
failed_rows = set(entry["row_number"] for entry in error_rows)
run_duration = round(time.time() - run_start, 2)
# ============================================================
# SECTION 9: SUMMARY OUTPUT
# Print a human-readable summary to the terminal
# Clearly states whether autoload should be triggered
# ============================================================
print("----- FILE VALIDATION SUMMARY -----")
print(f"Run time:           {run_timestamp}")
print(f"File:               {INPUT_FILE}")
print(f"Duration:           {run_duration}s")
print(f"Total rows checked: {total_rows}")
print(f"Rows failed:        {len(failed_rows)}")
print(f"Total errors found: {len(error_rows)}")
print(f"Rows passed:        {total_rows - len(failed_rows)}")

if file_failed:
    print("FILE STATUS:        FAIL")
    print(f"Error report:       {ERROR_FILE}")
    print("Reason:             One or more rows failed client validation rules.")
    print("Autoload:           NOT triggered.")
else:
    print("FILE STATUS:        PASS")
    print("No validation issues found.")
    print("Autoload:           SAFE to trigger.")
    # ============================================================
# SECTION 10: RUN LOG
# Append one row to the persistent audit trail
# Header only written on the very first run
# ============================================================
log_exists = os.path.exists(LOG_FILE)

with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
    fieldnames = ["timestamp", "filename", "total_rows",
                  "rows_failed", "rows_passed", "total_errors",
                  "status", "duration_seconds"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    if not log_exists:
        writer.writeheader()

    writer.writerow({
        "timestamp": run_timestamp,
        "filename": INPUT_FILE,
        "total_rows": total_rows,
        "rows_failed": len(failed_rows),
        "rows_passed": total_rows - len(failed_rows),
        "total_errors": len(error_rows),
        "status": "FAIL" if file_failed else "PASS",
        "duration_seconds": run_duration
    })

print(f"Run logged to:      {LOG_FILE}")