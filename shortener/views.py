from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib import messages
import json
from .models import URL
from .forms import URLForm

def index(request):
    """Main page with URL shortening form"""
    form = URLForm()
    context = {'form': form}
    return render(request, 'shortener/index.html', context)

def shorten_url(request):
    """Handle URL shortening via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            original_url = data.get('url', '').strip()
            
            if not original_url:
                return JsonResponse({'success': False, 'error': 'URL is required'})
            
            # Add protocol if missing
            if not original_url.startswith(('http://', 'https://')):
                original_url = 'http://' + original_url
            
            # Check if URL already exists
            existing_url = URL.objects.filter(original_url=original_url).first()
            if existing_url:
                short_url = request.build_absolute_uri(
                    reverse('redirect_url', kwargs={'short_code': existing_url.short_code})
                )
                return JsonResponse({
                    'success': True, 
                    'short_url': short_url,
                    'short_code': existing_url.short_code
                })
            
            # Create new shortened URL
            short_code = URL.generate_short_code()
            url_obj = URL.objects.create(
                original_url=original_url,
                short_code=short_code
            )
            
            short_url = request.build_absolute_uri(
                reverse('redirect_url', kwargs={'short_code': short_code})
            )
            
            return JsonResponse({
                'success': True, 
                'short_url': short_url,
                'short_code': short_code
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'An error occurred'})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

def redirect_url(request, short_code):
    """Redirect to original URL and increment click count"""
    url_obj = get_object_or_404(URL, short_code=short_code)
    url_obj.increment_clicks()
    return redirect(url_obj.original_url)

def url_stats(request, short_code):
    """Display statistics for a shortened URL"""
    url_obj = get_object_or_404(URL, short_code=short_code)
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
