# week4_etl_pipeline

## Overview
This project automates the extraction, transformation, and loading (ETL) of operational data from CSV files to a SQLite database with comprehensive data quality validation.

## Features
- **Extract**: Reads 4,969 records from CSV files
- **Transform**: Cleans, deduplicates, and prepares data
- **Load**: Stores data in SQLite with idempotency (clears table before loading)
- **Validate**: 6 data quality rules using Great Expectations
- **Logging**: Detailed logging to `pipeline.log`
- **Automation**: Scheduled daily at 2:00 AM via Windows Task Scheduler

## Prerequisites
- Python 3.8+
- pip (Python package manager)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Sigei200/week4_etl_pipeline
cd week4_etl_pipeline

