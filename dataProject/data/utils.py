import pandas as pd
import numpy as np
import traceback

column_type_overrides = {}

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

def convert_to_datetime(df, col, date_formats):
    converted_col = None
    for date_format in date_formats:
        try:
            converted_col = pd.to_datetime(df[col], errors='coerce', format=date_format)
            if converted_col.notna().any():
                break
        except ValueError:
            continue
    return converted_col if converted_col is not None and converted_col.notna().any() else df[col]

def convert_to_numeric(df, col):
    converted_col = pd.to_numeric(df[col], errors='coerce')
    if converted_col.notna().any():
        df[col] = converted_col
        if df[col].dtype == 'float':
            df[col] = pd.to_numeric(df[col], downcast='float')
        elif df[col].dtype == 'int':
            df[col] = pd.to_numeric(df[col], downcast='integer')
    return df[col]

def convert_to_timedelta(df, col):
    converted_col = pd.to_timedelta(df[col], errors='coerce')
    return converted_col if converted_col.notna().any() else df[col]

def convert_to_boolean(df, col):
    if all(val.lower() in ['true', 'false'] for val in df[col].astype(str).str.lower()):
        return df[col].astype(bool)
    return df[col]

def convert_to_complex(df, col, is_complex):
    if is_complex(df[col]):
        return df[col].apply(lambda x: complex(x) if pd.notna(x) else x)
    return df[col]

def convert_to_categorical(df, col, is_category):
    if is_category(df[col]):
        return df[col].astype('category')
    return df[col]

def infer_and_convert_data_types(df):
    date_formats = [
        '%Y-%m-%d',  # Standard YYYY-MM-DD
        '%d-%m-%Y',  # Non-standard DD-MM-YYYY
        '%m/%d/%Y',  # Standard MM/DD/YYYY
        '%d/%m/%Y',  # Standard DD/MM/YYYY
        '%Y/%m/%d',  # Non-standard YYYY/MM/DD
        '%Y%m%d',    # Standard YYYYMMDD
        '%m/%Y',      # Standard MM/YYYY
        '%Y/%m',      # Non-standard YYYY/MM
        '%m.%d.%Y',  # Non-standard MM.DD.YYYY
        '%d.%m.%Y',  # Non-standard DD.MM.YYYY
        '%d %B',     # Non-standard DD Month (e.g., 01 January)
        '%d%B',      # Non-standard DDMonth (e.g., 01January)
        '%B %d',     # Non-standard Month DD (e.g., January 01)
        '%B%d',      # Non-standard MonthDD (e.g., January01)
        '%d %B %Y',  # Non-standard DD Month YYYY (e.g., 01 January 2022)
        '%d%B%Y',    # Non-standard DDMonthYYYY (e.g., 01January2022)
        '%B %d, %Y', # Non-standard Month DD, YYYY (e.g., January 01, 2022) **
        '%Y %B %d',   # Non-standard YYYY Month DD (e.g., 2022 January 01)
        '%B %Y',       # Non-standard Month Year (e.g., January 2022)
        '%Y %B',       # Non-standard Year Month (e.g., 2022 January)
        '%B%Y',        # Non-standard MonthYear (e.g., January2022)
        '%Y%B',        # Non-standard YearMonth (e.g., 2022January)
    ]

    for col in df.columns:

        if df[col].dtype == object:
            df[col] = convert_to_datetime(df, col, date_formats)

        if df[col].dtype == object:
            df[col] = convert_to_numeric(df, col)

        if df[col].dtype == object:
            df[col] = convert_to_timedelta(df, col)

        if df[col].dtype == object:
            df[col] = convert_to_boolean(df, col)

        if df[col].dtype == object:
            df[col] = convert_to_complex(df, col, is_complex)

        if df[col].dtype == object:
            df[col] = convert_to_categorical(df, col, is_category)

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

# def preprocess_for_float_conversion(col):
#     # Replace non-convertible text with NaN
#     col = pd.to_numeric(col, errors='coerce')
#     return col


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
            print("skjkd", column, new_type)
            print(df[column].dtype)
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