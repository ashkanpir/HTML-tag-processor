import re
import logging
import pandas as pd
from typing import List, Tuple
from config import LANGUAGE_CONFIG
from collections import Counter

logger = logging.getLogger('csv_html_processor')


class HTMLProcessor:
    def __init__(self):
        pass

    @staticmethod
    def remove_formatting(s: str) -> str:
        """Cleans and standardizes HTML formatting while preserving structure"""
        s = re.sub(r'\s+', ' ', s.replace("\n", " ").replace("\t", " ").replace("\r", " "))
        s = s.replace("> <", "><").replace(" <br>", "<br>").replace("<br> ", "<br>")
        return s

    @staticmethod
    def normalize_html(content: str) -> str:
        """Standardizes HTML formatting to reduce mismatches."""
        content = re.sub(r'\s+', ' ', content)  # Remove extra spaces
        content = content.replace("> <", "><")  # Fix tag spacing
        content = re.sub(r'(<[^>]+) (target|rel|class|id|style)="[^"]*"', r'\1',
                         content)  # Remove unnecessary attributes
        return content

    @staticmethod
    def truncate_str(s: str, length: int = 30) -> str:
        """Truncates string with ellipsis in middle if too long"""
        return f"{s[:length]}...{s[-length:]}" if len(s) > length * 2 else s

    @staticmethod
    def extract_html_structure(content: str) -> List[List]:
        """Extracts HTML structure from content, preserving comments and self-closing tags."""
        structure = []
        pattern = re.compile(r'(<[^>]+>|<!--.*?-->|[^<]+)')
        for match in pattern.finditer(content):
            item = match.group(1)
            end_position = match.end()
            if item.strip():
                structure.append([item, item.startswith('<') and item.endswith('>'), end_position])
        return structure

    @staticmethod
    def extract_translatable_text(content: str) -> str:
        """Extracts only translatable text while preserving inline content in allowed tags."""
        return re.sub(r'<(h2|p|strong|b|i|span)[^>]*>(.*?)</\1>', r'\2', content)

    @staticmethod
    def reconstruct_html_from_structure(original_structure: List[List], translated_content: str) -> str:
        """Reconstructs HTML content while preserving original structure, ensuring correct tag placement."""
        result = translated_content
        search_start = 0

        for item in original_structure:
            if item[1]:  # is HTML tag or comment, leave it alone
                tag_position = result.find("<", search_start)
                if tag_position != -1:
                    result = result[:tag_position] + item[0] + result[tag_position:]
                    search_start = tag_position + len(item[0])
                continue

            # Ensure extracted translatable text is placed back inside its original tag
            if re.match(r'<(button|label|title|span|h1|h2|h3|p|strong|b|i)>', item[0]):
                tag_name = re.match(r'<(\w+)', item[0]).group(1)
                inner_text = HTMLProcessor.extract_translatable_text(item[0])
                if inner_text.strip():  # Only keep the tag if it has meaningful content
                    result = result.replace(item[0], f'<{tag_name}>{inner_text}</{tag_name}>')
                else:
                    # If an empty tag is inside a meaningful parent, remove only the empty child
                    result = re.sub(rf'<{tag_name}[^>]*></{tag_name}>', '', result)
                continue

            # Remove duplicate and empty headers like <h2></h2><h2>Title</h2>
            result = re.sub(r'<h(\d)></h\1>\s*<h\d>', '<h\1>', result)

            # Correct misplaced closing tags (e.g., <p><h2>...</p></h2>)
            result = re.sub(r'<p>(<h\d>.*?</h\d>)</p>', r'\1', result)  # Move headers out of <p>
            result = re.sub(r'<h\d></h\d>', '', result)  # Remove empty header tags

            # Ensure correct nesting: move misplaced <h2> out of <p>
            result = re.sub(r'<p>(<h\d>.*?</h\d>)</p>', r'\1', result)
            result = re.sub(r'<h\d></h\d>', '', result)  # Remove empty headers

            # Keep <a> tags intact but allow text inside them to be translated
            if item[0].startswith("<a ") and item[0].endswith("</a>"):
                inner_text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', item[0])
                translated_inner = HTMLProcessor.extract_translatable_text(inner_text)
                result = result.replace(inner_text, translated_inner)
                continue

        return result

    def process_csv(self, input_csv: str, output_csv: str, html_columns: List[str]):
        """Process CSV file, applying HTML structure validation and reconstruction to specified columns."""
        df = pd.read_csv(input_csv)

        for column in html_columns:
            if column in df.columns:
                df[column] = df[column].apply(self.normalize_html)  # Apply normalization before processing
                df[f'{column}_translatable'] = df[column].apply(self.extract_translatable_text)
                df[f'{column}_processed'] = df[column].apply(
                    lambda x: self.reconstruct_html_from_structure(self.extract_html_structure(str(x)), str(x)))

        df.to_csv(output_csv, index=False)
        print(f"Processed CSV saved as {output_csv}")
