from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib import messages
from .forms import CustomUserCreationForm
import json
from .models import URL
from .forms import URLForm

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class CustomLoginView(LoginView):
    template_name = 'shortener/login.html'
    redirect_authenticated_user = True

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'shortener/register.html', {'form': form})

@login_required
def my_urls(request):
    """Show user's URLs"""
    urls = URL.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shortener/my_urls.html', {'urls': urls})

def shorten_url(request):
    """Updated to handle user and custom codes"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            original_url = data.get('url', '').strip()
            custom_code = data.get('custom_code', '').strip()
            is_public = data.get('is_public', True)
            
            if not original_url:
                return JsonResponse({'success': False, 'error': 'URL is required'})
            
            # Add protocol if missing
            if not original_url.startswith(('http://', 'https://')):
                original_url = 'http://' + original_url
            
            # Check for existing URL (only for same user)
            existing_query = URL.objects.filter(original_url=original_url)
            if request.user.is_authenticated:
                existing_query = existing_query.filter(user=request.user)
            else:
                existing_query = existing_query.filter(user__isnull=True)
            
            existing_url = existing_query.first()
            if existing_url:
                short_url = request.build_absolute_uri(
                    reverse('redirect_url', kwargs={'short_code': existing_url.short_code})
                )
                return JsonResponse({
                    'success': True, 
                    'short_url': short_url,
                    'short_code': existing_url.short_code
                })
            
            # Use custom code or generate one
            if custom_code:
                if URL.objects.filter(short_code=custom_code).exists():
                    return JsonResponse({'success': False, 'error': 'Custom code already taken'})
                short_code = custom_code
            else:
                short_code = URL.generate_short_code()
            
            # Create new URL
            url_obj = URL.objects.create(
                original_url=original_url,
                short_code=short_code,
                user=request.user if request.user.is_authenticated else None,
                is_public=is_public
            )
            
            short_url = request.build_absolute_uri(
                reverse('redirect_url', kwargs={'short_code': short_code})
            )
            
            return JsonResponse({
                'success': True, 
                'short_url': short_url,
                'short_code': short_code
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'An error occurred'})

def url_stats(request, short_code):
    """Updated to check permissions"""
    url_obj = get_object_or_404(URL, short_code=short_code)
    
    # Check if user can view stats
    if not url_obj.can_view_stats(request.user):
        messages.error(request, 'You do not have permission to view these statistics.')
        return redirect('index')
    
    context = {
        'url': url_obj,
        'short_url': request.build_absolute_uri(
            reverse('redirect_url', kwargs={'short_code': short_code})
        )
    }
    return render(request, 'shortener/stats.html', context)

def api_urls(request):
    """API endpoint to list recent URLs"""
    urls = URL.objects.all()[:50]
    data = []
    for url in urls:
        data.append({
            'original_url': url.original_url,
            'short_code': url.short_code,
            'clicks': url.clicks,
            'created_at': url.created_at.isoformat(),
            'short_url': request.build_absolute_uri(
                reverse('redirect_url', kwargs={'short_code': url.short_code})
            )
        })
    return JsonResponse(data, safe=False)

def redirect_url(request, short_code):
    """Redirect to original URL and increment click count"""
    url_obj = get_object_or_404(URL, short_code=short_code)
    url_obj.increment_clicks()
    return redirect(url_obj.original_url)

def index(request):
    """Main page with URL shortening form"""
    form = URLForm()
    context = {'form': form}
    return render(request, 'shortener/index.html', context)
