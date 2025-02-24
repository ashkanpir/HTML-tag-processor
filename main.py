import os
import pandas as pd
import time
import logging
from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup
from tqdm import tqdm
from processor_01 import HTMLProcessor  # Ensure you have this module

# Configuration
SOURCE_FILE = ".html_processor/CSVs/processed_output.csv"  # File with VALUE_processed column
OUTPUT_FILE = ".html_processor/CSVs/translated_output.csv"
LOG_FILE = "translation_log.txt"
TARGET_LANGUAGE = "en"  # English Translation
BATCH_SIZE = 200
RATE_LIMIT_DELAY = 1  # Delay in seconds
API_RETRY_LIMIT = 3  # Number of retries for failed translations

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Processor
processor = HTMLProcessor()


def translate_text(text):
    """Translates only translatable text while preserving HTML structure."""
    if pd.isna(text) or not text.strip():
        return text  # Skip empty or NaN values

    original_structure = processor.extract_html_structure(text)
    translatable_text = processor.extract_translatable_text(text)

    retries = 0
    while retries < API_RETRY_LIMIT:
        try:
            translated_text = GoogleTranslator(source="tr", target=TARGET_LANGUAGE).translate(translatable_text)
            return processor.reconstruct_html_from_structure(original_structure, translated_text)
        except Exception as e:
            logging.error(f"❌ Translation failed for text: {text[:50]} | Attempt {retries + 1} | Error: {e}")
            retries += 1
            time.sleep(2)  # Wait before retrying

    return "ERROR: Translation Failed"


def process_translation():
    """Reads the processed CSV, translates text, and saves the output."""
    df = pd.read_csv(SOURCE_FILE)

    if "VALUE_processed" not in df.columns:
        raise ValueError("❌ Column 'VALUE_processed' is missing. Ensure the file has been pre-processed.")

    print(f"🚀 Translating {len(df)} rows... This may take a while.")
    tqdm.pandas(desc="Translating...")

    df["VALUE_EN"] = df["VALUE_processed"].progress_apply(translate_text)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Translation complete! Saved to {OUTPUT_FILE}")
    logging.info(f"Translation completed. Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    process_translation()
