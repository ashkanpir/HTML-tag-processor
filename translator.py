import logging
import pandas as pd
from openai_client import OpenAITranslationClient
from HTML_in_CSV_Processor import HTMLProcessor
from config import API_CONFIG

logger = logging.getLogger('website_translator')

def process_translation(input_csv, output_csv, api_key, target_language="EN"):
    """
    Loads a CSV, translates only translatable content, and ensures HTML is preserved.
    """
    df = pd.read_csv(input_csv)

    if "VALUE" not in df.columns:
        raise ValueError("CSV is missing the 'VALUE' column.")

    translator = OpenAITranslationClient(api_key)
    processor = HTMLProcessor()  # ✅ Use HTMLProcessor to preserve formatting

    # Normalize HTML before translation
    df["VALUE"] = df["VALUE"].apply(processor.normalize_html)

    # Translate only RICH_TEXT, FULL_HTML, and CSS/JS content
    df["VALUE_EN"] = df.apply(
        lambda row: processor.reconstruct_html_from_structure(
            processor.extract_html_structure(row["VALUE"]),
            translator.translate_text(row["VALUE"], target_language)
        ) if row["CONTENT_TYPE"] in ["RICH_TEXT", "FULL_HTML", "CSS/JS"] else row["VALUE"],
        axis=1
    )

    df.to_csv(output_csv, index=False)
    print(f"✅ Translated and saved to {output_csv}")

    return df
