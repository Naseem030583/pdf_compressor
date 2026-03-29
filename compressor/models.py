from django.db import models
import os


class PDFFile(models.Model):
    original_file = models.FileField(upload_to='uploads/')
    compressed_file = models.FileField(upload_to='compressed/', blank=True, null=True)
    original_size_kb = models.FloatField(default=0)
    compressed_size_kb = models.FloatField(default=0, blank=True, null=True)
    target_size_kb = models.IntegerField(default=500)
    reduction_percent = models.FloatField(default=0, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)

    # Logging fields
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)
    operating_system = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=20, blank=True, null=True)  # Mobile/Desktop/Tablet
    referer = models.URLField(max_length=500, blank=True, null=True)
    processing_time_seconds = models.FloatField(blank=True, null=True)
    total_pages = models.IntegerField(blank=True, null=True)
    downloaded = models.BooleanField(default=False)
    download_count = models.IntegerField(default=0)
    downloaded_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{os.path.basename(self.original_file.name)} - {self.status}"

    @property
    def original_filename(self):
        return os.path.basename(self.original_file.name)

    @property
    def compressed_filename(self):
        if self.compressed_file:
            return os.path.basename(self.compressed_file.name)
        return None
