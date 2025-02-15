import os
import pandas as pd
import logging
from processor_01 import HTMLProcessor

# Set up logging
logger = logging.getLogger('html_processor')
logging.basicConfig(level=logging.INFO)

# File paths
input_csv = '/Users/ashkanpirme.com/Downloads/Translations/Source CSV Files to be translated/JETBAHIS.COM-TUR-2025_02_07-13_51_38.csv' # Update with actual file path
processed_csv = "processed_output_15.csv"

# Initialize HTML Processor
processor = HTMLProcessor()

# Load CSV
if not os.path.exists(input_csv):
    raise FileNotFoundError(f"❌ Input file not found: {input_csv}")

df = pd.read_csv(input_csv)

# Filter relevant rows
df_filtered = df[df["CONTEXT"] == "PAGE"].copy()

# Ensure there are rows to process
if df_filtered.empty:
    logger.warning("⚠️ No rows found where CONTEXT == 'PAGE'")
else:
    # Process VALUE column
    df_filtered["VALUE_processed"] = df_filtered["VALUE"].apply(
        lambda x: processor.reconstruct_html_from_structure(
            processor.extract_html_structure(str(x)), str(x)) if pd.notna(x) else ""
    )

    # Save processed CSV
    df_filtered.to_csv(processed_csv, index=False)
    logger.info(f"✅ Processed CSV saved as {processed_csv}")
