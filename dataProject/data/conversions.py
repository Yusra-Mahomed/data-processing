import re
import pandas as pd
import re
import pandas as pd
import numpy as np
import traceback
from dateutil import parser
from dateutil.parser import ParserError
from .typechecks import looks_like_number, is_complex


def is_allowed_none(val):
    return pd.isnull(val) or str(val).strip().lower() in ALLOWED_NONE_TYPES


ALLOWED_NONE_TYPES = [
    "nan",
    "na",
    "n/a",
    "none",
    "null",
    "missing",
    "miss",
    "unknow",
    "unk",
    "-999",
    "not available",
    ''
]

# Conversion Functions
def convert_to_categorical(df, col, is_category):
    if is_category(df[col]):
        return df[col].astype('category')
    return df[col]

def convert_to_datetime(df, col):
    try:
        converted_col = []
        for value in df[col]:
            if pd.isnull(value) or is_allowed_none(value):
                converted_col.append(pd.NaT)  # Append NaT for null values and allowed none types
            else:
                converted_col.append(parser.parse(str(value), fuzzy=True))
        return pd.Series(converted_col)
    except Exception as e:
        print(f"Error converting column '{col}' to datetime: {e}")
        return df[col]
    
def convert_to_timedelta(df, col):
    try:
        converted_col = pd.to_timedelta(df[col], errors='coerce')
        return converted_col
    except Exception as e:
        print(f"Error converting column '{col}' to timedelta: {e}")
        return df[col]

def convert_to_numeric(df, col):
    try:
        # Check if there are complex numbers in the column
        if df[col].apply(lambda x: is_complex(str(x))).any():
            raise ValueError(f"Column '{col}' contains complex numbers, cannot convert to numeric.")
        
        # Convert values that look like a number or percentage to decimals, else set to NaN
        df[col] = df[col].apply(
            lambda x: float(str(x).replace(',', '').strip('%')) / 100 
            if isinstance(x, str) and x.endswith('%') 
            else float(str(x).replace(',', '')) 
            if isinstance(x, str) and looks_like_number(x) 
            else x  # Keep the original value if it's not a string
        )
        
        # Now that the column is cleaned up, coerce any stragglers to NaN
        converted_col = pd.to_numeric(df[col], errors='coerce')
        print(f"Converted {col} dtype: {converted_col.dtype}")
        return converted_col
    
    except Exception as e:
        raise ValueError(f"Error converting column '{col}' to numeric: {e}")


def convert_to_boolean(df, col):
    bool_variable_map = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
        "t": True,
        "f": False,
        "on": True,
        "off": False,
        "none": None,
    }

    # Check if all values can be converted
    if not df[col].apply(lambda x: str(x).lower() in bool_variable_map or pd.isnull(x)).all():
        raise ValueError(f"Column '{col}' contains values that cannot be converted to boolean.")

    try:
        # Convert the column using the mapping
        converted_col = df[col].apply(lambda x: bool_variable_map[str(x).lower()] if pd.notnull(x) else x)
        # Convert None explicitly to pd.NA to handle nullable boolean types
        converted_col = converted_col.where(pd.notnull(converted_col), pd.NA)
        return converted_col.astype("boolean")  # Use Pandas' nullable boolean type
    except Exception as e:
        raise ValueError(f"Error converting column '{col}' to boolean: {e}")

    
def convert_to_complex(df, col):
    try:
        # Check if any value in the column is a complex number
        if df[col].apply(lambda x: isinstance(x, complex) or isinstance(x, str) and '+' in x and 'j' in x).any():
            converted_col = df[col].apply(lambda x: complex(x) if pd.notna(x) else x)
            return converted_col
        else:
            return df[col]  # If no complex numbers found, return original column
    except Exception as e:
        print(f"Error converting column '{col}' to complex: {e}")
        return df[col]