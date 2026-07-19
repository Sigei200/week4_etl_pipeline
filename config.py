"""Configuration helper for the ETL pipeline."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'pipeline.db')
TABLE_NAME = os.getenv('TABLE_NAME', 'sales_data')
SOURCE_DATA_PATH = os.getenv('SOURCE_DATA_PATH', 'data/source.csv')
IDEMPOTENCY_MODE = os.getenv('IDEMPOTENCY_MODE', 'clear')

# Validation thresholds
MAX_TEMPERATURE = float(os.getenv('MAX_TEMPERATURE', 150))
MIN_PRESSURE = float(os.getenv('MIN_PRESSURE', 0))
MAX_PRESSURE = float(os.getenv('MAX_PRESSURE', 1000))
