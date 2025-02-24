import pandas as pd
import re
from bs4 import BeautifulSoup

# HTML Tag Categories
RICH_TEXT_TAGS = {
    "b", "i", "u", "strong", "em", "mark", "span", "a",
    "h1", "h2", "h3", "h4", "h5", "h6", "ul", "li", "p", "br", "blockquote",
    "hr", "code", "cite"
}

FULL_HTML_TAGS = {
    "div", "section", "table", "header", "footer", "article", "aside",
    "form", "iframe", "colgroup", "fieldset", "nav"
}

CSS_JS_TAGS = {"style", "script"}

def classify_content(text):
    """
    Classifies text content into categories:
    - PLAIN_TEXT: No HTML elements.
    - RICH_TEXT: Readable text with inline HTML (<b>, <i>, <h1>, etc.).
    - FULL_HTML: Structured HTML (e.g., <div>, <table>, <section>).
    - CSS/JS: Contains <style> or <script>.
    - UNKNOWN: If it doesn’t fit neatly into any category.
    """
    if pd.isna(text) or not text.strip():
        return "EMPTY"

    soup = BeautifulSoup(text, "html.parser")

    # Identify CSS/JS content
    if any(tag.name in CSS_JS_TAGS for tag in soup.find_all()):
        return "CSS/JS"

    # Identify FULL_HTML (heavy structure)
    if any(tag.name in FULL_HTML_TAGS for tag in soup.find_all()):
        return "FULL_HTML"

    # Identify RICH_TEXT (inline formatting and readable text)
    if any(tag.name in RICH_TEXT_TAGS for tag in soup.find_all()):
        return "RICH_TEXT"

    # If it's only an image or a simple tag, classify as rich text
    if soup.find("img") or soup.find("hr") or soup.find("br"):
        return "RICH_TEXT"

    # If it has no recognizable HTML, it's plain text
    if not soup.find():
        return "PLAIN_TEXT"

    return "UNKNOWN"


def process_csv(input_csv, output_csv):
    """Loads a CSV, classifies the VALUE column, and saves results."""
    df = pd.read_csv(input_csv)

    if "VALUE" not in df.columns:
        raise ValueError("CSV is missing the 'VALUE' column.")

    print(f"Processing {len(df)} rows...")
    df["CONTENT_TYPE"] = df["VALUE"].apply(classify_content)
    df.to_csv(output_csv, index=False)
    print(f"✅ Processed and saved to {output_csv}")

    return df


def filter_content(input_csv, output_filtered_csv):
    """Filters classified data for translation-relevant content types."""
    df = pd.read_csv(input_csv)

    # Select only the necessary content types
    filtered_df = df[df['CONTENT_TYPE'].isin(['RICH_TEXT', 'FULL_HTML', 'CSS/JS', 'UNKNOWN'])]

    filtered_df.to_csv(output_filtered_csv, index=False)
    print(f"✅ Filtered content saved to {output_filtered_csv}")

    return filtered_df

import pandas as pd
from content_classifier import process_csv, filter_content

# File paths
input_file = "/Users/ashkanpirme.com/Downloads/Translations/Source CSV Files to be translated/DISCOUNTCASINO.COM-TUR-2025_02_07-12_53_21.csv"  # Change this to your actual file
classified_output_file = ".html_processor/CSVs/classified_output_discount_casion_02.csv"
filtered_output_file = ".html_processor/CSVs/filtered_classified_output_discount_casion_02.csv"

# Step 1: Classify the content
df = process_csv(input_file, classified_output_file)

# Step 2: Filter the classified content
filtered_df = filter_content(classified_output_file, filtered_output_file)


