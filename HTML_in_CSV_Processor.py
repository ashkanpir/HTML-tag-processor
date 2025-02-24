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
        """Extracts only translatable text from HTML while preserving structure."""
        return re.sub(r'<[^>]+>', '', content).strip()

    @staticmethod
    def validate_html_structure(original_structure: List[List], translated_content: str, start_position: int,
                                leftover: str) -> Tuple[int, str]:
        """Validates translated content against original HTML structure."""
        translated_structure = HTMLProcessor.extract_html_structure(leftover + translated_content)

        for i, (orig, trans) in enumerate(zip(original_structure[start_position:], translated_structure)):
            if orig[1] != trans[1] or (
                    orig[1] and re.split(r'[\s>]', orig[0])[0].lower() != re.split(r'[\s>]', trans[0])[0].lower()):
                logger.error(f"Structure mismatch: Original {start_position}-{start_position + i} | Translated 0-{i}")
                return start_position, leftover  # Avoid raising error, return as is

        end_position = start_position + len(translated_structure)
        leftover = "" if translated_structure[-1][1] else leftover
        if not translated_structure[-1][1]:
            end_position -= 1

        return end_position, leftover

    @staticmethod
    def reconstruct_html_from_structure(original_structure: List[List], translated_content: str) -> str:
        """Reconstructs HTML content while preserving original structure, but only translating necessary parts."""
        result = translated_content
        search_start = 0

        for item in original_structure:
            if item[1]:  # is HTML tag or comment, leave it alone
                tag_position = result.find("<", search_start)
                if tag_position != -1:
                    result = result[:tag_position] + item[0] + result[tag_position:]
                    search_start = tag_position + len(item[0])
                continue

            # Allow translatable text inside specific tags
            if re.match(r'<(button|label|title|span|h1|h2|h3|p)>', item[0]):
                result = result.replace(item[0], HTMLProcessor.extract_translatable_text(item[0]))
                continue

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
