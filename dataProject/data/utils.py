import re
import pandas as pd
import numpy as np
import traceback
from dateutil import parser
from dateutil.parser import ParserError
from .conversions import is_allowed_none, convert_to_boolean, convert_to_categorical, convert_to_datetime, convert_to_numeric, convert_to_timedelta, convert_to_complex, looks_like_number
from .typechecks import is_category, is_complex, is_timedelta, looks_like_number, can_parse_date

column_type_overrides = {}

def normalise_boolean(val):
    true_values = ['true', '1', 'yes', 't', 'on']
    false_values = ['false', '0', 'no', 'f', 'off']
    if str(val).lower() in true_values:
        return True
    elif str(val).lower() in false_values:
        return False
    else:
        return pd.NA  


def infer_data_type(col):
    # Normalising boolean types 
    col_normalised_bool = col.apply(normalise_boolean)
    if pd.api.types.is_bool_dtype(col_normalised_bool):
        return 'Boolean'
    
    # Remove commas
    col_cleaned = col.apply(lambda x: x.replace(',', '').strip() if isinstance(x, str) else x)

    # Normalise None values
    col_cleaned = col_cleaned.apply(lambda x: None if is_allowed_none(x) else x)

    # Numeric type threshold check (this is for mixed types)
    numeric_count = sum(looks_like_number(x) for x in col_cleaned.dropna())
    if numeric_count / len(col_cleaned.dropna()) > 1:
        return 'Decimal'
    
    # Count the number of boolean entries
    boolean_count = sum(isinstance(x, bool) for x in col_cleaned.dropna())
    if boolean_count / len(col_cleaned.dropna()) > 1:
        return 'Boolean'
    
    
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
    if is_category(col_cleaned):
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
            'Date': lambda col: convert_to_datetime(df, col),
            'Integer': lambda col: pd.to_numeric(df[col], errors='raise').astype('Int64'),
            'Decimal': lambda col: convert_to_numeric(df, col),  # Using convert_to_numeric for Decimal as well
            'Time Duration': lambda col: pd.to_timedelta(df[col], errors='raise'),
            'Boolean': lambda col: convert_to_boolean(df, col),
            'Complex Number': lambda col: df[col].apply(lambda x: complex(x) if pd.notna(x) else x),
            'Category': lambda col: convert_to_categorical(df, col, is_category),  # Note: Ensure you have an is_category function defined
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