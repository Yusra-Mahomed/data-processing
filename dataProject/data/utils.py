import re
import pandas as pd
import numpy as np
import traceback
from dateutil import parser
from dateutil.parser import ParserError

column_type_overrides = {}

# def is_category(col: pd.Series, max_unique_ratio=0.5):
#     series = col.dropna()
#     # Check if series is not empty
#     if len(series) > 0:  
#         unique_ratio = len(series.unique()) / len(series)
#          # Check if unique value ratio is below or equal to the threshold
#         if unique_ratio <= max_unique_ratio: 
#             return True
#     return False

# def is_complex(col: pd.Series):
#     try:
#         # Attempt to convert each value to complex
#         for value in col.dropna():
#             complex(value)  
#     except (ValueError, TypeError):
#         return False
#     return True

# def convert_to_datetime(df, col, date_formats):
#     converted_col = None
#     for date_format in date_formats:
#         try:
#             # try to convert column to the date_format
#             converted_col = pd.to_datetime(df[col], errors='coerce', format=date_format)
#             if converted_col.notna().any():
#                 break
#         except ValueError:
#             continue
#     return converted_col if converted_col is not None and converted_col.notna().any() else df[col]

# def convert_to_numeric(df, col):
#     converted_col = pd.to_numeric(df[col], errors='coerce')
#     if converted_col.notna().any():
#         df[col] = converted_col
#         if df[col].dtype == 'float':
#             df[col] = pd.to_numeric(df[col], downcast='float')
#         elif df[col].dtype == 'int':
#             df[col] = pd.to_numeric(df[col], downcast='integer')
#     return df[col]

# def convert_to_timedelta(df, col):
#     converted_col = pd.to_timedelta(df[col], errors='coerce')
#     return converted_col if converted_col.notna().any() else df[col]

# def convert_to_boolean(df, col):
#     if all(val.lower() in ['true', 'false'] for val in df[col].astype(str).str.lower()):
#         return df[col].astype(bool)
#     return df[col]

# def convert_to_complex(df, col, is_complex):
#     if is_complex(df[col]):
#         return df[col].apply(lambda x: complex(x) if pd.notna(x) else x)
#     return df[col]

# def convert_to_categorical(df, col, is_category):
#     if is_category(df[col]):
#         return df[col].astype('category')
#     return df[col]



# def infer_and_convert_data_types(df):
#     date_formats = [
#         '%Y-%m-%d',  # Standard YYYY-MM-DD
#         '%d-%m-%Y',  # Non-standard DD-MM-YYYY
#         '%m/%d/%Y',  # Standard MM/DD/YYYY
#         '%d/%m/%Y',  # Standard DD/MM/YYYY
#         '%Y/%m/%d',  # Non-standard YYYY/MM/DD
#         '%Y%m%d',    # Standard YYYYMMDD
#         '%m/%Y',      # Standard MM/YYYY
#         '%Y/%m',      # Non-standard YYYY/MM
#         '%m.%d.%Y',  # Non-standard MM.DD.YYYY
#         '%d.%m.%Y',  # Non-standard DD.MM.YYYY
#         '%d %B',     # Non-standard DD Month (e.g., 01 January)
#         '%d%B',      # Non-standard DDMonth (e.g., 01January)
#         '%B %d',     # Non-standard Month DD (e.g., January 01)
#         '%B%d',      # Non-standard MonthDD (e.g., January01)
#         '%d %B %Y',  # Non-standard DD Month YYYY (e.g., 01 January 2022)
#         '%d%B%Y',    # Non-standard DDMonthYYYY (e.g., 01January2022)
#         '%B %d, %Y', # Non-standard Month DD, YYYY (e.g., January 01, 2022) **
#         '%Y %B %d',   # Non-standard YYYY Month DD (e.g., 2022 January 01)
#         '%B %Y',       # Non-standard Month Year (e.g., January 2022)
#         '%Y %B',       # Non-standard Year Month (e.g., 2022 January)
#         '%B%Y',        # Non-standard MonthYear (e.g., January2022)
#         '%Y%B',        # Non-standard YearMonth (e.g., 2022January)
#     ]

#     for col in df.columns:
#         if df[col].dtype == object:
#             df[col] = convert_to_datetime(df, col, date_formats)

#         if df[col].dtype == object:
#             df[col] = convert_to_numeric(df, col)

#         if df[col].dtype == object:
#             df[col] = convert_to_timedelta(df, col)

#         if df[col].dtype == object:
#             df[col] = convert_to_boolean(df, col)

#         if df[col].dtype == object:
#             df[col] = convert_to_complex(df, col, is_complex)

#         if df[col].dtype == object:
#             df[col] = convert_to_categorical(df, col, is_category)

#     return df


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
        # First, check if there are complex numbers in the column
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
        print(f"Converted {col} dtype: {converted_col.dtype}")  # Diagnostic print
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


def normalise_boolean(val):
    true_values = ['true', '1', 'yes', 't', 'on']
    false_values = ['false', '0', 'no', 'f', 'off']
    if str(val).lower() in true_values:
        return True
    elif str(val).lower() in false_values:
        return False
    else:
        return pd.NA  # Use pandas NA for undefined or unconvertible values


def can_parse_date(string):
    try:
        # Attempt to parse the string as a date.
        result = parser.parse(string, fuzzy=False)
        
        # Check if the result is really a date by ensuring it doesn't match certain non-date patterns
        non_date_patterns = [
            r"^\d+$",  # Strings that are only digits are not dates.
            r"[a-zA-Z]",  # Strings containing letters that were not parsed into a month name are not dates.
            r"^-?\d+(\.\d+)?$",  # Strings that represent a float number are not dates.
            # Add any more patterns that are known to be not dates.
        ]
        if any(re.search(pattern, string) for pattern in non_date_patterns):
            return False
        # If the date was parsed without fuzzy logic, it is likely a valid date.
        return True
    except (parser.ParserError, TypeError, ValueError):
        # If the parsing fails, it's not a date.
        return False
    
def preprocess_for_float_conversion(col):
    """
    Preprocesses a pandas Series for float conversion by replacing non-convertible values with NaN.

    Parameters:
    - col (pd.Series): The pandas Series to preprocess.

    Returns:
    - pd.Series: The preprocessed Series ready for float conversion.
    """
    col = pd.to_numeric(col, errors='coerce')
    return col


def infer_data_type(col):
    # Normalising boolean types 
    col_normalised_bool = col.apply(normalise_boolean)
    if pd.api.types.is_bool_dtype(col_normalised_bool):
        return 'Boolean'
    
    # Remove commas
    col_cleaned = col.apply(lambda x: x.replace(',', '').strip() if isinstance(x, str) else x)

    # Normalise None values
    col_cleaned = col_cleaned.apply(lambda x: None if is_allowed_none(x) else x)

    print(f"Cleaned {col.name}:", col_cleaned.tolist())  # Debug print statement

    if all(isinstance(x, bool) for x in col_cleaned.dropna()):
        return 'Boolean'
    if any(is_complex(x) for x in col_cleaned.dropna()):
        return 'Complex Number'
    if all(looks_like_number(x) for x in col_cleaned.dropna()):
        return 'Decimal'
    if any(is_timedelta(str(x)) for x in col_cleaned.dropna()):
        return 'Time Duration'
    if any(can_parse_date(str(x)) for x in col.dropna()):
        return 'Date'
    if len(set(col.dropna())) < len(col.dropna()) / 2:
        return 'Category'
    if all(isinstance(x, str) for x in col.dropna()):
        return 'Text'

    return 'Text'


def infer_and_convert_data_types(df):
    for col in df.columns:
        dtype = infer_data_type(df[col])
        if dtype == 'Decimal':
            df[col] = convert_to_numeric(df, col)
        elif dtype == 'Date':
            df[col] = convert_to_datetime(df, col)
        elif dtype == 'Time Duration':
            df[col] = convert_to_timedelta(df, col)
        elif dtype == 'Complex Number':
            df[col] = convert_to_complex(df, col)
        elif dtype == 'Boolean':
            df[col] = convert_to_boolean(df, col)
        elif dtype == 'Category':
            df[col] = df[col].astype('category')
    
    return df


def get_user_friendly_dtype(dtype):
    dtype_name = str(dtype)
    if dtype_name.startswith('int') or dtype_name.startswith('uint'):
        return 'Integer'
    elif dtype_name.startswith('float'):
        return 'Decimal'
    elif dtype_name.startswith('complex'):
        return 'Complex Number'
    elif dtype_name.startswith('timedelta'):
        return 'Time Duration'
    else:
        return {
            'object': 'Text',
            'bool': 'Boolean',
            'datetime64[ns]': 'Date',
            'category': 'Category',
        }.get(dtype_name, dtype_name) 
    
def serialise_dataframe(df):
    # Convert a DataFrame to a list of dicts with JSON serializable values
    # Convertied NaN to N/A
    df = df.copy()
    for column in df.columns:
        dtype = df[column].dtype
        if pd.api.types.is_datetime64_any_dtype(dtype):
            df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S').replace(pd.NaT, 'N/A')
        elif pd.api.types.is_timedelta64_dtype(dtype):
            df[column] = df[column].apply(lambda x: x.total_seconds() if pd.notnull(x) else 'N/A')
        elif pd.api.types.is_categorical_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
            df[column] = df[column].astype(str).replace({'nan': 'N/A', 'None': 'N/A'})
        elif pd.api.types.is_complex_dtype(dtype):
            df[column] = df[column].apply(lambda x: str(x) if pd.notnull(x) else 'N/A')

        else:
            df[column] = df[column].apply(lambda x: 'N/A' if pd.isnull(x) else x)
    
    return df.to_dict(orient='records')


def can_convert(col, conversion_function):
    try:
        conversion_function(col)
        return True
    except:
        return False


def override_data(df, column, new_type):
    print(f"Attempting to override column '{column}' to new type '{new_type}'.")
    try:
        conversion_functions = {
            'Date': lambda col: pd.to_datetime(df[col], errors='raise'),
            'Integer': lambda col: pd.to_numeric(df[col], errors='raise').astype('Int64'),
            'Decimal':  lambda col: pd.to_numeric(df[col].replace('Not Available', np.nan), errors='raise'),
            'Time Duration': lambda col: pd.to_timedelta(df[col], errors='raise'),
            'Boolean': lambda col: df[col].astype(bool),
            'Complex Number': lambda col: df[col].apply(lambda x: complex(x) if pd.notna(x) else x),
            'Category': lambda col: df[col].astype('category'),
            'Text': lambda col: df[col].astype(str) 
        }

        if new_type in conversion_functions:
            # Check if all values can be converted without error
            if can_convert(column, conversion_functions[new_type]):
                df[column] = conversion_functions[new_type](column)
                global column_type_overrides
                column_type_overrides[column] = new_type
                return True, f"Data type overridden successfully to {new_type}."
            else:
                return False, f"Cannot convert from {column} to {new_type}, operation aborted."
        else:
            return False, f"Invalid data type specified: {new_type}."

    except Exception as e:
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return False, str(e)