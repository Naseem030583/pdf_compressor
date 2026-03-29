from django import forms
from .models import PDFFile


class PDFUploadForm(forms.ModelForm):
    target_size_kb = forms.IntegerField(
        min_value=10,
        max_value=100000,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 500',
        }),
        label='Target Size (KB)',
        help_text='Enter your desired file size in KB'
    )

    class Meta:
        model = PDFFile
        fields = ['original_file', 'target_size_kb']
        widgets = {
            'original_file': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': '.pdf',
            }),
        }

    def clean_original_file(self):
        file = self.cleaned_data.get('original_file')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
            if file.size > 50 * 1024 * 1024:  # 50 MB limit
                raise forms.ValidationError('File size must be under 50 MB.')
        return file
