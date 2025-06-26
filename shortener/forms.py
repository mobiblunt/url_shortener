# ========== shortener/forms.py ==========
from django import forms
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from .models import URL
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class URLForm(forms.ModelForm):
    custom_code = forms.CharField(
        max_length=20, 
        required=False, 
        help_text="Optional: Choose your own short code"
    )
    is_public = forms.BooleanField(
        required=False, 
        initial=True,
        help_text="Make statistics public"
    )

    class Meta:
        model = URL
        fields = ['original_url', 'is_public']
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

    def clean_custom_code(self):
        custom_code = self.cleaned_data.get('custom_code')
        if custom_code:
            # Validate custom code
            if URL.objects.filter(short_code=custom_code).exists():
                raise ValidationError('This custom code is already taken.')
            if len(custom_code) < 3:
                raise ValidationError('Custom code must be at least 3 characters.')
        return custom_code

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