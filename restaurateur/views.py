from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

import json

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order, OrderItem
from django.db.models import Case, When, Value, IntegerField
from foodcartapp.utils.geocoder import get_coordinates
from django.db.models import Prefetch
from collections import defaultdict


class Login(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=75,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Укажите имя пользователя"}
        ),
    )
    password = forms.CharField(
        label="Пароль",
        max_length=75,
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={"form": form})

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(
            request,
            "login.html",
            context={
                "form": form,
                "ivalid": True,
            },
        )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("restaurateur:login")


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_products(request):
    restaurants = list(Restaurant.objects.order_by("name"))
    products = list(Product.objects.prefetch_related("menu_items"))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False) for restaurant in restaurants
        ]

        products_with_restaurant_availability.append((product, ordered_availability))

    return render(
        request,
        template_name="products_list.html",
        context={
            "products_with_restaurant_availability": products_with_restaurant_availability,
            "restaurants": restaurants,
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_restaurants(request):
    return render(
        request,
        template_name="restaurants_list.html",
        context={
            "restaurants": Restaurant.objects.all(),
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_orders(request):
    orders = (
        Order.objects.all()
        .with_total_price()
        .exclude(status="completed")
        .prefetch_related(
            Prefetch("items", queryset=OrderItem.objects.select_related("product")),
            "restaurant",
        )
        .annotate(
            status_order=Case(
                When(status="pending", then=Value(1)),
                When(status="assembly", then=Value(2)),
                When(status="delivery", then=Value(3)),
                default=Value(99),
                output_field=IntegerField(),
            )
        )
        .order_by("status_order", "-created_at")
    )

    addresses_to_geocode = set()

    for order in orders:
        addresses_to_geocode.add(order.address)

    restaurant_addresses = Restaurant.objects.values_list(
        "address", flat=True
    ).distinct()
    addresses_to_geocode.update(restaurant_addresses)

    coordinates_cache = {}
    for address in addresses_to_geocode:
        coordinates_cache[address] = get_coordinates(address)

    orders_data = []

    for order in orders:
        order_coords = coordinates_cache.get(order.address)

        available_restaurants = order.get_available_restaurants()
        restaurants_with_distances = []

        for restaurant in available_restaurants:
            restaurant_coords = coordinates_cache.get(restaurant.address)
            distance = None

            if order_coords and restaurant_coords:
                from foodcartapp.utils.geocoder import calculate_distance

                distance = calculate_distance(order_coords, restaurant_coords)

            restaurants_with_distances.append(
                {
                    "restaurant": restaurant,
                    "distance": distance,
                    "has_distance": distance is not None,
                }
            )

        restaurants_with_distances.sort(
            key=lambda x: (
                x["distance"] is None,
                x["distance"] if x["distance"] is not None else float("inf"),
            )
        )

        orders_data.append(
            {
                "order": order,
                "available_restaurants": restaurants_with_distances,
                "total_price": order.total_price,
                "order_has_coords": order_coords is not None,
            }
        )

    return render(
        request,
        template_name="order_items.html",
        context={
            "order_items": orders_data,
        },
    )
