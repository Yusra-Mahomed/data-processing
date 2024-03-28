from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import os

class UploadFileTest(TestCase):
    def test_upload_file_view_with_csv(self):

        url = reverse('data:upload_file')

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sample_csv_path = os.path.join(base_dir, 'data', 'sampleData', 'sample_data.csv')

        self.assertTrue(os.path.exists(sample_csv_path), f"File not found: {sample_csv_path}")

        with open(sample_csv_path, 'rb') as csv_file:
            file_data = csv_file.read()
        
        uploaded_file = SimpleUploadedFile(name='test_sample_data.csv', content=file_data, content_type='text/csv')
    
        response = self.client.post(url, {'datafile': uploaded_file})
        
        self.assertEqual(response.status_code, 200)
