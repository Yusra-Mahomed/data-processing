from io import BytesIO
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import os
from data.models import Dataset, ColumnType  # Adjust import as necessary
from django.test import TestCase
from django.urls import reverse

import pandas as pd

class DataConversionTestCase(TestCase):

    def setUp(self):
        # Setup code if necessary, such as creating shared resources
        pass

    def create_upload_file(self, data, filename='test.csv'):
        """
        Helper function to create a file-like object from a DataFrame to simulate file upload.
        """
        if filename.endswith('.csv'):
            content = data.to_csv(index=False)
            # Encode the CSV string content to bytes
            content_bytes = content.encode('utf-8')
            return SimpleUploadedFile(filename, content_bytes, content_type='text/csv')
        elif filename.endswith('.xlsx'):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                data.to_excel(writer, index=False)
            output.seek(0)
            return SimpleUploadedFile(filename, output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_bool_conversion_success(self):
        # Define test data with values expected to be successfully converted to booleans
        data = pd.DataFrame({
            'bool_col': ['yes', 'no', 'true', 'false', '1', '0']
        })
        file = self.create_upload_file(data, 'bool_test.csv')

        # Perform the file upload
        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        # Retrieve the latest dataset and its column types
        dataset = Dataset.objects.latest('id')  # Adjust if using a different identifier
        column_type = dataset.column_types.get(column_name='bool_col')

        self.assertEqual(column_type.inferred_type, 'boolean', 'Column bool_col should have been successfully converted to boolean.')
    

    def test_decimal_conversion_success(self):
        data = pd.DataFrame({
            'decimal_col': ['123.45', '67.89', '0.12']  # Example decimal values as strings
        })
        file = self.create_upload_file(data, 'decimal_test.csv')

        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        dataset = Dataset.objects.latest('id')
        column_type = dataset.column_types.get(column_name='decimal_col')

        self.assertEqual(column_type.inferred_type, 'float64', 'Column decimal_col should have been successfully converted to decimal.')



    def test_integer_conversion_success(self):
        data = pd.DataFrame({
            'int_col': ['123', '456', '789']  # Integer values represented as strings
        })
        file = self.create_upload_file(data, 'int_test.csv')

        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        dataset = Dataset.objects.latest('id')
        column_type = dataset.column_types.get(column_name='int_col')

        self.assertEqual(column_type.inferred_type, 'int64', 'Column int_col should have been successfully converted to integer.')

    def test_timedelta_conversion_success(self):
        data = pd.DataFrame({
            'timedelta_col': ['1 day', '3 days', '6 hours']  # Example timedelta values
        })
        file = self.create_upload_file(data, 'timedelta_test.csv')

        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        dataset = Dataset.objects.latest('id')
        column_type = dataset.column_types.get(column_name='timedelta_col')

        self.assertEqual(column_type.inferred_type, 'timedelta64[ns]', 'Column timedelta_col should have been successfully converted to timedelta.')

    def test_date_conversion_success(self):
        data = pd.DataFrame({
            'date_col': ['2023-01-01', '2023-03-15', '2023-05-20']  # Example date values
        })
        file = self.create_upload_file(data, 'date_test.csv')

        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        dataset = Dataset.objects.latest('id')
        column_type = dataset.column_types.get(column_name='date_col')

        self.assertEqual(column_type.inferred_type, 'datetime64[ns]', 'Column date_col should have been successfully converted to date.')

    def test_complex_conversion_success(self):
        data = pd.DataFrame({
            'complex_col': ['1+2j', '3-4j', '5+6j']  # Example complex number values
        })
        file = self.create_upload_file(data, 'complex_test.csv')

        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        dataset = Dataset.objects.latest('id')
        column_type = dataset.column_types.get(column_name='complex_col')

        self.assertEqual(column_type.inferred_type, 'complex128', 'Column complex_col should have been successfully converted to complex.')
    
    def test_category_conversion_success(self):
        data = pd.DataFrame({
            'category_col': ['A', 'B', 'C', 'A', 'B', 'C']  # Example categorical values
        })
        file = self.create_upload_file(data, 'category_test.csv')

        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        dataset = Dataset.objects.latest('id')
        column_type = dataset.column_types.get(column_name='category_col')

        self.assertEqual(column_type.inferred_type, 'object', 'Column category_col should have been successfully converted to category.')