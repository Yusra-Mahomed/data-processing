from django.test import TestCase
from django.urls import reverse
from data.models import Dataset  # Adjust import as per your project structure
from data.views import override_data_type
import json

class OverrideDataTypeTestCase(TestCase):

    def setUp(self):
        # Create a test Dataset object with processed file pickle data
        self.dataset = Dataset.objects.create(
            file_name='test_data.csv',
            processed_file_pkl=b'\x80\x04\x95\x00\x00\x00\x00\x00\x00\x00\x8c\x08pandas...',
        )

    def test_overriding_column_to_date_error(self):
        # Attempt to override a column to 'date', which is not supported
        data = {'column': 'some_column', 'new_type': 'date'}
        response = self.client.post(reverse('data:override'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json())

    def test_overriding_column_to_complex_error(self):
        # Attempt to override a column to 'complex', which is not supported
        data = {'column': 'some_column', 'new_type': 'complex'}
        response = self.client.post(reverse('data:override'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json())

    def test_overriding_column_to_int_error(self):
        # Attempt to override a column to 'int', which is not supported
        data = {'column': 'some_column', 'new_type': 'int'}
        response = self.client.post(reverse('data:override'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json())

    def test_overriding_column_to_decimal_error(self):
        # Attempt to override a column to 'decimal', which is not supported
        data = {'column': 'some_column', 'new_type': 'decimal'}
        response = self.client.post(reverse('data:override'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json())

    def test_overriding_column_to_timedelta_error(self):
        # Attempt to override a column to 'timedelta', which is not supported
        data = {'column': 'some_column', 'new_type': 'timedelta'}
        response = self.client.post(reverse('data:override'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json())

    def test_overriding_column_to_bool_error(self):
        # Attempt to override a column to 'bool', which is not supported
        data = {'column': 'some_column', 'new_type': 'bool'}
        response = self.client.post(reverse('data:override'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json())

    def test_overriding_column_to_category_error(self):
        # Attempt to override a column to 'category', which is not supported
        data = {'column': 'some_column', 'new_type': 'category'}
        response = self.client.post(reverse('data:override'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json())

    # Add more tests for other error cases as needed
