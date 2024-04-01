from io import BytesIO
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import os
from data.models import Dataset, ColumnType  # Adjust import as necessary
from django.test import TestCase
from django.urls import reverse

import pandas as pd

# class UploadFileTest(TestCase):
#     def test_upload_file_view_with_csv(self):
#         url = reverse('data:file_upload')

#         base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#         sample_csv_path = os.path.join(base_dir, 'data', 'example_data', 'sample_data.csv')

#         self.assertTrue(os.path.exists(sample_csv_path), f"File not found: {sample_csv_path}")

#         with open(sample_csv_path, 'rb') as csv_file:
#             file_data = csv_file.read()
        
#         # Creating a SimpleUploadedFile object to mimic the file upload in the test
#         uploaded_file = SimpleUploadedFile(name='test_sample_data.csv', content=file_data, content_type='text/csv')
        
#         # Performing a POST request to the upload_file view with the file
#         response = self.client.post(url, {'datafile': uploaded_file})
        
#         # Asserting that the response status code is 200 (OK)
#         self.assertEqual(response.status_code, 200)


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


    def test_bool_conversion_handling(self):
        data = pd.DataFrame({'bool_col': ['yes', 'no', 'maybe']})
        file = self.create_upload_file(data, 'bool_test.csv')
        self.client.post(reverse('data:file_upload'), {'datafile': file})

        # Retrieve the latest dataset and its column types
        dataset = Dataset.objects.latest('id')  # Assuming 'id' or use 'uploaded_at' if available
        column_type = dataset.column_types.get(column_name='bool_col')

        # Assert that the column did not convert to boolean due to presence of 'maybe'
        self.assertNotEqual(column_type.inferred_type, 'boolean', 'Column bool_col should not have inferred type boolean.')

    def test_complex_conversion_handling(self):
        data = pd.DataFrame({'complex_col': ['1+2j', '3+4j', 'not a complex number']})
        file = self.create_upload_file(data, 'complex_test.csv')
        self.client.post(reverse('data:file_upload'), {'datafile': file})

        # Retrieve the latest dataset and its column types
        dataset = Dataset.objects.latest('id')
        column_type = dataset.column_types.get(column_name='complex_col')

        # Assert that the column did not convert to complex due to invalid value
        self.assertNotEqual(column_type.inferred_type, 'complex', 'Column complex_col should not have inferred type complex.')

        # Continue with tests for CATEGORY CONVERSION SUCCESS, CATEGORY CONVERSION ERROR, etc.

    def test_date_conversion_error(self):
        # Define test data with at least one value that should not be successfully converted to a date
        data = pd.DataFrame({
            'date_col': ['2020-01-01', 'not a date', '2020-03-01']
        })
        file = self.create_upload_file(data, 'date_test.csv')

        # Perform the file upload
        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        # Retrieve the latest dataset and check the inferred data type for 'date_col'
        dataset = Dataset.objects.latest('id')
        column_type = dataset.column_types.get(column_name='date_col')

        # Assert that 'date_col' was not converted to date due to the presence of 'not a date'
        self.assertNotEqual(column_type.user_modified_type, 'date', 'Column date_col should not have been successfully converted to date.')

    def test_integer_conversion_error(self):
        # Define test data with at least one value that cannot be successfully converted to an integer
        data = pd.DataFrame({
            'int_col': ['100', 'not an integer', '200']
        })
        file = self.create_upload_file(data, 'int_test.csv')

        # Perform the file upload
        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        # Retrieve the latest dataset and check the inferred data type for 'int_col'
        dataset = Dataset.objects.latest('id')
        column_type = dataset.column_types.get(column_name='int_col')

        # Assert that 'int_col' was not converted to integer due to 'not an integer'
        self.assertNotEqual(column_type.user_modified_type, 'integer', 'Column int_col should not have been successfully converted to integer.')

    def test_timedelta_conversion_error(self):
        # Define test data with at least one value that should not be successfully converted to timedelta
        data = pd.DataFrame({
            'timedelta_col': ['1 days', 'not a timedelta', '2 days']
        })
        file = self.create_upload_file(data, 'timedelta_test.csv')

        # Perform the file upload
        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        # Retrieve the latest dataset and its column types
        dataset = Dataset.objects.latest('id')  # Adjust if using a different identifier
        column_type = dataset.column_types.get(column_name='timedelta_col')

        # Assert the failed conversion due to the presence of 'not a timedelta'
        self.assertNotEqual(column_type.user_modified_type, 'timedelta', 'Column timedelta_col should not have been successfully converted to timedelta.')

    def test_category_conversion_error(self):
        # Define test data that shouldn't be successfully converted to category
        # Example: Assuming a very high number of unique values or non-categorical data
        data = pd.DataFrame({
            'category_col': range(1, 1001)  # 1000 unique numbers
        })
        file = self.create_upload_file(data, 'category_test.csv')

        # Perform the file upload
        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        # Retrieve the latest dataset and its column types
        dataset = Dataset.objects.latest('id')
        column_type = dataset.column_types.get(column_name='category_col')

        # Assert that 'category_col' was not converted to category due to too many unique values
        self.assertNotEqual(column_type.user_modified_type, 'category', 'Column category_col should not have been successfully converted to category.')

    def test_text_conversion_integrity(self):
        # Define test data with values that might be mistaken for dates or numbers but should stay as text
        data = pd.DataFrame({
            'text_col': ['12345', '2020-01-01', 'Hello, World!']  # Mix of numbers, dates, and clear text
        })
        file = self.create_upload_file(data, 'text_test.csv')

        # Perform the file upload
        response = self.client.post(reverse('data:file_upload'), {'datafile': file})
        self.assertEqual(response.status_code, 200, 'File upload failed when it should have succeeded.')

        # Retrieve the latest dataset and its column types
        dataset = Dataset.objects.latest('id')  # Adjust based on your models
        column_type = dataset.column_types.get(column_name='text_col')
        # Assert that the column is preserved as text, indicating no unintended conversion occurred
        self.assertEqual(column_type.user_modified_type, 'Text', 'Column text_col should have preserved its text data type.')

