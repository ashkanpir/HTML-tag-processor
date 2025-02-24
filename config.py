"""
Configuration file for Multilingual HTML Translator
Updated for OpenAI compatibility
"""

# API Configuration
API_CONFIG = {
    'model': 'gpt-3.5-turbo',  # ✅ Use a valid OpenAI model
    'max_tokens': 4096,
    'temperature': 0.3,
    'api_key': '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'  # ✅ Literal API key
}

# Translation Process Configuration
TRANSLATION_CONFIG = {
    'chunk_max_size': 15000,
    'chunk_overlap': 1200,
    'overlap_parting': 2,
    'max_retries': 3,
    'sleep_time': 5,
    'min_tokens': 2000,
    'max_tokens': 8192,
    'default_temperature': 0.3,
    'recovery_mode': False,
    'verbose': True,
    'source_dir': 'website2',
    'target_dir_template': 'website2/{lang}'  # {lang} will be replaced with language code
}

# Language Settings
LANGUAGE_CONFIG = {
    'default_multiplier': 1.2,
    'rtl_languages': ['he', 'ar'],
    'asian_languages': ['ja', 'ko', 'zh'],

    'hebrew_chars': {
        'ranges': [
            (0x05D0, 0x05EA),  # Hebrew letters
            (0x05F0, 0x05F2)  # Hebrew ligatures
        ]
    },

    'source_text': {
        'website_name': "התדרדרות הארץ",
        'more_text': "עוד",
        'about_text': "אודות"
    },

    'text_separators': [
        "<br><br><div>", "<br><div>", "<div>", "<br><br><b>", "<br><b>",
        "<br><br><br>", "<br><br>", "<br>", ". ", "? ", ", ", " "
    ],

    'languages': {
        'en': {
            'name': "English",
            'html_code': "en",
            'title': "The Degeneration of the Nation",
            'more': "More",
            'about': "About",
            'multiplier': 1.2,
            'future': "Translation will be completed in the future",
            'translator_note': "Translator's note",
            'example': "Hello&nbsp;world<br><b>Title"
        }
    }
}

# Path mapping configuration
PATH_MAPPING_CONFIG = {
    'source_paths': {
        'source_section': 'translated_section'
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'format': '%(asctime)s %(levelname)s %(message)s',
    'datefmt': '%H:%M',
    'level': 'INFO',
    'log_file_suffix': 'translation_log'
}

EXECUTION_CONFIG = {
    'mode': 'full',  # or 'test'
    'test_file_count': 1
}
