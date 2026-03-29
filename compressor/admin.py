from django.contrib import admin
from .models import PDFFile


@admin.register(PDFFile)
class PDFFileAdmin(admin.ModelAdmin):
    list_display = [
        'original_filename', 'original_size_kb', 'target_size_kb',
        'compressed_size_kb', 'reduction_percent', 'status',
        'ip_address', 'browser', 'operating_system', 'device_type',
        'processing_time_seconds', 'downloaded', 'download_count', 'created_at'
    ]
    list_filter = ['status', 'browser', 'operating_system', 'device_type', 'downloaded', 'created_at']
    search_fields = ['ip_address', 'browser', 'operating_system', 'original_file']
    readonly_fields = [
        'original_size_kb', 'compressed_size_kb', 'reduction_percent',
        'ip_address', 'user_agent', 'browser', 'operating_system',
        'device_type', 'referer', 'processing_time_seconds',
        'total_pages', 'download_count', 'downloaded_at'
    ]
