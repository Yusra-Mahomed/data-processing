import re
import pandas as pd
import numpy as np
import traceback
from dateutil import parser
from dateutil.parser import ParserError


def can_parse_date(string):
   
  # Define non-date patterns to exclude strings that shouldn't be considered as dates
  non_date_patterns = [
      r"^\d+$",  # Strings that are only digits are not dates
      r"^-?\d+(.\d+)?$",  # Strings that represent a float number are not dates
    ]
  # Check against non-date patterns before attempting to parse
  if any(re.search(pattern, string) for pattern in non_date_patterns):
      return False
  try:# Attempt to parse the string as a date without using fuzzy logic
      parsed_date = parser.parse(string, fuzzy=False)
      # Additional check to ensure the string represents a meaningful date# For instance, ensuring the year makes sense (you might adjust this range)
      if parsed_date.year >= 1000 and parsed_date.year <= 9999:
          return True
      else:
          return False
  except (parser.ParserError, TypeError, ValueError):# If parsing fails, the string is not a date
      return False
    
def is_timedelta(column):
    patterns = [
        r'\d+\s*years?',
        r'\d+\s*months?',
        r'\d+\s*weeks?',
        r'\d+\s*days?',
        r'\d+\s*hours?',
        r'\d+\s*minutes?',
        r'\d+\s*seconds?',
    ]
    
    for pattern in patterns:
        if column.str.contains(pattern, case=False, regex=True).any():
            return True
    
    return False

def is_category(col: pd.Series, max_unique_ratio=0.5):
    series = col.dropna()
    # Check if series is not empty
    if len(series) > 0:  
        unique_ratio = len(series.unique()) / len(series)
         # Check if unique value ratio is below or equal to the threshold
        if unique_ratio <= max_unique_ratio: 
            return True
    return False

def is_complex(col: pd.Series):
    try:
        # Attempt to convert each value to complex
        for value in col.dropna():
            complex(value)  
    except (ValueError, TypeError):
        return False
    return True



def is_complex(val):
    if isinstance(val, complex):
        return True
    if isinstance(val, str):
        # Match strings that are in the form of a complex number (a + bi)
        match = re.match(r'^([+-]?[\d.]+)?([+-]?[\d.]+j)$', val.strip().replace(' ', ''))
        return bool(match)
    return False


def is_timedelta(string):
    # Patterns for different time units
    patterns = [
        r'\b\d+\s*years?\b',
        r'\b\d+\s*months?\b',
        r'\b\d+\s*weeks?\b',
        r'\b\d+\s*days?\b',
        r'\b\d+\s*hours?\b',
        r'\b\d+\s*minutes?\b',
        r'\b\d+\s*seconds?\b',
    ]
    return any(re.search(pattern, string, re.IGNORECASE) for pattern in patterns)

def looks_like_number(val):
    if pd.isna(val):
        return False
    if isinstance(val, (int, float, np.number)):
        return True
    if isinstance(val, str):
        # remove commas
        val = val.replace(',', '').strip()
        # Check for a percentage at the end of the string and remove it
        if val.endswith('%'):
            val = val[:-1]
        # This regex will match any string that represents an int or float, negative or positive
        if re.match(r'^-?\d+(?:\.\d+)?$', val):
            return True
    return False
