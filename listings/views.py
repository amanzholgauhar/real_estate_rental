import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .forms import BookingForm, PropertyForm, ReviewForm
from .models import Booking, Property, Review
from .serializers import PropertySerializer

logger = logging.getLogger(__name__)


class TestView(APIView):
    def get(self, request):
        return JsonResponse({"message": "It works!"})


class PropertyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Property.objects.select_related("user").prefetch_related("booking_set").all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "location"]
    ordering_fields = ["price", "location"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PropertyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Property.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this property.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this property.")
        instance.delete()


@login_required
def add_property_view(request):
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.user = request.user
            prop.save()
            return redirect("property_list")
    else:
        form = PropertyForm()
    return render(request, "listings/add_property.html", {"form": form})


@login_required
def edit_property_view(request, pk):
    prop = get_object_or_404(Property, pk=pk, user=request.user)
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=prop)
        if form.is_valid():
            form.save()
            return redirect("property_list")
    else:
        form = PropertyForm(instance=prop)
    return render(request, "listings/edit_property.html", {"form": form, "property": prop})


@login_required
def delete_property_view(request, pk):
    prop = get_object_or_404(Property, pk=pk, user=request.user)
    if request.method == "POST":
        prop.delete()
        return redirect("property_list")
    return render(request, "listings/delete_property_confirm.html", {"property": prop})


def property_list_view(request):

    qs = Property.objects.all()
    search = request.GET.get("search", "")
    location = request.GET.get("location", "")
    price = request.GET.get("price", "")

    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(location__icontains=search)
        )
    if location:
        qs = qs.filter(location__icontains=location)
    if price:
        try:
            max_price = float(price)
            qs = qs.filter(price__lte=max_price)
        except ValueError:
            pass

    properties = qs.annotate(avg_rating=Avg("reviews__rating"))

    return render(request, "listings/property_list.html", {
        "properties": properties,
    })


def property_detail_view(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    avg_rating = prop.reviews.aggregate(avg=Avg("rating"))["avg"]
    user_review = None
    if request.user.is_authenticated:
        user_review = prop.reviews.filter(user=request.user).first()

    return render(request, "listings/property_detail.html", {
        "property":    prop,
        "avg_rating":  avg_rating,
        "user_review": user_review,
    })


@login_required
def create_booking(request):
    initial = {}
    if request.GET.get("property_id"):
        initial["property"] = request.GET["property_id"]

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()

            send_mail(
                subject="Booking Confirmed",
                message=(
                    f"Your booking for '{booking.property.title}' "
                    "has been successfully created."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
            )
            return redirect("my_bookings")
    else:
        form = BookingForm(initial=initial)

    return render(request, "listings/create_booking.html", {"form": form})


@login_required
def quick_booking(request):
    prop_id = request.GET.get("property_id")
    if not prop_id:
        return redirect("property_list")
    prop = get_object_or_404(Property, pk=prop_id)
    Booking.objects.create(user=request.user, property=prop, status="pending")

    send_mail(
        subject="Booking Confirmed",
        message=(
            f"Your booking for '{prop.title}' "
            "has been successfully created."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
    )
    return redirect("my_bookings")


@login_required
def my_bookings_view(request):
    bookings = (
        Booking.objects
        .filter(user=request.user)
        .exclude(status="cancelled")
        .select_related("property")
    )
    return render(request, "listings/my_bookings.html", {"bookings": bookings})


@login_required
def edit_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect("my_bookings")
    else:
        form = BookingForm(instance=booking)
    return render(request, "listings/edit_booking.html", {"form": form})


@login_required
def create_review(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if Review.objects.filter(user=request.user, property=prop).exists():
        existing = prop.reviews.get(user=request.user)
        return redirect("edit_review", pk=existing.pk)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.user = request.user
            rev.property = prop
            rev.save()
            messages.success(request, "Review submitted.")
            return redirect("property_detail", pk=pk)
    else:
        form = ReviewForm()

    return render(request, "listings/review_form.html", {
        "form":     form,
        "property": prop,
    })


@login_required
def edit_review(request, pk):
    rev = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=rev)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated.")
            return redirect("property_detail", pk=rev.property.pk)
    else:
        form = ReviewForm(instance=rev)

    return render(request, "listings/review_form.html", {
        "form":     form,
        "property": rev.property,
    })
