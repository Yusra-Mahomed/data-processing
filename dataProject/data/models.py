from django.db import models

class Dataset(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    processed_at = models.DateTimeField(null=True, blank=True)
    original_file = models.FileField(upload_to='datasets/')
    processed_data = models.TextField(blank=True, null=True) 
    processed_file_pkl = models.BinaryField(null=True, blank=True)

    def str(self):
        return self.file_name

class ColumnType(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='column_types')
    column_name = models.CharField(max_length=255)
    original_type = models.CharField(max_length=50)
    inferred_type = models.CharField(max_length=50)
    user_modified_type = models.CharField(max_length=50, blank=True, null=True)

    def str(self):
        return f"{self.column_name} in {self.dataset.file_name} - Original: {self.original_type}, Inferred: {self.inferred_type}"