import pandas as pd
from translator import process_translation
from config import API_CONFIG

# File paths
input_file = "/Users/ashkanpirme.com/PycharmProjects/HTML_Processor_Translator/.html_processor/CSVs/filtered_classified_output_discount_casion_02.csv"
translated_output_file = "translated_discount_casion_02.csv"

# Step 2: Translate content while preserving HTML structure
translated_df = process_translation(input_file, translated_output_file, API_CONFIG['api_key'], target_language="EN")

# Step 3: Display the translated data
#import ace_tools as tools
#tools.display_dataframe_to_user(name="Translated Output", dataframe=translated_df)
