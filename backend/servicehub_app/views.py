from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from math import radians, cos, sin, asin, sqrt
from django.shortcuts import get_object_or_404, redirect
from .models import Booking, UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages


# Haversine formula to calculate distance in km
def calculate_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Earth radius
    return c * r


# 1. View to render the HTML home page
def home(request):
    return render(request, 'servicehub_app/index.html')


# 2. API View to return nearby providers as JSON
def find_nearby_providers(request):
    client_lat = request.GET.get('lat')
    client_lon = request.GET.get('lon')

    if not client_lat or not client_lon:
        return JsonResponse({'error': 'Coordinates required'}, status=400)

    providers = UserProfile.objects.filter(is_provider=True, is_verified=True)
    nearby_list = []

    for p in providers:
        if p.latitude and p.longitude:
            dist = calculate_distance(client_lat, client_lon, p.latitude, p.longitude)
            if dist <= 3.0:  # 3km radius constraint
                nearby_list.append({
                    'name': p.user.username,
                    'service': p.service_type,
                    'distance_km': round(dist, 2)
                })

    return JsonResponse({'providers': nearby_list})


# 3. View to render the Registration page
def register_view(request):
    return render(request, 'servicehub_app/register.html')


def book_service(request, provider_id):
    if request.method == 'POST':
        provider_profile = get_object_or_404(UserProfile, id=provider_id)

        # Create the booking
        # For now, we use a fixed fee (e.g., 1000 KES) for testing
        Booking.objects.create(
            client=request.user,
            provider=provider_profile.user,
            total_fee=1000
        )
        return JsonResponse({'status': 'success', 'message': 'Booking request sent!'})


@login_required
def create_booking(request, provider_id):
    if request.method == 'POST':
        provider_profile = get_object_or_404(UserProfile, id=provider_id)

        # Create the booking with a test amount (e.g., 1500 KES)
        new_booking = Booking.objects.create(
            client=request.user,
            provider=provider_profile.user,
            total_fee=1500
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Booking created! Hub Commission: {new_booking.platform_commission}'
        })

@login_required
def get_my_bookings(request):
    # Fetch bookings where the current user is the client
    bookings = Booking.objects.filter(client=request.user).order_by('-created_at')
    data = [{
        'provider': b.provider.username,
        'total_fee': b.total_fee,
        'status': b.status,
        'date': b.created_at.strftime("%Y-%m-%d")
    } for b in bookings]
    return JsonResponse(data, safe=False)


@login_required
def provider_dashboard(request):
    # Ensure only providers can access this page
    profile = get_object_or_404(UserProfile, user=request.user)
    if not profile.is_provider:
        return redirect('home')

    # Fetch jobs assigned to this provider
    jobs = Booking.objects.filter(provider=request.user).order_by('-created_at')

    # Calculate total earnings (the 90% share)
    total_earnings = jobs.filter(status='completed').aggregate(Sum('provider_payout'))['provider_payout__sum'] or 0

    context = {
        'jobs': jobs,
        'total_earnings': total_earnings,
        'profile': profile
    }
    return render(request, 'servicehub_app/provider_dashboard.html', context)


def apply_provider(request):
    if request.method == 'POST':
        # Manually extracting data from the custom HTML form
        data = request.POST
        try:
            # 1. Create the User (Account Details)
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )

            # 2. Create the Profile (Professional Details)
            UserProfile.objects.create(
                user=user,
                is_provider=True,
                service_type=data['service_type'],
                phone_number=data['phone_number'],
                bio=data['bio'],
                latitude=data['lat'],
                longitude=data['lon'],
                is_verified=False  # Requires admin oversight per methodology
            )

            messages.success(request, "Application submitted! Please wait for verification.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'servicehub_app/apply_provider.html')