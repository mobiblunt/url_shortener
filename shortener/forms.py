# ========== shortener/forms.py ==========
from django import forms
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from .models import URL

class URLForm(forms.ModelForm):
    class Meta:
        model = URL
        fields = ['original_url']
        widgets = {
            'original_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/very/long/url',
                'required': True,
            })
        }
        labels = {
            'original_url': 'Enter your long URL:'
        }
    
    def clean_original_url(self):
        url = self.cleaned_data['original_url']
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Validate URL format
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValidationError('Please enter a valid URL.')
        except:
            raise ValidationError('Please enter a valid URL.')
        
        return url