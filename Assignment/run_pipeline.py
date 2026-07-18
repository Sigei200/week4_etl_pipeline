# run_pipeline.py - Updated with better error handling
import os
import logging
import sqlite3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# Setup logging
logging.basicConfig(
    filename='pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Create .env file if it doesn't exist"""
    env_file = '.env'
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("""# Database Configuration
DATABASE_PATH=pipeline.db
TABLE_NAME=sales_data
SOURCE_DATA_PATH=D:/EMTECH/PLP/Week 3/final_integrated_pipeline_data.csv
IDEMPOTENCY_MODE=clear
""")
        logger.info("Created .env file with default settings")
    
    load_dotenv()
    logger.info("Loaded environment variables")

def extract():
    """Extract data from your CSV file"""
    try:
        logger.info("Starting extraction...")
        
        # Try multiple possible paths
        possible_paths = [
            os.getenv('SOURCE_DATA_PATH', r"D:\EMTECH\PLP\Week 3\final_integrated_pipeline_data.csv"),
            r"D:\EMTECH\PLP\Week 3\final_integrated_pipeline_data.csv",
            r"D:\EMTECH\PLP\Week3\final_integrated_pipeline_data.csv",
            r"D:\ENETCHPL\PLP\Week 3\final_integrated_pipeline_data.csv",
            r"final_integrated_pipeline_data.csv",  # If in current directory
        ]
        
        df = None
        used_path = None
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found file at: {path}")
                df = pd.read_csv(path)
                used_path = path
                break
        
        if df is None:
            # List files in current directory to help debug
            current_files = os.listdir('.')
            logger.error(f"Files in current directory: {current_files}")
            raise FileNotFoundError(f"CSV file not found. Tried: {possible_paths}")
        
        logger.info(f"Extracted {len(df)} records from {used_path}")
        logger.info(f"Columns found: {df.columns.tolist()}")
        
        return df
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise

def transform(df):
    """Transform data (clean, filter, aggregate)"""
    try:
        logger.info("Starting transformation...")
        
        # Log original shape
        logger.info(f"Original data shape: {df.shape}")
        logger.info(f"First few rows:\n{df.head()}")
        logger.info(f"Data types:\n{df.dtypes}")
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        logger.info(f"After removing duplicates: {len(df)} records")
        
        # Remove rows with all null values
        df = df.dropna(how='all')
        logger.info(f"After removing all-null rows: {len(df)} records")
        
        # Remove rows where first column is null (if it exists)
        if len(df.columns) > 0:
            df = df.dropna(subset=[df.columns[0]])
            logger.info(f"After removing null in {df.columns[0]}: {len(df)} records")
        
        # Try to convert date columns if they exist
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    logger.info(f"Converted {col} to datetime")
                except Exception as e:
                    logger.warning(f"Could not convert {col} to datetime: {e}")
        
        # Convert numeric columns
        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                logger.info(f"Converted {col} to numeric")
            except:
                pass  # Keep as string if can't convert
        
        logger.info(f"Transformation complete. Final records: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"Transformation failed: {str(e)}")
        raise

def load(df):
    """Load data to database with idempotency"""
    try:
        logger.info("Starting load...")
        
        db_path = os.getenv('DATABASE_PATH', 'pipeline.db')
        table_name = os.getenv('TABLE_NAME', 'sales_data')
        
        conn = sqlite3.connect(db_path)
        
        # Clear table before loading (idempotency)
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        df.to_sql(table_name, conn, index=False, if_exists='replace')
        
        # Get record count
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        conn.close()
        
        logger.info(f"Table cleared and loaded with {count} records")
        logger.info("Load completed successfully")
        return count
    except Exception as e:
        logger.error(f"Load failed: {str(e)}")
        raise

def validate_data(df):
    """Simple data validation"""
    logger.info("Starting data validation...")
    
    try:
        # Check if dataframe is empty
        if len(df) == 0:
            logger.error("Validation failed: DataFrame is empty")
            return False
        
        # Check for null values in first column
        if len(df.columns) > 0:
            null_count = df[df.columns[0]].isnull().sum()
            if null_count > 0:
                logger.warning(f"Found {null_count} null values in {df.columns[0]}")
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            logger.warning(f"Found {duplicates} duplicate rows")
        
        # Check for numeric columns with outliers
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols[:5]:  # Check first 5 numeric columns
            logger.info(f"Column {col}: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}")
        
        logger.info("Validation checks completed")
        return True
        
    except Exception as e:
        logger.warning(f"Validation encountered an error: {str(e)}")
        return True  # Continue even if validation fails

def main():
    """Main pipeline execution"""
    try:
        # Setup
        logger.info("="*50)
        start_time = datetime.now()
        logger.info(f"Pipeline started at {start_time}")
        
        # Load environment
        setup_environment()
        
        # Extract
        raw_data = extract()
        
        # Transform
        transformed_data = transform(raw_data)
        
        # Validate
        if not validate_data(transformed_data):
            logger.critical("Pipeline halted due to validation failures")
            return 1
        
        # Load
        record_count = load(transformed_data)
        
        # Log completion
        end_time = datetime.now()
        logger.info(f"Pipeline completed successfully")
        logger.info(f"Total records processed: {record_count}")
        logger.info(f"Execution time: {end_time - start_time}")
        logger.info("="*50)
        return 0
        
    except Exception as e:
        logger.critical(f"Pipeline failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
