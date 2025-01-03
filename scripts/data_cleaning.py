import pandas as pd
import re
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
def setup_logging():
    """Configure logging to write to both file and console"""
    # Create logs directory if it doesn't exist
    log_dir = Path("../logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"data_cleaning_{timestamp}.log"
    
    # Create formatters and handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logging.info(f"Logging to file: {log_file}")

class ElectionDataCleaner:
    
    COLUMN_PATTERNS = {
        'Occupation': {
            r'(?i)trade[r]?\s*$': 'Trader',
            r'(?i)farm(er)?s?\s*$': 'Farmer',
            r'(?i)seam?stress|s[ei]amstress': 'Seamstress',
            r'(?i)hair\s*dress?[e]?r|hair.*style': 'Hairdresser',
            r'(?i)teach(er)?\s*$': 'Teacher',
            r'(?i)driv(er)?\s*$': 'Driver',
            r'(?i)okada\s*(rider)?': 'Okada Rider',
            r'(?i)unemployed?': 'Unemployed'
        },
        'Party_Belong': {
            r'(?i)^ndc\s*$|^n$': 'NDC',
            r'(?i)^npp\s*$': 'NPP',
            r'(?i)^cpp\s*$': 'CPP',
            r'(?i)new\s*force': 'New Force',
            r'(?i)none|unknown|cant\s*tell': 'Not Specified'
        },
        'Voted_Last_Election': {
            r'(?i)^y(es)?$': 'Yes',
            r'(?i)^n(o)?$': 'No'
        },
        'Reason_Not_Voted': {
            r"(?i)wasn'?t?\s*interested|no\s*interest": "Not Interested",
            r"(?i)no\s*transport|transportation": "No Transportation",
            r"(?i)missing\s*id|no\s*id|lost\s*id": "ID Issues",
            r"(?i)sick|illness|health": "Health Issues",
            r"(?i)travel|busy|work": "Not Available",
            r"(?i)^$|none|no\s*response": "No Response"
        },
        'Know_Projects': {
            r"(?i)yes.*knew.*about.*them": "Yes, Knew Projects",
            r"(?i)heard.*but.*not.*helpful": "Heard But Not Helpful",
            r"(?i)did.*not.*know|don'?t?\s*know": "Did Not Know",
            r"(?i)^$|none|no\s*response": "No Response"
        },
        'Solved_Community_Problems': {
            r"(?i)yes.*solved.*major.*issue": "Yes, Solved Major Issues",
            r"(?i)tried.*but.*wasn'?t?\s*enough|partial": "Partial Solution",
            r"(?i)no.*solution|didn'?t?\s*solve": "No Solution",
            r"(?i)^$|none|no\s*response": "No Response"
        },
        'Fair_Election_Results': {
            r"(?i)^y(es)?$|fair": "Yes",
            r"(?i)^n(o)?$|unfair": "No",
            r"(?i)don'?t?\s*know|unsure": "Don't Know",
            r"(?i)^$|none|no\s*response": "No Response"
        }
    }

    TEXT_PATTERNS = {
        'encoding_artifacts': r'(?:Ã\s*Â|Ã\s*\w|\s*Â|Ât|â€™|â€|Ã¢â‚¬â„¢)',
        'apostrophes': r"['']",
        'quotes': r'["""]',
        'whitespace': r'\s+',
        'special_chars': r'[^\w\s\'-]',
        'trailing': r'^\s+|\s+$',
        'multiple_spaces': r' +'
    }

    TEXT_REPLACEMENTS = {
        'encoding_artifacts': '',
        'apostrophes': "'",
        'whitespace': ' ',
        'special_chars': '',
        'trailing': '',
        'quotes': '',
        'multiple_spaces': ' ',
    }

    def __init__(self, input_file: str):
        self.input_file = Path(input_file)
        self.data = None
        
    def load_data(self):
        """Load data with proper encoding"""
        encodings = ['utf-8', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                self.data = pd.read_csv(self.input_file, encoding=encoding)
                self.validate_data()
                logging.info(f"Successfully loaded data using {encoding} encoding")
                logging.info(f"Loaded {len(self.data)} records")
                return True
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logging.error(f"Error loading data: {e}")
                return False
        
        logging.error("Failed to load data with any encoding")
        return False

    def validate_data(self):
        """Validate required columns exist"""
        missing_cols = [col for col in self.COLUMN_PATTERNS.keys() 
                       if col not in self.data.columns]
        if missing_cols:
            logging.warning(f"Missing columns: {missing_cols}")

    def clean_text(self, text: str) -> str:
        """Clean text using defined patterns"""
        if pd.isna(text):
            return "Unknown"
        
        text = str(text)
        
        # Convert common UTF-8 encoded characters first
        text = text.replace('Ã¢', 'a')
        text = text.replace('Ât', "'t")
        text = text.replace('â€™', "'")
        text = text.replace('â€œ', '"')
        text = text.replace('â€', '"')
        # Additional replacement for problematic apostrophe
        text = text.replace('ÃÂ', "'")
        text = text.replace('ÃÂ', "'")
        
        
        # Apply encoding artifacts cleaning
        text = re.sub(self.TEXT_PATTERNS['encoding_artifacts'], '', text)
        
        # Then apply other cleaning patterns
        for pattern_name, pattern in self.TEXT_PATTERNS.items():
            if pattern_name not in ['encoding_artifacts']:  # Skip as already handled
                replacement = self.TEXT_REPLACEMENTS[pattern_name]
                text = re.sub(pattern, replacement, text)
        
        # Final cleanup
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces
        
        return text or "Unknown"

    def standardize_column(self, column: str):
        """Standardize values in a column using regex patterns"""
        if column not in self.COLUMN_PATTERNS:
            return
        
        original_values = self.data[column].value_counts()
        self.data[column] = self.data[column].apply(self.clean_text)
        patterns = self.COLUMN_PATTERNS[column]
        
        for pattern, replacement in patterns.items():
            self.data[column] = self.data[column].replace(
                to_replace=pattern,
                value=replacement,
                regex=True
            )
        
        # Report changes
        new_values = self.data[column].value_counts()
        logging.info(f"\nColumn {column} standardization:")
        logging.info(f"Original unique values: {len(original_values)}")
        logging.info(f"New unique values: {len(new_values)}")
        logging.info("Value mappings:")
        for val in original_values.index:
            if val in self.data[column].values:
                continue
            mapped_to = self.data[self.data[column].notna()][column].iloc[0]
            logging.info(f"  '{val}' → '{mapped_to}'")

    def standardize_column_with_search(self, column):
        """Standardize values by explicitly checking each pattern."""
        if column not in self.COLUMN_PATTERNS:
            return

        def match_pattern(text):
            text = self.clean_text(text)
            for pattern, replacement in self.COLUMN_PATTERNS[column].items():
                if re.search(pattern, text, re.IGNORECASE):
                    return replacement
            return "Other"

        self.data[column] = self.data[column].apply(match_pattern)

    def clean_data(self):
        """Clean all columns in dataset"""
        if self.data is None:
            logging.error("No data loaded")
            return False

        logging.info("Starting data cleaning process...")
        initial_null_counts = self.data.isnull().sum()

        for column in self.COLUMN_PATTERNS.keys():
            if column in self.data.columns:
                logging.info(f"\nCleaning column: {column}")
                self.standardize_column_with_search(column)

        final_null_counts = self.data.isnull().sum()
        
        # Report cleaning results
        logging.info("\nCleaning Summary:")
        for column in self.data.columns:
            initial_nulls = initial_null_counts[column]
            final_nulls = final_null_counts[column]
            if initial_nulls != final_nulls:
                logging.info(f"{column}: Filled {initial_nulls - final_nulls} null values")
        
        return True

    def save_cleaned_data(self, output_file: str):
        """Save cleaned data to file"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.data.to_csv(output_path, index=False)
            logging.info(f"Saved cleaned data to {output_path}")
            return True
        except Exception as e:
            logging.error(f"Error saving data: {e}")
            return False

def main():
    setup_logging()
    cleaner = ElectionDataCleaner("../data/CleanedElectionSurvey.csv")
    if cleaner.load_data() and cleaner.clean_data():
        cleaner.save_cleaned_data("../data/cleaned/CleanedElectionSurvey_v3.csv")

if __name__ == "__main__":
    main()