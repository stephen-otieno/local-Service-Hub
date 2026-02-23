from django.contrib import admin
from .models import UserProfile, Booking,Provider, Client, ClientFeedback, ProviderFeedback
from django.utils import timezone

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_type', 'is_provider', 'is_verified')
    list_filter = ('is_provider', 'is_verified', 'service_type')
    search_fields = ('user__username', 'service_type')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('provider', 'total_amount', 'provider_cut', 'status', 'is_paid_to_provider')
    list_filter = ('status', 'is_paid_to_provider')
    actions = ['mark_as_paid']

    @admin.action(description='Mark selected bookings as Paid to Provider')
    def mark_as_paid(self, request, queryset):
        # Ensure we only pay out completed jobs
        completed_jobs = queryset.filter(status='completed')
        count = completed_jobs.update(is_paid_to_provider=True, payout_date=timezone.now())
        self.message_user(request, f"Successfully marked {count} jobs as paid.")

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    # Only show users marked as providers
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_provider=True)

    list_display = ('user', 'service_type', 'is_verified', 'phone_number', 'latitude', 'longitude')
    list_filter = ('is_verified', 'service_type')
    search_fields = ('user__username', 'service_type')
    
    # Action for manual verification per your project methodology
    actions = ['make_verified']

    @admin.action(description='Verify selected providers')
    def make_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, "Providers verified for 3km radius matching.")

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    # Only show users NOT marked as providers
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_provider=False)

    list_display = ('user', 'phone_number')
    search_fields = ('user__username',)


@admin.register(ClientFeedback)
class ClientFeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('subject', 'message', 'user__username')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_type='client')


@admin.register(ProviderFeedback)
class ProviderFeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('subject', 'message', 'user__username')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_type='provider')