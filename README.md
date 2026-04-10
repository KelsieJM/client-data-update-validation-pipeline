# Client Update Data Validation Pipeline

A pre-load validation tool for detecting invalid characters in DCA data files before they reach downstream systems.

## The Problem

DCAs (Debt Collection Agencies) send client update files containing consumer data such as name and address changes, weekly on a Monday with an SLA of 5pm. Invalid characters in those files only get detected after the file is placed on SFTP to send to the client, where it won't send because of the invalid characters. This can sometimes require manual investigation to locate these errors, often under time pressure.

As the intermediary between DCAs and clients, validation must occur at the point of receipt, before files enter the processing pipeline. Prevention at source is the only available control, as the upstream DCA process cannot be directly governed.

This tool runs pre-validation checks before the file enters the pipeline, catching errors at the source and preventing SLA breaches.

## Business Decisions

- Fail the entire file on any invalid character found, rather than loading only clean rows. This reflects the client's requirement that data integrity is maintained across the full file. Partial loads are not acceptable as they could result in incomplete or inconsistent updates reaching the client.
- Report all invalid characters per row rather than stopping at the first. This ensures Operations has a complete picture of all errors in a single run, preventing the repetitive fix-and-reload cycle that occurs when errors are surfaced one at a time.
- Validation rules are config-driven per client rather than hardcoded. Different clients have different character restrictions, separating rules from logic means new clients can be added without modifying the script.

## How It Works

- Input file received from DCA
- Validation rules loaded from config
- Each row checked against client-specific rules
- Error report generated with full details of every violation
- Summary printed to terminal with accurate row and error counts
- Every run logged to persistent audit trail

## Features

- Config-driven multi-client rules
- Catches all errors per row, not just the first
- Distinguishes between failed rows and total errors found
- Graceful failure with clear messages if files or columns are missing

```
## Project Structure
main.py          # main validation script
config.json      # client validation rules
input.csv        # sample input file
README.md        # this file
```

## Future Improvements

- Command line arguments for dynamic file input
- Airflow DAG integration for scheduled Monday morning runs
- Database lookup instead of config file for validation rules
- Email notification on failure with error report attached
- Column validation checks before processing begins
