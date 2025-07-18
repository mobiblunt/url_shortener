from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import string
import random

class URL(models.Model):
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    clicks = models.PositiveIntegerField(default=0)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=True)  # Public or private URL


    class Meta:
        ordering = ['-created_at']

    def can_view_stats(self, user):
        """Check if user can view statistics"""
        return self.is_public or self.user == user or user.is_staff
    
    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"
    
    @classmethod
    def generate_short_code(cls, length=6):
        """Generate a unique short code"""
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not cls.objects.filter(short_code=code).exists():
                return code
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('redirect_url', kwargs={'short_code': self.short_code})
    
    def increment_clicks(self):
        """Increment click count atomically"""
        self.clicks = models.F('clicks') + 1
        self.save(update_fields=['clicks'])
        self.refresh_from_db()


