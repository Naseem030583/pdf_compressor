import os
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from .forms import PDFUploadForm
from .models import PDFFile
from .utils import compress_pdf


def get_client_ip(request):
    """Get real IP address, even behind proxy."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def parse_user_agent(ua_string):
    """Parse browser, OS, and device type from user agent string."""
    ua = ua_string.lower() if ua_string else ''
    info = {
        'browser': 'Unknown',
        'os': 'Unknown',
        'device': 'Desktop',
    }

    # Detect Browser
    if 'edg/' in ua or 'edge/' in ua:
        info['browser'] = 'Microsoft Edge'
    elif 'opr/' in ua or 'opera' in ua:
        info['browser'] = 'Opera'
    elif 'chrome' in ua and 'safari' in ua:
        info['browser'] = 'Google Chrome'
    elif 'firefox' in ua:
        info['browser'] = 'Mozilla Firefox'
    elif 'safari' in ua:
        info['browser'] = 'Safari'
    elif 'msie' in ua or 'trident' in ua:
        info['browser'] = 'Internet Explorer'
    elif 'brave' in ua:
        info['browser'] = 'Brave'

    # Detect OS
    if 'windows nt 10' in ua:
        info['os'] = 'Windows 10/11'
    elif 'windows nt' in ua:
        info['os'] = 'Windows'
    elif 'mac os x' in ua:
        info['os'] = 'macOS'
    elif 'android' in ua:
        info['os'] = 'Android'
    elif 'iphone' in ua or 'ipad' in ua:
        info['os'] = 'iOS'
    elif 'linux' in ua:
        info['os'] = 'Linux'
    elif 'chrome os' in ua:
        info['os'] = 'Chrome OS'

    # Detect Device
    if 'mobile' in ua or 'android' in ua and 'mobile' in ua or 'iphone' in ua:
        info['device'] = 'Mobile'
    elif 'ipad' in ua or 'tablet' in ua:
        info['device'] = 'Tablet'
    else:
        info['device'] = 'Desktop'

    return info


def home(request):
    """Home page with upload form."""
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_obj = form.save(commit=False)

            # Calculate original size
            uploaded_file = request.FILES['original_file']
            pdf_obj.original_size_kb = round(uploaded_file.size / 1024, 1)
            pdf_obj.status = 'processing'

            # Capture request info
            pdf_obj.ip_address = get_client_ip(request)
            ua_string = request.META.get('HTTP_USER_AGENT', '')
            pdf_obj.user_agent = ua_string
            ua_info = parse_user_agent(ua_string)
            pdf_obj.browser = ua_info['browser']
            pdf_obj.operating_system = ua_info['os']
            pdf_obj.device_type = ua_info['device']
            pdf_obj.referer = request.META.get('HTTP_REFERER', None)

            pdf_obj.save()

            # Compress the PDF
            input_path = pdf_obj.original_file.path

            # Generate output filename
            original_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{original_name}_compressed.pdf"
            output_dir = os.path.join(settings.MEDIA_ROOT, 'compressed')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_filename)

            try:
                # Track processing time
                start_time = time.time()
                result = compress_pdf(input_path, output_path, pdf_obj.target_size_kb)
                end_time = time.time()

                pdf_obj.compressed_file = f"compressed/{output_filename}"
                pdf_obj.compressed_size_kb = result['compressed_size_kb']
                pdf_obj.reduction_percent = result['reduction_percent']
                pdf_obj.processing_time_seconds = round(end_time - start_time, 2)
                pdf_obj.total_pages = result.get('total_pages', None)
                pdf_obj.status = 'completed'
                pdf_obj.error_message = result['message']
                pdf_obj.save()

                return redirect('result', pk=pdf_obj.pk)

            except Exception as e:
                pdf_obj.status = 'failed'
                pdf_obj.error_message = str(e)
                pdf_obj.processing_time_seconds = round(time.time() - start_time, 2)
                pdf_obj.save()
                return redirect('result', pk=pdf_obj.pk)
    else:
        form = PDFUploadForm()

    return render(request, 'compressor/home.html', {
        'form': form,
    })


def result(request, pk):
    """Show compression result."""
    pdf_obj = get_object_or_404(PDFFile, pk=pk)
    return render(request, 'compressor/result.html', {'pdf': pdf_obj})


def download(request, pk):
    """Download compressed PDF."""
    pdf_obj = get_object_or_404(PDFFile, pk=pk)
    if pdf_obj.compressed_file:
        # Track download
        pdf_obj.downloaded = True
        pdf_obj.download_count += 1
        pdf_obj.downloaded_at = timezone.now()
        pdf_obj.save()

        file_path = pdf_obj.compressed_file.path
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{pdf_obj.compressed_filename}"'
        return response
    return redirect('home')


@user_passes_test(lambda u: u.is_superuser)
def history(request):
    """Show compression history (superuser only)."""
    files = PDFFile.objects.all().order_by('-created_at')

    # Stats
    total_compressions = files.count()
    successful = files.filter(status='completed').count()
    total_saved_kb = sum(
        (f.original_size_kb - (f.compressed_size_kb or 0))
        for f in files.filter(status='completed')
    )
    unique_ips = files.values('ip_address').distinct().count()

    context = {
        'files': files,
        'total_compressions': total_compressions,
        'successful': successful,
        'total_saved_kb': round(total_saved_kb, 1),
        'total_saved_mb': round(total_saved_kb / 1024, 2),
        'unique_ips': unique_ips,
    }
    return render(request, 'compressor/history.html', context)
