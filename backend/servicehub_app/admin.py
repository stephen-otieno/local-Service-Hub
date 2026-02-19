from django.contrib import admin
from .models import UserProfile, Booking

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_type', 'is_provider', 'is_verified')
    list_filter = ('is_provider', 'is_verified', 'service_type')
    search_fields = ('user__username', 'service_type')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'provider', 'total_fee', 'status', 'created_at')
    readonly_fields = ('provider_payout', 'platform_commission') # Prevent manual editing of split