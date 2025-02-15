import re
import logging
import pandas as pd
from typing import List

logger = logging.getLogger('csv_html_processor')


class HTMLProcessor:
    def __init__(self):
        pass

    @staticmethod
    def remove_formatting(s: str) -> str:
        """Cleans and standardizes HTML formatting while preserving structure."""
        s = re.sub(r'\s+', ' ', s.replace("\n", " ").replace("\t", " ").replace("\r", " "))
        s = s.replace("> <", "><").replace(" <br>", "<br>").replace("<br> ", "<br>")
        return s

    @staticmethod
    def normalize_html(content: str) -> str:
        """Standardizes HTML formatting to reduce mismatches."""
        content = re.sub(r'\s+', ' ', content)  # Remove extra spaces
        content = content.replace("> <", "><")  # Fix tag spacing
        content = re.sub(r'(<[^>]+) (target|rel|class|id|style)="[^"]*"', r'\1', content)  # Remove unnecessary attributes
        return content

    @staticmethod
    def extract_html_structure(content: str) -> List[List]:
        """Extracts HTML structure from content, preserving comments and self-closing tags."""
        structure = []
        pattern = re.compile(r'(<[^>]+>|<!--.*?-->|[^<]+)')
        for match in pattern.finditer(content):
            item = match.group(1)
            if item.strip():
                structure.append([item, item.startswith('<') and item.endswith('>')])
        return structure

    @staticmethod
    def extract_translatable_text(content: str) -> str:
        """Extracts only translatable text while preserving inline content in allowed tags."""
        text = re.sub(r'<(h2|p|strong|b|i|span)[^>]*>(.*?)</\1>', r'\2', content)
        text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', text)  # Keep text inside <a>
        return text

    @staticmethod
    def reconstruct_html_from_structure(original_structure: List[List], translated_content: str) -> str:
        """
        Reconstructs HTML content while preserving original structure,
        only replacing translatable text without altering the HTML tags.
        """
        result = translated_content
        search_start = 0

        for item in original_structure:
            if item[1]:  # is an HTML tag, keep it intact
                tag_position = result.find("<", search_start)
                if tag_position != -1:
                    result = result[:tag_position] + item[0] + result[tag_position:]
                    search_start = tag_position + len(item[0])
                continue

            # Ensure extracted translatable text is placed back inside its original tag
            if re.match(r'<(h2|p|strong|b|i|span|button|label|title)>', item[0]):
                tag_name = re.match(r'<(\w+)', item[0]).group(1)
                inner_text = HTMLProcessor.extract_translatable_text(item[0])
                if inner_text.strip():  # Only keep the tag if it has meaningful content
                    result = result.replace(item[0], f'<{tag_name}>{inner_text}</{tag_name}>')

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
                    lambda x: self.reconstruct_html_from_structure(self.extract_html_structure(str(x)), str(x))
                )

        df.to_csv(output_csv, index=False)
        print(f"Processed CSV saved as {output_csv}")
