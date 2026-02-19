from django.db import models
from django.contrib.auth.models import User
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_provider = models.BooleanField(default=False)
    # Geolocation for 3km radius matching [cite: 22, 36]
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    service_type = models.CharField(max_length=100, blank=True)  # e.g., Plumbing, Painting [cite: 10]
    is_verified = models.BooleanField(default=False)  # For digital trust [cite: 14]


class Booking(models.Model):
    client = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    provider = models.ForeignKey(User, related_name='jobs', on_delete=models.CASCADE)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    provider_payout = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(max_length=20, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.provider_payout = self.total_fee * 0.90
        self.platform_commission = self.total_fee * 0.10
        super().save(*args, **kwargs)